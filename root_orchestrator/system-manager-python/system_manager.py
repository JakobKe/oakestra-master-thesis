import json
import os
import socket
import threading
from concurrent import futures
from datetime import timedelta
from pathlib import Path
from secrets import token_hex

import grpc
from blueprints import blueprints
from bson import json_util
from ext_requests.cluster_db import mongo_upsert_cluster
from ext_requests.mongodb_client import mongo_init
from ext_requests.net_plugin_requests import net_register_cluster
from ext_requests.user_db import create_admin
from flask import Flask, flash, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_smorest import Api
from flask_socketio import SocketIO, emit
from flask_swagger_ui import get_swaggerui_blueprint
from google.protobuf.json_format import MessageToDict
from proto.clusterRegistration_pb2 import SC1Message, SC2Message
from proto.clusterRegistration_pb2_grpc import (
    add_register_clusterServicer_to_server,
    register_clusterServicer,
)
from sm_logging import configure_logging
from utils.network import sanitize
from werkzeug.utils import redirect, secure_filename

my_logger = configure_logging()

UPLOAD_FOLDER = "files"
ALLOWED_EXTENSIONS = {"txt", "json", "yml"}

app = Flask(__name__)

app.config["OPENAPI_VERSION"] = "3.0.2"
app.config["API_TITLE"] = "Oakestra root api"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_URL_PREFIX"] = "/docs"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["JWT_SECRET_KEY"] = token_hex(32)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=10)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=7)
app.config["RESET_TOKEN_EXPIRES"] = timedelta(hours=3)  # for password reset

jwt = JWTManager(app)
api = Api(app, spec_kwargs={"host": "oakestra.io", "x-internal-id": "1"})

cors = CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(
    app,
    async_mode="eventlet",
    logger=True,
    engineio_logger=True,
    cors_allowed_origins="*",
)
mongo_init(app)
create_admin()

MY_PORT = os.environ.get("MY_PORT") or 10000
MY_PORT_GRPC = os.environ.get("MY_PORT_GRPC") or 50052

cluster_gauges_for_prometheus = []

# Register apis
for bp in blueprints:
    api.register_blueprint(bp)

api.spec.components.security_scheme(
    "bearerAuth", {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
)
api.spec.options["security"] = [{"bearerAuth": []}]

# Swagger docs
SWAGGER_URL = "/api/docs"
API_URL = "/docs/openapi.json"
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={"app_name": "Oakestra root orchestrator"},
)
app.register_blueprint(swaggerui_blueprint)


# .......... Register clusters via WebSocket ...........#
# ......................................................#


@socketio.on("connect", namespace="/register")
def on_connect():
    app.logger.info("SocketIO - Cluster_Manager connected: {}".format(request.remote_addr))
    app.logger.info(request.environ.get("REMOTE_PORT"))
    # time.sleep(1)  # Wait here to Avoid Race Condition with Client (Cluster Manager) does no work.
    # Apparently, nothing in between is sent by Websocket protocol
    emit(
        "sc1",
        {"Hello-Cluster_Manager": "please send your cluster info"},
        namespace="/register",
    )


@socketio.on("cs1", namespace="/register")
def handle_init_client(message):
    app.logger.info(
        "SocketIO - Received Cluster_Manager_to_System_Manager_1: {}:{}".format(
            request.remote_addr, request.environ.get("REMOTE_PORT")
        )
    )
    app.logger.info(message)

    cluster_address = sanitize(request.remote_addr)

    cid = mongo_upsert_cluster(cluster_ip=cluster_address, message=message)
    x = {"id": str(cid)}

    net_register_cluster(
        cluster_id=str(cid),
        cluster_address=cluster_address,
        cluster_port=message["network_component_port"],
    )

    emit("sc2", json.dumps(x), namespace="/register")


@socketio.event(namespace="/register")
def disconnect():
    app.logger.info("SocketIO - Client disconnected")


# ............... Finish WebSocket handling ............#
# ......................................................#


# .............. Register clusters via GRPC ............#
# ......................................................#


class ClusterRegistrationServicer(register_clusterServicer):
    def handle_init_greeting(self, request, context):
        app.logger.info("gRPC - Cluster_Manager connected: {}".format(context.peer()))
        return SC1Message(hello_cluster_manager="please send your cluster info")

    def handle_init_final(self, request, context):
        app.logger.info(
            "gRPC - Received Cluster_Manager_to_System_Manager_1: {}".format(context.peer())
        )
        app.logger.info(request)
        message = MessageToDict(request, preserving_proto_field_name=True)
        cluster_ip = context.peer().split(":")[1]

        cid = mongo_upsert_cluster(cluster_ip=cluster_ip, message=message)

        net_register_cluster(
            cluster_id=str(cid),
            cluster_address=cluster_ip,
            cluster_port=request.network_component_port,
        )

        return SC2Message(id=str(cid))


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # server = grpc.server()  # single threaded
    add_register_clusterServicer_to_server(ClusterRegistrationServicer(), server)
    server.add_insecure_port("0.0.0.0:" + str(MY_PORT_GRPC))
    server.start()
    server.wait_for_termination()


# ................. Finish GRPC handling ...............#
# ......................................................#


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# Used to upload file from the frontend
@app.route("/frontend/uploader", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files["file"]
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)
        if not allowed_file(file.filename):
            return "Not a valid file", 400
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            response = {"path": str(Path(filename).absolute())}
            return str(json_util.dumps(response))
    return """
    <!doctype html>
    <h1>Not a valid request</h1>
    """


def start_flask_server():
     eventlet.wsgi.server(
        eventlet.listen(("::", int(MY_PORT)), family=socket.AF_INET6), app, log=my_logger
    )

def start_grpc_server():
    my_logger.info("Start gRPC Server")
    serve()


if __name__ == "__main__":
    import eventlet
    flask_thread = threading.Thread(target=start_flask_server)
    grpc_thread = threading.Thread(target=start_grpc_server)

    flask_thread.start()
    grpc_thread.start()

    flask_thread.join()
    grpc_thread.join()
