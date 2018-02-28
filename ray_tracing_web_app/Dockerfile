FROM ubuntu:14.04

# Copyright (c) 2018, Intel Research and Development Ireland Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


RUN apt-get update --fix-missing

RUN apt-get install -y git wget build-essential openssl libssl-dev pkg-config python python-dev python-pip ruby rake ruby-dev mongodb libkrb5-dev ImageMagick mencoder curl

RUN curl -sL https://deb.nodesource.com/setup_4.x | sudo bash -

RUN apt-get install -y nodejs

RUN mkdir /data && mkdir /data/db

RUN pip install pip --upgrade
RUN pip install pika pyyaml requests mock pbr ez_setup jpype1 pymongo paramiko scp pillow

RUN gem install bson_ext -v 1.9.2
RUN gem install genghisapp

RUN npm install -g npm

RUN pip install jsonpickle

RUN git clone https://github.com/webpy/webpy.git /root/webpy
WORKDIR /root/webpy
RUN rm /root/webpy/web/wsgi.py

#now clone project from bitbucket to  /webapp foler
RUN mkdir -p /webapp

RUN rm -rf /webapp/*

RUN wget -O rtwebproject.zip https://codeload.github.com/IntelLabsEurope/raytracing-demonstration-application/zip/master
RUN unzip rtwebproject.zip -d  /webapp

RUN mv /webapp/raytracing-demonstration-application-master/ray_tracing_web_app/wsgi.py /root/webpy/web/
 
RUN pip install .

RUN apt-get install -y supervisor

RUN mv /webapp/cloudlightning-t2.2_raytracing_integrated_usecase-54fa0f6fc6e6/ray_tracing_web_app/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

RUN mv /webapp/cloudlightning-t2.2_raytracing_integrated_usecase-54fa0f6fc6e6/ray_tracing_web_app/ /src/

RUN ln -s /usr/bin/npm /usr/local/bin/npm

RUN rm -rf rtwebproject.zip

WORKDIR /src/src

RUN npm install .

ENTRYPOINT ["/usr/bin/supervisord", "-c","/etc/supervisor/conf.d/supervisord.conf"]

