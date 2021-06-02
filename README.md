# EdgeIO Infrastructure Getting Started

## Root Orchestrator setup

On a Linux machine with public IP address or DNS name, first install Docker and Docker-compose. Then, run the following commands to set up the Root Orchestrator components. Open the following ports:

- Port 80 - Grafana Dashboard
- Port 10000 - System Manager


```bash
cd root_orchestrator/
docker-compose up -d
```

## Cluster Orchestrator(s) setup

On a second Linux machine with public IP address or DNS name, first install Docker and Docker-compose. Then, run the following commands to set up the Root Orchestrator components. Open port 10000 for the cluster manager.

Set a cluster_name, cluster_location, and the system_manager port in the docker-compose.yml.


```bash
cd cluster_orchestrator/
docker-compose up -d
```

## Add worker nodes (run Node Engine)

On an arbitrary Linux machine, install Python3.8 and virtualenv. Set the IP address of the cluster orchestrator which should take care of the worker node in the start-up.sh file, and run the following:

```bash
cd node_engine/
./start-up.sh
```

# Application Deployment

## Deployment descriptor

In order to deploy a container a deployment descriptor must be ppassed to the deployment command. 
The deployment descriptor contains all the information that EdgeIO needs in order to achieve a complete
deploy in the system. 

`deployment_descriptor_model.yaml`
```yaml
api_version: v0.1 
app_name: demo   
app_ns: default
service_name: service1
service_ns: test
image: docker.io/library/nginx:alpine
image_runtime: docker
port: 80
cluster_location: hpi
node: vm-20211019-009
requirements:
    cpu: 0 # cores
    memory: 100  # in MB
    node: vm-20211019-009
```

- api_version: by default you can leave v0.1
- Give your application a fully qualified name: A fully qualified name in EdgeIO is composed of 4 components
    - app_name: name of the application
    - app_ns: namespace of the app, used to reference different deployment of the same applciation. Examples of namespace name can be `default` or `production` or `test`
    - service_name: name of the service that is going to be deployed
    - service_ns: same as app ns, this can be used to reference different deployment of the same service. Like `v1` or `test`
- image: link to the docker image that will be downloaded 
- image_runtime: right now the only stable runtime is `docker`
- port: port exposed by your service, if any, otherwise leave it blank.
- cluster_location: if you have any preference on a specific cluster write here the name otherwise remove this field.
- node: if you have any prefrence on a specific node within a cluster write here the hostname otw remove this field
- requirements: does your container have any min cpu or memory requirement?
    - cpu: expressed in number of cores
    - memory: expressed in MB
    - node: same value expressed in the node field out of the requirements section. Right now this is a duplicate. And must be included if you specified a node requirement before. Please refer to: [Github Issue #24](https://github.com/edgeIO/src/issues/24)
    
    
## Deploy

After creating a deployment descriptor file, simply deploy a service using 

```
curl -F file=@'deploy.yaml' http://localhost:10000/api/deploy -v
```

deploy.taml is the deployment descriptor file

If the call is successful you'll receive the job name for this service. Save this name for future call.

## Undeploy 

```
curl localhost:10000/api/delete/<job_name>
```

job_name is the name you receive as answer after a deployment 

## Query job status 

```
curl localhost:10000/api/job/status/<job_id>
```

## List of the current deployed Jobs

```
curl localhost:10000/api/jobs
```

Use this endpoint to get information regarding the deployed services in the system. Like the network address assigned to a service.

# Networking 

After a successful deployment in EdgeIO a service is going to have 2 internal IP addresses that can be used for container to container communication. 
The addresses currently can be retrieved with the ```job/list``` command. Each service is going to have an Instance address and a RR address. 

- Instance address is bounded to the specific instance of a service. THis address will always refer to that instance.
- The RR address instead can be used to balance across all the instaces of the same service, "one address to rule them all".

The addresses right now are assigned at deploy time randomly. 
