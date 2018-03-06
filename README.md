# Ray Tracing Demonstrator Application

1. [Introduction](#introduction)
2. [Installation](#installation)
	* [Retrieve the code](#retrieve-the-code)
	* [Building docker containers](#building-docker-containers)
3. [Environment](#environment)
   	* [CPU Deployment ](#cpu-deployment)
   	* [MIC Co-processor Deployment](#mic-co-processor-deployment)   	
4. [Deploying the Application without Mesos](#deploying-the-application-without-mesos)
	* [Start Ray Tracing Engine Container](#start-ray-tracing-engine-container)
	* [Start Ray Tracing WebService Container](#start-ray-tracing-webService-container)
	* [Linking the Containers](#linking-the-containers)
	* [Running the demo](#running-the-demo)
	* [Deploying the Application with Mesos](#deploying-the-application-with-mesos)
5. [About Ray Tracing Demonstrator Application](#about-ray-tracing-demonstrator-application)
6. [Acknowledgements](#acknowledgements)

## Introduction

Ray Tracing Demonstration Application is a Python implementation of web-based Ray Traced 3D image rendering application deployed using Docker containers. This demo application is designed to discover and utilize the Intel Xeon CPUs or Xeon Phi coprocessors exposed by Infrastructure manager i.e. Apache Mesos and execute Intel’s Embree Ray Tracing Kernels in order to render 3D images of Ray Tracing models uploaded by users. 

Application users can perform both batch and interactive rendering by submitting the jobs through web UI and download the fully rendered images or visualize the real-time rendered images through SSH X11 display forwarding onto their local workstation screen.

This demo application has been implemented and packaged into two docker containers to manage the dependencies and provide lightweight portability for cloud deployment. 

## Installation

### Retrieve the code

	# Clone the repository 
	git clone https://github.com/IntelLabsEurope/raytracing-demonstration-application.git
	# Change directory to the landscaper root.
	cd raytracing-demonstration-application
	
### Building docker containers

    # Build ray tracing engine backend container
	cd raytracing_engine
	docker build -t rtdemo/raytracing_engine:1
	# Build ray tracing webservice container for webGUI
	cd ray_tracing_web_app
	docker build -t rtdemo/raytracing_webserver:1	
    
## Environment

### CPU Deployment
Supports Linux OS i.e. Ubuntu 16.04 or CentOS 7.0 follow OS installation guide:
	Ubuntu: https://help.ubuntu.com/lts/installation-guide/index.html
	CentOS: https://wiki.centos.org/

Install Docker version 1.10.x or above, follow the installation guide:
	Ubuntu: https://docs.docker.com/install/linux/docker-ce/ubuntu/
	Centos: https://docs.docker.com/install/linux/docker-ce/centos/

For interactive real time rendering client system need X11 display capability with SSH tunneling.
 
### MIC Co-processor Deployment:
For Mesos/Marathon deployment follow the guide to setup mesos cluster from : https://mesosphere.github.io/marathon/docs/

To execute ray tracing demo using Xeon Phi (MIC co-processor) follow the hardware installation and configuration guide. 

Container rtdemo/raytracing_engine:1 includes required libraries to run the application assuming MIC co-processors are fully operation in the host machine. 

## Deploying the Application without Mesos

### Start Ray Tracing Engine Container

	docker run --name rtengine -p 2222:22 rtdemo/raytracing_engine:1

### Start Ray Tracing WebService Container

	docker run --name webserver -p 3005:3005 -p 9393:9393  rtdemo/raytracing_webserver:1
	
### Linking the containers

	curl -i -H "Content-Type: application/json" -X POST -d '{"url":"<host-ip:2222>"}' http://host-ip:9393/

### Running the demo

	Open the webGUI using URL <container_url>:3005 and follow the instruction. 

## Deploying the Application with Mesos 

	cd deploy_scripts
	./deploy_ray_tracing_application.sh	

## About Ray Tracing Demonstrator Application

The Ray Tracing Demonstrator Application was developed by Intel Labs Europe and is published under the Apache License, Version 2.0.

Contributions from the community are welcome via Pull Requests.

## Acknowledgments 
This is Open Source software released under the Apache 2.0 License. Please see the LICENSE file for full license details.
This software has been contributed by CloudLightning, a Horizon 2020 project co-funded by the European Union. https://www.cloudlightning.eu/