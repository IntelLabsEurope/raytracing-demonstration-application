/* 
 Copyright (c) 2017, Intel Research and Development Ireland Ltd.

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
 */

//var deploy = 'cl_production';
var deploy = 'dev_env';

var config = {};
config.endpoints = {};

if (deploy == 'cl_production'){
}
else if (deploy == 'dev_env'){
	config.debug = false;
	config.connection_string = '127.0.0.1:27017/local';
	config.upload_dir = '/tmp';

	config.embree_user = 'root';
	//use one or other of these, leave unused one as empty string
	config.embree_pass = 'secret';
	config.key_filename = ''

	config.model_suffix = '.obj';
	config.webservice_port = '9393'
}

module.exports = config;

