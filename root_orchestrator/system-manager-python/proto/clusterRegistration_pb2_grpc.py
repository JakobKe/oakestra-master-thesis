# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import proto.clusterRegistration_pb2 as clusterRegistration__pb2


class register_clusterStub(object):
    """Init Registration 
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.handle_init_greeting = channel.unary_unary(
                '/clusterRegistration.register_cluster/handle_init_greeting',
                request_serializer=clusterRegistration__pb2.CS1Message.SerializeToString,
                response_deserializer=clusterRegistration__pb2.SC1Message.FromString,
                )
        self.handle_init_final = channel.unary_unary(
                '/clusterRegistration.register_cluster/handle_init_final',
                request_serializer=clusterRegistration__pb2.CS2Message.SerializeToString,
                response_deserializer=clusterRegistration__pb2.SC2Message.FromString,
                )


class register_clusterServicer(object):
    """Init Registration 
    """

    def handle_init_greeting(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def handle_init_final(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_register_clusterServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'handle_init_greeting': grpc.unary_unary_rpc_method_handler(
                    servicer.handle_init_greeting,
                    request_deserializer=clusterRegistration__pb2.CS1Message.FromString,
                    response_serializer=clusterRegistration__pb2.SC1Message.SerializeToString,
            ),
            'handle_init_final': grpc.unary_unary_rpc_method_handler(
                    servicer.handle_init_final,
                    request_deserializer=clusterRegistration__pb2.CS2Message.FromString,
                    response_serializer=clusterRegistration__pb2.SC2Message.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'clusterRegistration.register_cluster', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class register_cluster(object):
    """Init Registration 
    """

    @staticmethod
    def handle_init_greeting(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/clusterRegistration.register_cluster/handle_init_greeting',
            clusterRegistration__pb2.CS1Message.SerializeToString,
            clusterRegistration__pb2.SC1Message.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def handle_init_final(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/clusterRegistration.register_cluster/handle_init_final',
            clusterRegistration__pb2.CS2Message.SerializeToString,
            clusterRegistration__pb2.SC2Message.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
