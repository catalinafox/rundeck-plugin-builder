#!/usr/bin/env python3
##########################################################################################
# Copyright 2020 Adobe. All rights reserved.
# This file is licensed to you under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License. You may obtain a copy
# of the License at http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
# OF ANY KIND, either express or implied. See the License for the specific language
# governing permissions and limitations under the License.
##########################################################################################
import git
import os
import argparse
import sys
import subprocess
import shlex

def read_input(filename:str, build_path="buildplugins") -> set:
    if not os.path.isdir(build_path):
        os.mkdir(build_path)
        print ("Build path is created at {}/{}...".format(os.getcwd(), build_path))
    else:
        print("Build path already exists at {}/{}...".format(os.getcwd(), build_path))

    with open(filename,"r") as f:
        for i in range(13):
            f.readline()
        for line in f:
            plugin_name = line.strip().split("/")[-1]
            print("Cloning {}...".format(plugin_name))
            if os.path.isdir(os.getcwd() + "/buildplugins/" + plugin_name):
                print("Repository already exists. Jumping to the next...")
            else:
                git.Git(build_path).clone(line.strip())

    plugins = {x for x in os.listdir(build_path) if os.path.isdir(os.path.join(build_path, x))}

    return plugins

def build_plugin(plugin, built_plugins):
    delimiter = '\n'+ '-'  * 200 + '\n'
    rundeck_rootdir = os.getcwd()
    os.chdir(os.getcwd() + "/buildplugins/" + plugin)
    print("{}Building {}{}".format(delimiter, plugin, delimiter))
    run_command('gradle clean build', built_plugins, plugin)
    os.chdir(rundeck_rootdir)

def run_command(command, built_plugins, plugin):
    process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
    while True:
        output = process.stdout.readline()
        if not output and process.poll() is not None:
            break
        if output:
            print(output.strip().decode('utf-8'))
            if 'BUILD SUCCESSFUL' in output.strip().decode('utf-8'):
                built_plugins.add(plugin)
    rc = process.poll()
    return rc

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", dest='input', type=str, help="input file")
    args = parser.parse_args()
    if args.input:
        if not os.path.isfile(args.input):
            print('The specified input file {} does not exist'.format(args.input))
            sys.exit()
        plugins = read_input(str(args.input))
        built_plugins = set()
        for plugin in plugins:
            build_plugin(plugin, built_plugins)

    print("Successfully built: {}".format(', '.join(map(str, built_plugins))))
    print("Build failed for: {}".format(', '.join(map(str, plugins-built_plugins))))

if __name__ == '__main__':
    main()
