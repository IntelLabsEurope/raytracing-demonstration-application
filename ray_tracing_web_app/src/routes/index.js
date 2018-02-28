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

var express = require('express');
var router = express.Router();
var request = require('request');
var conf = require('../config.js');
var uuid = require('node-uuid');

var DEBUG = conf.debug;

/* BASIC ROUTING */
router.get('/', function(req, res) {
    var db = req.db;
    var collection = db.get('config');
    
    collection.find({},{},function(e,docs){
        if (docs && docs.length > 0 && 'url' in docs[0]){
            res.render('index', {
                "embree_url" : docs[0]['url']
            });
        }
        else{
            res.render('index', {
                "embree_url" : 'Ray Tracing Engine not found, please update!'
            });
        }
    });

});

router.get('/status', function(req, res) {
    var db = req.db;
    var collection = db.get('jobs');
    collection.find({},{},function(e,docs){
        res.render('status', {
            "jobs" : docs
        });
    });
});

/*
*
*   Request urls to route stuff via python.
*
*/

var generateCommand = function(data, container_ip, is_phi){

    var port = ''
    var url = ''
    if (container_ip.indexOf(':') >= 0){
        url = container_ip.split(':')[0]
        port = container_ip.split(':')[1]
    }
    if (port){
        return 'ssh -X ' + conf.embree_user + '@' + url + ' -p ' + port + ' ' + generateExec(data, is_phi)
    }
    else{
        return 'ssh -X ' + conf.embree_user + '@' + container_ip + ' ' + generateExec(data, is_phi)   
    }
}

var generateExec = function(data, is_phi){
    if (is_phi === undefined)
        is_phi = false;
    var epath_base = '/embree/embree-2.8.0.x86_64.linux/';
    var epath_source = epath_base + 'embree-vars.sh';
    var epath_exec = epath_base + 'bin/pathtracer' + (is_phi == 'True'? '_xeonphi' : '');

    return epath_exec + ' -i ' + data.model_path +
            ' -ambientlight ' + data.ambient_light.split(',').join(' ') +
            ' -size ' + data.frame_size.split('x').join(' ') +
            ' -vp ' + data.camera_pos.split(',').join(' ') +
            ' -vi ' + data.camera_look.split(',').join(' ')
}

var checkPHI = function(){

}

//TODO - refactor / tidy
router.post('/file/upload', function(req, res) {
    var the_file = req.body['file-0'];
    var the_data = req.body['json'];
    var create_data = JSON.parse(the_data)

    var job_id = uuid.v4();

    var db = req.db;
    var collection = db.get('config');
    collection.find({},{},function(e,docs){

        //container_ip = '172.17.0.3';
        container_ip = docs[0]['url'];

        var interactive = ((create_data['job_type'] == 'Interactive')? true : false);
        create_data['status'] = (interactive)? 'n/a' : 'please wait...';

        //uploaded path on local machine, were assuming the python code is running on same machine for now.
        var options = {
            uri: 'http://0.0.0.0:' + conf.webservice_port + '/file/send',
            method: 'POST',
            json: {
                'ip': container_ip,
                'job_id': job_id,
                'user': conf.embree_user,
                'pass': conf.embree_pass,
                'key_filename': conf.key_filename,
                'filename': the_file.name,
                'path': the_file.path,
                'model_suffix' : conf.model_suffix,
                'interactive': interactive
            }
        };
        request(options, function (error, response, body) {
            if(body == 'None'){
                res.send({ 'error' : 'no response from embree engine'})
            }
            else{
                var result_obj = body
                if ('error' in result_obj){
                    res.send({ 'error' : result_obj['error']});
                }
                else{
                    create_data.model_path = result_obj.path;
                    create_data.id = job_id;
                    create_data.command = generateCommand(create_data, container_ip, result_obj.phi);
                    //create job
                    var options = {
                        uri: 'http://0.0.0.0:' + conf.webservice_port + '/jobs/create',
                        method: 'POST',
                        json: create_data
                    };
                    request(options, function (error, response, body) {
                        //if (!error && 200 <= response.statusCode < 300 && 'token' in body) {
                        if(true){
                            res.send({'success': 'job created'})
                        }
                        else{
                            res.send({ 'error' : 'could not save job'});
                        }
                    });
                }
            }
        });
    });//end collection find
});

router.get('/file/url', function(req, res) {
});

router.post('/jobs/create', function(req, res) {
    var data = req.body;
    var options = {
        uri: 'http://0.0.0.0:' + conf.webservice_port + '/jobs/create',
        method: 'POST',
        json: data
    };
    request(options, function (error, response, body) {
        //if (!error && 200 <= response.statusCode < 300 && 'token' in body) {
        if(true){
            res.send('a')
        }
        else{
            res.send('b');
        }
    });

});

router.post('/jobstatus', function(req, res) {
    var data = req.body;
    var db = req.db;
    var collection = db.get('config');
    collection.find({},{},function(e,docs){
        data['container_ip'] = docs[0]['url'];
        data['user'] = conf.embree_user;
        data['pass'] = conf.embree_pass;

        var options = {
            uri: 'http://0.0.0.0:' + conf.webservice_port + '/jobstatus',
            method: 'POST',
            json: data
        };

        request(options, function (error, response, body) {
            //if (!error && 200 <= response.statusCode < 300 && 'token' in body) {
            if (body !== undefined && 'status' in body){
                res.send(body)
            }
            else{
                //TODO: handle this
                res.send(null);
            }
        });
    });
});

router.post('/download', function(req, res) {
    var data = req.body;
    var db = req.db;
    var collection = db.get('config');
    collection.find({},{},function(e,docs){
        //container_ip = '172.17.0.3';
        data['container_ip'] = docs[0]['url'];
        data['user'] = conf.embree_user;
        data['pass'] = conf.embree_pass;

        var options = {
            uri: 'http://0.0.0.0:' + conf.webservice_port + '/download',
            method: 'POST',
            json: data
        };

        request(options, function (error, response, body) {
            //if (!error && 200 <= response.statusCode < 300 && 'token' in body) {
            
            if (body !== undefined && 'filename' in body){
                res.send(body)
            }
            else{
                //TODO: handle this
                res.send(null);
            }
        });
    });
});


router.post('/delete', function(req, res) {
    var data = req.body;
    var options = {
        uri: 'http://0.0.0.0:' + conf.webservice_port + '/delete',
        method: 'POST',
        json: data
    };

    request(options, function (error, response, body) {
        if (body !== undefined && 'success' in body){
            res.send(body)
        }
        else{
            //TODO: handle this
            res.send(null);
        }
    });

});


router.post('/generatepreview', function(req, res) {
    var data = req.body;
    var db = req.db;
    var collection = db.get('jobs');
    var cfg_collection = db.get('config');
    cfg_collection.find({},{},function(e,docs){
        //container_ip = '172.17.0.3';
        data['container_ip'] = docs[0]['url'];
        data['user'] = conf.embree_user;
        data['pass'] = conf.embree_pass;
        collection.findOne({'id': data['id']}, function(e,item){
            var a = generateExec(item)
            data['command'] = a;
            var options = {
                uri: 'http://0.0.0.0:' + conf.webservice_port + '/preview',
                method: 'POST',
                json: data
            };
            request(options, function (error, response, body) {
                if (body !== undefined && 'success' in body){
                    res.send(body)
                }
                else{
                    //TODO: handle this
                    res.send(null);
                }
            });
        });
    });
});

router.post('/generatempeg', function(req, res) {
    var data = req.body;
    var db = req.db;
    var collection = db.get('config');
    collection.find({},{},function(e,docs){
        //container_ip = '172.17.0.3';
        data['container_ip'] = docs[0]['url'];
        data['user'] = conf.embree_user;
        data['pass'] = conf.embree_pass;

        var options = {
            uri: 'http://0.0.0.0:' + conf.webservice_port + '/generatempeg',
            method: 'POST',
            json: data
        };
        request(options, function (error, response, body) {
            if (body !== undefined && 'success' in body){
                res.send(body)
            }
            else{
                //TODO: handle this
                res.send(null);
            }
        }); 
    });
});

module.exports = router;


