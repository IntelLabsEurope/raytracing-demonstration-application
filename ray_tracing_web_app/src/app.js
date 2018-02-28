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
var formidable = require('express-formidable');
var path = require('path');
var favicon = require('serve-favicon');
var logger = require('morgan');
var cookieParser = require('cookie-parser');
var bodyParser = require('body-parser');

var mongo = require('mongodb');
var monk = require('monk');
var conf = require('./config.js');
var db = monk(conf.connection_string);

//monk still doesnt support gridfs??
//adding in a mongoose connection just for that
var mongoose = require('mongoose')
mongoose.connect('mongodb://' + conf.connection_string);
var gfs_db = mongoose.connection;
var GridStore = require('mongodb').GridStore;
var ObjectID = require('mongodb').ObjectID;

var routes = require('./routes/index');

var app = express();

// view engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'jade');
app.set('DEBUG', conf.debug);

// uncomment after placing your favicon in /public
//app.use(favicon(path.join(__dirname, 'public', 'favicon.ico')));
app.use(logger('dev'));
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));

//express-formiddable middleware
app.use(formidable.parse({ uploadDir: conf.upload_dir, keepExtensions: true }));

app.use(function(req,res,next){
    req.db = db;
    next();
});

//routine to get serve a gridfs stored image by its id
//currently only supports/assumes PNG
var getFile = function(callback, id) {
  var gs = new GridStore(gfs_db, new ObjectID(id), 'r');
  gs.open(function(err,gs){
      gs.read(callback);
  });
};
app.get('/data/:image_id', function(req, res) {
  getFile(function(error, data) {
     res.writeHead('200', {'Content-Type': 'image/png'});
     res.end(data,'binary');
  }, req.params.image_id);
});

app.use('/', routes);

// catch 404 and forward to error handler
app.use(function(req, res, next) {
  var err = new Error('Not Found');
  err.status = 404;
  next(err);
});

// error handlers

// development error handler
// will print stacktrace
if (app.get('env') === 'development') {
  app.use(function(err, req, res, next) {
    res.status(err.status || 500);
    res.render('error', {
      message: err.message,
      error: err
    });
  });
}

// production error handler
// no stacktraces leaked to user
app.use(function(err, req, res, next) {
  res.status(err.status || 500);
  res.render('error', {
    message: err.message,
    error: {}
  });
});

module.exports = app;
