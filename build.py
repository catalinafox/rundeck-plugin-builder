##########################################################################################
Copyright 2020 Adobe. All rights reserved.
This file is licensed to you under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License. You may obtain a copy
of the License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under
the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR REPRESENTATIONS
OF ANY KIND, either express or implied. See the License for the specific language
governing permissions and limitations under the License.
##########################################################################################
#!/usr/bin/env python3
import git
import os
import argparse
import sys
from jinja2 import Template

def read_input(filename:str, build_path="buildplugins") -> list:
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

    plugins = [x for x in os.listdir(build_path)
                        if os.path.isdir(os.path.join(build_path, x))]
    print("Plugins are {}".format(plugins))
    return plugins

def generate_gradle_tasks(plugins, build_path="buildplugins"):

    tm = Template("{% for plugin in plugins %}\
\ntask {{ plugin.replace(\"-\",\"\") }}(type: Jar) {\n\tbaseName = \"{{ plugin }}\"\
\n\t// add all classes and resources produced from main source set\
\n\tfrom(sourceSets.main.output) {\
\n\t\t// filter to only include the plugin\
\n\t\tinclude \"{{ build_path }}/{{ plugin }}/**\"\
\n\t}\
\n}\
{% endfor %}\
\nartifacts {\
\narchives {% for plugin in plugins %}{% if not loop.first %}, {{plugin}}{% else %}{{plugin}}{% endif %}{% endfor %}\
}\
")
    task = tm.render(plugins=plugins, build_path=build_path)
    print(task)

    return task

def write_tasks(task, in_file="build_input.gradle", out_file="build.gradle"):

    input_file = open(in_file, 'r').readlines()
    write_file = open(out_file,'w')
    for line in input_file:
        write_file.write(line)
    write_file.write(task + "\n")
    write_file.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", dest='input', type=str, help="input file")
    args = parser.parse_args()
    if args.input:
        if not os.path.isfile(args.input):
            print('The specified input file {} does not exist'.format(args.input))
            sys.exit()
        plugins = read_input(str(args.input))
        task = generate_gradle_tasks(plugins=plugins)
        write_tasks(task)

if __name__ == '__main__':
    main()
