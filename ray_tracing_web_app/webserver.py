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

import web
import jsonpickle as json
import uuid
import pymongo
import gridfs
import datetime
import os
import zipfile
import subprocess

from paramiko import SSHClient, AutoAddPolicy, RSAKey
from scp import SCPClient
from PIL import Image


urls = (
    '/', 'update_url',
    '/file/send', 'send_file',
    '/file/execute_render', 'execute_render',
    '/jobs/create', 'create_job',
    '/checkphi', 'checkphi',
    '/jobstatus', 'job_status',
    '/download', 'download',
    '/delete', 'delete_job',
    '/preview', 'preview',
    '/generatempeg', 'generatempeg'
)


# TODO: Improve error handling
# TODO: Make exceptions specific

#login = web.input()
#if login.password == web.db_parameters['pw']:
#    web.setcookie('user', web.db_parameters['user'])
#web.redirect('/')

#eg
#curl -i -H "Content-Type: application/json" -X POST -d '{"url":"168.0.3:5050"}' http://127.0.0.1:8080/

app = web.application(urls, globals())

# TODO: Move these out to the config
JOB_FOLDER = '/tmp'
JOB_STATUS_FILE = 'status.txt'
BATCH_FILE_NAME = 'batch.txt'
RENDERER_BINARY = 'pathtracer_xeonphi'
OUTPUT_DIR_NAME = 'output'
PUBLIC_DIR_ROOT = '/src/src/public'
DOWNLOAD_DIR = '{}/{}'.format(PUBLIC_DIR_ROOT, 'downloads')

database_name = 'local'
config_collection = 'config'

ssh = SSHClient()

class update_url:
    def POST(self):
        try:
            data = web.data()
            url = json.loads(data)['url'] if 'url' in json.loads(data) else None
            if url:
                print url
                try:
                    mongo_client = pymongo.MongoClient(
                        'localhost', 27017, serverSelectionTimeoutMS=5000)
                    mongo_db = mongo_client[database_name]
                    mongo_db.drop_collection(config_collection)
                    mongo_collection = mongo_db[config_collection]
                    post_cfg = {
                        "url": url
                    }
                    mongo_collection.insert_one(post_cfg)
                except Exception as e:
                    print e
                    pass

        except Exception as e:
            print str(e)
            pass
        return

class create_job:
    def POST(self):
        try:
            data = json.loads(web.data())
            data['start_time'] = datetime.datetime.utcnow()
            try:
                mongo_client = pymongo.MongoClient(
                    'localhost', 27017, serverSelectionTimeoutMS=5000)
                mongo_db = mongo_client[database_name]
                mongo_collection = mongo_db['jobs']
                mongo_collection.insert_one(data)
            except Exception as e:
                print e
                pass

        except Exception as e:
            print str(e)
            pass
        return


class execute_render:
    def POST(self):
        return

class send_file:
    def POST(self):
        valid_obj_file = None
        batch_file = False
        is_phi = False
        error_message = None
        try:
            data = json.loads(web.data())
            rand_id =  data['job_id']
            container_ip = data['ip']
            username = data['user']
            password = data['pass']
            key_filename = data['key_filename']
            model_suffix = data['model_suffix']
            interactive = data['interactive']

            zip_location = '{}/{}/'.format(JOB_FOLDER, rand_id)
            zip_name = data['filename']
            try:
                ssh.set_missing_host_key_policy(AutoAddPolicy())
                if password:

                    if ':' in container_ip:
                        container_port = int(container_ip.split(':')[1])
                        container_ip = container_ip.split(':')[0]
                    else:
                        container_port = 22
                    ssh.connect(container_ip, port=int(container_port), username=username, password=password)
                else:
                    pk = RSAKey.from_private_key_file(key_filename)
                    ssh.connect(container_ip, username=username, pkey=pk)

                cmd = "mkdir {} {}{}".format(
                    zip_location,
                    zip_location,
                    OUTPUT_DIR_NAME)
                stdin, stdout, stderr = ssh.exec_command(cmd)
                print stdout.read()

                with SCPClient(ssh.get_transport()) as scp:
                    scp.put(data['path'], zip_location + zip_name)

                cmd = "unzip -o " + zip_location + zip_name + " -d " + zip_location
                stdin, stdout, stderr = ssh.exec_command(cmd)
                print stdout.read()
                cmd = "ls " + zip_location
                stdin, stdout, stderr = ssh.exec_command(cmd)
                extracted_files = stdout.read()

                for file in extracted_files.split('\n'):
                    if file == BATCH_FILE_NAME:
                        batch_file = True
                    if file.endswith(model_suffix):
                        valid_obj_file = zip_location + file
                try:
                    cmd = 'test -d /sys/class/mic && echo true'
                    stdin, stdout, stderr = ssh.exec_command(cmd)
                    phiresult = stdout.read()

                    if phiresult and 'true' in phiresult:
                        is_phi = True
                except Exception as e:
                    is_phi = False
                    pass

                # kick off batch job, keep alive in BG with nohup
                if batch_file:
                    transport = ssh.get_transport()
                    async_channel = transport.open_session()
                    cmd = 'nohup /scripts/exec_batch_file.sh {} {} {} {}'.format(
                        zip_location,
                        valid_obj_file,
                        RENDERER_BINARY,
                        BATCH_FILE_NAME)
                    print '\n'
                    print cmd
                    print '\n'
                    async_channel.exec_command(cmd)

            except Exception as e:
                error_message = str(e)

        except Exception as e:
            error_message = str(e)
            pass

        if valid_obj_file:
            if interactive:
                return json.dumps({ "path" : str(valid_obj_file), "phi": str(is_phi), "folder": rand_id })
            else:
                if batch_file:
                    return json.dumps({ "path" : str(valid_obj_file), "phi": str(is_phi), "folder": rand_id })
                else:
                    return json.dumps({ "error" : 'no batch file found in zip' })
        else:
            return json.dumps({ "error" : 'invalid object file', "detail": str(error_message) })


class checkphi:
    def GET(self):
        return True


class job_status:
    def POST(self):
        try:
            data = web.data()
            print data
            job_id = json.loads(data)['id'] if 'id' in json.loads(data) else None
            print job_id
            if job_id:

                conn_data = json.loads(web.data())
                container_ip = conn_data['container_ip']
                username = conn_data['user']
                password = conn_data['pass']

                mongo_client = pymongo.MongoClient(
                    'localhost', 27017, serverSelectionTimeoutMS=5000)
                mongo_db = mongo_client[database_name]
                mongo_collection = mongo_db['jobs']
                r = mongo_collection.find_one({"id": job_id})

                folder = os.path.dirname(r['model_path'])
                status_file = '{}/{}'.format(folder, JOB_STATUS_FILE)

                # TODO: refactor error handling
                # TODO: take these from config
                # TODO: implement a reusable ssh client helper class

                if ':' in container_ip:
                    container_port = int(container_ip.split(':')[1])
                    container_ip = container_ip.split(':')[0]
                else:
                    container_port = 22

                client = SSHClient()
                client.set_missing_host_key_policy(AutoAddPolicy())
                client.connect(container_ip, port=container_port, username=username, password=password)
                
                try:
                    cmd = 'test -e {} && echo true'.format(status_file)
                    stdin, stdout, stderr = client.exec_command(cmd)
                    has_status = stdout.read()

                    cmd = 'cat {}'.format(status_file)
                    stdin, stdout, stderr = client.exec_command(cmd)
                    job_status = stdout.read()

                    if 'complete' in job_status:
                        r['status'] = job_status
                        mongo_collection.save(r)
                    
                    return json.dumps({"status" : job_status.replace('\n', '')})
                except Exception as e:
                    print str(e)
                    pass

        except Exception as e:
            print str(e)
            pass
        return json.dumps({ "status" : 'n/a' })

class download:
    def POST(self):
        try:
            data = web.data()
            job_id = json.loads(data)['id'] if 'id' in json.loads(data) else None
            if job_id:
                remote_file = '{}/{}/{}.zip'.format(JOB_FOLDER, job_id, OUTPUT_DIR_NAME)
                local_file = '{}/{}_{}.zip'.format(DOWNLOAD_DIR, OUTPUT_DIR_NAME, job_id)
                
                conn_data = json.loads(web.data())
                container_ip = conn_data['container_ip']
                username = conn_data['user']
                password = conn_data['pass']

                if ':' in container_ip:
                    container_port = int(container_ip.split(':')[1])
                    container_ip = container_ip.split(':')[0]
                else:
                    container_port = 22

                client = SSHClient()
                client.set_missing_host_key_policy(AutoAddPolicy())
                client.connect(container_ip, port=container_port, username=username, password=password)

                with SCPClient(client.get_transport()) as scp:
                    scp.get(remote_file, local_file)
                return json.dumps({"success" : 'get completed', "filename": local_file.replace(PUBLIC_DIR_ROOT, '')})

        except Exception as e:
            print str(e)
            pass

        return json.dumps({ "error" : 'an error occurred with the file transfer' })

class delete_job:
    def POST(self):
        try:
            data = web.data()
            job_id = json.loads(data)['id'] if 'id' in json.loads(data) else None
            if job_id:
                mongo_client = pymongo.MongoClient(
                    'localhost', 27017, serverSelectionTimeoutMS=5000)
                mongo_db = mongo_client[database_name]
                mongo_collection = mongo_db['jobs']
                r = mongo_collection.find_one({"id": job_id})

                mongo_collection.remove(r['_id'])
                return json.dumps({"success" : 'delete completed', "id": job_id})

                #TODO: add associated file cleanup
        except Exception as e:
            print str(e)
            pass

        return json.dumps({ "error" : 'an error occurred with the file transfer' })

class preview:
    def POST(self):

        PREVIEW_IMAGE = 'preview.ppm'

        try:
            data = web.data()
            job_id = json.loads(data)['id'] if 'id' in json.loads(data) else None
            command = json.loads(data)['command'] if 'command' in json.loads(data) else None

            if job_id and command:

                conn_data = json.loads(web.data())
                container_ip = conn_data['container_ip']
                username = conn_data['user']
                password = conn_data['pass']

                if ':' in container_ip:
                    container_port = int(container_ip.split(':')[1])
                    container_ip = container_ip.split(':')[0]
                else:
                    container_port = 22

                client = SSHClient()
                client.set_missing_host_key_policy(AutoAddPolicy())
                client.connect(container_ip, port=container_port, username=username, password=password)
                
                preview_file = '{}/{}/{}'.format(JOB_FOLDER, job_id, PREVIEW_IMAGE)
                local_file = '/tmp/' + job_id + '_preview.ppm'
                try:
                    cmd = 'test -e {} && echo true'.format(preview_file)
                    stdin, stdout, stderr = client.exec_command(cmd)
                    has_preview = 'true' in stdout.read()
                    if not has_preview:
                        #generate the image if it doesnt exist
                        cmd = '/scripts/generate_preview.sh "{}" {}'.format(
                            command, preview_file)
                        stdin, stdout, stderr = client.exec_command(cmd)
                        generated = stdout.read()

                    with SCPClient(client.get_transport()) as scp:
                        scp.get(preview_file, local_file)
                    
                    converted_file = local_file.replace('.ppm', '.jpg')
                    Image.open(local_file).save(converted_file)

                    mongo_client = pymongo.MongoClient('localhost', 27017, serverSelectionTimeoutMS=5000)
                    mongo_db = mongo_client[database_name]
                    mongo_collection = mongo_db['jobs']
                    r = mongo_collection.find_one({"id": job_id})

                    with open(converted_file) as imagefile:
                        gfs = gridfs.GridFS(mongo_db)
                        fileid = gfs.put(imagefile.read(), filename=local_file)
                    
                    r['preview_image'] = fileid
                    mongo_collection.save(r)

                    return json.dumps({"success" : 'preview_generated', "imageid": str(fileid)})


                except Exception as e:
                    print e

                
        except Exception as e:
            print str(e)
            pass

        return json.dumps({ "error" : 'an error occurred with the file transfer' })


class generatempeg:
    def POST(self):

        FRAMES_PER_SECOND="4"

        try:
            data = web.data()
            job_id = json.loads(data)['id'] if 'id' in json.loads(data) else None

            if job_id:
                remote_file = '{}/{}/{}.zip'.format(JOB_FOLDER, job_id, OUTPUT_DIR_NAME)
                local_file = '{}/{}_{}.zip'.format(DOWNLOAD_DIR, OUTPUT_DIR_NAME, job_id)
                mpeg_file = '{}/{}.mpeg'.format(DOWNLOAD_DIR, job_id)

                conn_data = json.loads(web.data())
                container_ip = conn_data['container_ip']
                username = conn_data['user']
                password = conn_data['pass']
                
                if ':' in container_ip:
                    container_port = int(container_ip.split(':')[1])
                    container_ip = container_ip.split(':')[0]
                else:
                    container_port = 22

                client = SSHClient()
                client.set_missing_host_key_policy(AutoAddPolicy())
                client.connect(container_ip, port=container_port, username=username, password=password)

                with SCPClient(client.get_transport()) as scp:
                    scp.get(remote_file, local_file)

                extract_dir = '/tmp/mpeg/{}'.format(job_id)
                if not os.path.exists(extract_dir):
                    os.makedirs(extract_dir)
                _zip = zipfile.ZipFile(local_file, 'r')
                _zip.extractall(extract_dir)
                _zip.close()
                subprocess.call(['/src/generate_mpeg.sh', extract_dir, mpeg_file, FRAMES_PER_SECOND])

                return json.dumps({"success" : 'get completed', "filename": mpeg_file.replace(PUBLIC_DIR_ROOT, '')})
        except Exception as e:
            print str(e)
            pass

        return json.dumps({ "error" : 'an error occurred with the mpeg creation' })

if __name__ == "__main__":
    app.run()


