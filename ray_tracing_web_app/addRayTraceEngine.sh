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

while :
do
	x=$(curl -o /dev/null --silent --head --write-out '%{http_code}\n' localhost:9393/checkphi)
	if [ $x -eq 200 ]
	then
		echo "localhost:9393 is ready. POST-ing raytracing engine url..."
	    result=$(curl --silent -i -H "Content-Type: application/json" -X POST -d '{"url":"'$RT_ENGINE:$RT_ENGINE_PORT'"}' localhost:9393)
	    echo $result
	    break
	else
		echo "localhost:9393 status: $x"
		echo "localhost:9393 is unavailable. Sleeping 20 seconds..."
	    sleep 10
	fi
done