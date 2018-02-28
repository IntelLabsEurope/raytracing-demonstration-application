#!/bin/bash

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


#requires ImageMagic convert & mencoder to be installed
#expects a full path to a folder of images
#images are ppm format (output from embree) and numbered sequentially 00001.ppm to nnnnn.ppm

# $1: path to folder of images
# $2: full path to ouput file
# $3: frames per second

for f in $1/*.ppm; do convert -quality 100 $f $1/`basename $f .ppm`.jpg; done
mencoder "mf://"$1/"*.jpg" -mf fps=$3 -o $2 -ovc lavc -lavcopts vcodec=msmpeg4v2:vbitrate=800
