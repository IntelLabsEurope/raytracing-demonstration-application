# Copyright (c) 2017, Intel Research and Development Ireland Ltd.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#    http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

FROM centos:7

RUN echo 'root:secret' | chpasswd
RUN yum install -y openssh-server || true
RUN yum install -y openssh-clients
RUN yum install -y unzip
RUN yum install -y gimp
RUN yum install -y zip

RUN  yum install -y mesa* freeglut.x86_64 \
	            freeglut-devel.x86_64  \
                    libXmu.x86_64 libXi.x86_64 \
                    libXmu-devel.x86_64 \
                    tbb.x86_64 \
                    wget \
                    pciutils \
                    libXi-devel.x86_64 || true

RUN yum install -y xorg-x11-xauth \
		   xorg-x11-fonts-* \
		   xorg-x11-utils

RUN mkdir /embree
WORKDIR /embree
RUN wget https://github.com/embree/embree/releases/download/v2.8.0/embree-2.8.0.x86_64.rpm.tar.gz
RUN tar xzf embree-2.8.0.x86_64.rpm.tar.gz
RUN rpm --install embree-lib-2.8.0-1.x86_64.rpm
RUN rpm --install embree-devel-2.8.0-1.x86_64.rpm
RUN rpm --install embree-examples-2.8.0-1.x86_64.rpm
RUN wget http://registrationcenter-download.intel.com/akdlm/irc_nas/9669/mpss-3.7.2-linux.tar
RUN tar xvf mpss-3.7.2-linux.tar
RUN cp mpss-3.7.2/*.rpm /embree/
RUN rpm --install libscif*.rpm
RUN rpm --install mpss-coi-*.rpm
RUN rm embree-2.8.0.x86_64.rpm.tar.gz
RUN rm *.rpm
RUN wget https://github.com/embree/embree/releases/download/v2.8.0/embree-2.8.0.x86_64.linux.tar.gz
RUN tar zxf embree-2.8.0.x86_64.linux.tar.gz
RUN rm embree-2.8.0.x86_64.linux.tar.gz

RUN mkdir -p /var/run/sshd ; chmod -rx /var/run/sshd
RUN ssh-keygen -t rsa -f /etc/ssh/ssh_host_rsa_key
RUN sed -ri 's/#PermitRootLogin yes/PermitRootLogin yes/g' /etc/ssh/sshd_config
RUN sed -ri 's/UsePAM yes/#UsePAM yes/g' /etc/ssh/sshd_config
RUN sed -ri 's/#UsePAM no/UsePAM no/g' /etc/ssh/sshd_config

RUN export SINK_LD_LIBRARY_PATH=/usr/local:${SINK_LD_LIBRARY_PATH}

RUN echo X11Forwarding yes >> /etc/ssh/sshd_config
RUN echo X11DisplayOffset 10 >> /etc/ssh/sshd_config
RUN echo X11UseLocalhost no >> /etc/ssh/sshd_config

RUN mkdir /scripts
ADD exec_batch_file.sh /scripts
ADD generate_preview.sh /scripts

RUN echo "source /embree/embree-2.8.0.x86_64.linux/embree-vars.sh" >> /root/.bashrc

EXPOSE 22
CMD    ["/usr/sbin/sshd", "-D"]
