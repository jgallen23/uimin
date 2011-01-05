#!/usr/bin/env python

import sys
import os
import yaml
from filters.jsmin import jsmin
from filters.cssmin import cssmin
import time

DEBUG = False
ROOT = os.getcwd()

filename_formats = {
    'plain': '%(name)s.%(type)s',
    'plain_min': '%(name)s.min.%(type)s',
    'version': '%(name)s-%(version)s.%(type)s',
    'version_min': '%(name)s-%(version)s.min.%(type)s'
}

def debug(message):
    print message

def concat(filenames, separator=''):
    """
    Concatenate the files from the list of the ``filenames``, ouput separated with ``separator``.
    """
    r = ''
    for filename in filenames:
        debug("Concatinating file: %s" % filename)
        fd = open(os.path.join(ROOT, filename), 'rb')
        r += fd.read()
        r += separator
        fd.close()
    return r

def write_file(path, filename, data):
    filepath = os.path.join(path, filename)
    #if not os.path.exists(filepath):
    file = open(filepath, 'w')
    file.write(data)
    file.close()
    debug("File Created: %s" % filename)

def get_auto_version(files):
    return int(max([os.stat(os.path.join(ROOT, f)).st_mtime for f in files]))

def get_file(name, type, min = True):
    config = read_config()
    #try:
    group = config[type][name]
    if not group.has_key("auto_version") or group["auto_version"]:
        data = { 'name': name, 'version': get_auto_version(group["files"]), 'type': type }
        filename = filename_formats["version_min"] % data if min else filename_formats['version'] % data
        return os.path.join(config['output_dir'], filename)
    #except:
        #return None

def get_files(name, type):
    config = read_config()
    #try:
    group = config[type][name]
    return [filename for filename in group['files']]

def process_inheritance(config, group):
    if group.has_key('inherit'):
        process_inheritance(config, config['js'][group['inherit']])
        for file in reversed(config['js'][group['inherit']]['files']):
            group['files'].insert(0, file)
        del group['inherit']

def process_js_group(name, group, output_dir):
    """
    jga.js
    jga.min.js
    jga-{checksum}.js
    jga-{checksum}-min.js
    jga-1.0.js
    jga-1.0.min.js
    """
    debug("\nGenerating: %s" % name)
    files = group['files']

    js = concat(files)
    js_min = jsmin(js)

    if not group.has_key("plain") or (group.has_key("plain") and group["plain"]):
        file_data = { 'name': name, 'type': 'js' }
        filename = filename_formats['plain']  % file_data
        filename_min = filename_formats['plain_min'] % file_data
        write_file(output_dir, filename, js)
        write_file(output_dir, filename_min, js_min)
    if group.has_key("version") or (group.has_key('auto_version') and group['auto_version']):
        file_data = { 'name': name,
                'version': group['version'] if group.has_key("version") else get_auto_version(files),
                'type': 'js' }
        filename = filename_formats['version'] % file_data
        filename_min = filename_formats['version_min']  % file_data
        write_file(output_dir, filename, js)
        write_file(output_dir, filename_min, js_min)

def process_css_group(name, group, output_dir):
    """
    jga.css
    jga.min.css
    jga-{checksum}.css
    jga-{checksum}-min.css
    jga-1.0.css
    jga-1.0.min.css
    """
    files = group['files']

    css = concat(files)
    css_min = cssmin(css)

    if not group.has_key("plain") or (group.has_key("plain") and group["plain"]):
        file_data = { 'name': name, 'type': 'css' }
        filename = filename_formats['plain']  % file_data
        filename_min = filename_formats['plain_min'] % file_data
        write_file(output_dir, filename, css)
        write_file(output_dir, filename_min, css_min)
    if group.has_key("version") or (group.has_key('auto_version') and group['auto_version']):
        file_data = { 'name': name,
                'version': group['version'] if group.has_key("version") else get_auto_version(files),
                'type': 'css' }
        filename = filename_formats['version'] % file_data
        filename_min = filename_formats['version_min']  % file_data
        write_file(output_dir, filename, css)
        write_file(output_dir, filename_min, css_min)

def read_config(file):
    config_path = os.path.join(ROOT, file)
    if not os.path.exists(config_path):
        raise
    file = open(config_path, 'r')
    config = yaml.load(file)
    file.close()
    #if not os.path.exists(config["output_dir"]):
        #os.mkdir(config["output_dir"])
    return config

def get_file_list(file, type, name, debug = False, format = "plain_min"):
    config = read_config(file)
    process_inheritance(config, config['js'][name])
    group = config[type][name]
    if not debug:
        file_data = { 'name': name, 'type': type }
        filename_min = filename_formats[format]  % file_data
        return [filename_min]
    else:
        return group['files']



def main(args):
    if len(args) == 0:
        file = "uimin.yaml"
    else:
        file = os.path.join(os.getcwd(), args[0])

    if not os.path.exists(file):
        print "Cannot find ", file
        return


    config = read_config(file)

    if not os.path.exists(config['output_dir']):
        os.mkdir(config['output_dir'])

    if config.has_key('js'):
        [process_inheritance(config, config['js'][name]) for name in config['js']]
        [process_js_group(name, config["js"][name], config["output_dir"]) for name in config["js"]]
    if config.has_key('css'):
        [process_inheritance(config, config['css'][name]) for name in config['css']]
        [process_css_group(name, config["css"][name], config["output_dir"]) for name in config["css"]]

if __name__ == "__main__": main(sys.argv[1:])

