# Copyright (c) 2017, Intel Research and Development Ireland Ltd.
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

curl -X POST $1/v2/apps?force=true -H Content-type: application/json -d '{
  "id": "'$2'",
  "cpus": 0.1,
  "mem": 512,
  "cmd": "service mongodb restart & /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf & vi",
  "container": {
    "type": "DOCKER",
    "docker": {
      "image": "'$3'",
      "forcePullImage": false,
      "network": "BRIDGE",
      "portMappings": [
        { "containerPort": 9393, "hostPort": 0, "servicePort": '$4', "protocol": "tcp" },
        { "containerPort": 3005, "hostPort": 0, "servicePort": '$5', "protocol": "tcp"}
      ],
      "parameters": [
        {
          "key": "hostname",
          "value": "raytracing_webservice.weave.local"
        }
      ]
     }
  },
  "labels": {
    "name": "ray_tracing_webservice_instance"
  }
}'
