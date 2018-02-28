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

clear

MARATHON_URL="http://host-ip:port"

ENGINE_NAME="cloudlightning/rtengine0001"
ENGINE_IMAGE="rtdemo/raytracing_engine:1"
ENGINE_PORT="7330"

GUI_NAME="cloudlightning/rtwebservice0001"
GUI_IMAGE="rtdemo/raytracing_webserver:1"
GUI_PORT_PY=7333
GUI_PORT_WEB=7334

# Delete
curl -i -H "Accept: application/json" -H "Content-Type: application/json" -X DELETE $MARATHON_URL/v2/apps/$ENGINE_NAME
curl -i -H "Accept: application/json" -H "Content-Type: application/json" -X DELETE $MARATHON_URL/v2/apps/$GUI_NAME

clear
echo "deleting existing deployments, please wait..."

sleep 10s

#clear
echo "Deploying Ray Tracing WebService..."

./ray_tracing_webservice_master.sh $MARATHON_URL $GUI_NAME $GUI_IMAGE $GUI_PORT_PY $GUI_PORT_WEB

echo "Deploying Ray Tracing Engine..."
./ray_tracing_engine.sh $MARATHON_URL $ENGINE_NAME $ENGINE_IMAGE $ENGINE_PORT

sleep 25s

ipRTEngine=$(curl --silent -H "Content-Type: application/json" -X GET $MARATHON_URL/v2/apps/$ENGINE_NAME | ./jq-linux64 -r .app.tasks[0].host)
ipRTPort=$(curl --silent -H "Content-Type: application/json" -X GET $MARATHON_URL/v2/apps/$ENGINE_NAME | ./jq-linux64 .app.tasks[0].ports[0])

ipWebService=$(curl --silent -H "Content-Type: application/json" -X GET $MARATHON_URL/v2/apps/$GUI_NAME | ./jq-linux64 -r .app.tasks[0].host)
APIPort=$(curl --silent -H "Content-Type: application/json" -X GET $MARATHON_URL/v2/apps/$GUI_NAME | ./jq-linux64 .app.tasks[0].ports[0])
WebPort=$(curl --silent -H "Content-Type: application/json" -X GET $MARATHON_URL/v2/apps/$GUI_NAME | ./jq-linux64 .app.tasks[0].ports[1])

echo "----"
echo $ipRTEngine
echo $ipRTPort
echo $ipWebService
echo $APIPort
echo $WebPort
echo '------'

#clear
echo "Webservice IP : " $ipWebService
echo "RT Engine : " $ipRTEngine
echo "Linking RT Engine and RT WebService..."

for i in {40..1..2};do echo -n "." && sleep 2; done

echo $ipWebService:$APIPort
echo $ipRTEngine
curl -i -H "Content-Type: application/json" -X POST -d '{"url":"'$ipRTEngine:$ipRTPort'"}' $ipWebService:$APIPort

echo curl -i -H \"Content-Type: application/json\" -X POST -d \'{"url":"'$ipRTEngine'"}\' $ipWebService:$APIPort

#clear
echo "Deployment of Ray Tracing Application Completed!."
echo ""
echo "RT Engine IP: " $ipRTEngine
echo ""
echo "Ray Tracing Service URL : $ipWebService:$WebPort"


