#!/bin/bash

#!/bin/bash
#
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


# executes a batch file sequence of renders
# outputs images to a directory#
# updates render status to "x/y" or "completed" when done
# zips output folder when completed to <output_dirname>.zip

# $1: an absolute path to the job folder
# $2: full path to the obj file
# $3: the binary to use
# $4: the batch filename: batch.txt in general
source /embree/embree-2.8.0.x86_64.linux/embree-vars.sh

obj_file=$2
exe='/embree/embree-2.8.0.x86_64.linux/bin/'$3
output_dir_name='output'
status_file_name='status.txt'

output_path=$1'/'$output_dir_name
status_file=$1'/'$status_file_name

count=1
job_size=$(wc -l < $1'/'$4)

while read cmd
do
    padded_count=$(printf "%05d" $count)

    out_file=$output_path'/image-'$padded_count'.ppm'
    e_cmd=$exe' -i '$obj_file' '$cmd' -o '$out_file
    eval $e_cmd
    echo $count'/'$job_size > $status_file
    count=$((count+1))
done < $1'/'$4

echo 'complete' > $status_file
zip_cmd='zip -jr  '$1'/'$output_dir_name'.zip '$output_path

eval $zip_cmd