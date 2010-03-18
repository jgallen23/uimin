#!/usr/bin/env python

import os
import yaml
from filters.jsmin import jsmin
from filters.cssmin import cssmin
import time

filename_formats = {
    'plain': '%(name)s.%(type)s',
    'plain_min': '%(name)s.min.%(type)s',
    'version': '%(name)s-%(version)s.%(type)s',
    'version_min': '%(name)s-%(version)s.min.%(type)s'
}

def concat(filenames, separator=''):
    """
    Concatenate the files from the list of the ``filenames``, ouput separated with ``separator``.
    """
    r = ''
    for filename in filenames:
        fd = open(filename, 'rb')
        r += fd.read()
        r += separator
        fd.close()
    return r

def write_file(path, filename, data):
    file = open(os.path.join(path, filename), 'w')
    file.write(data)
    file.close()

def get_auto_version(files):
    return int(max([os.stat(os.path.join(f)).st_mtime for f in files]))

def get_file(name, type, min = True):
    config = read_config()
    try:
        group = config[type][name]
        if group.has_key("auto_version") and group["auto_version"]:
            data = { 'name': name, 'version': get_auto_version(group["files"]), 'type': type }
            filename = filename_formats["version_min"] % data if min else filename_formats['version'] % data
            return os.path.join(config['output_dir'], filename)
    except:
        return None

def process_js_group(name, group, output_dir):
    """
    jga.js
    jga.min.js
    jga-{checksum}.js
    jga-{checksum}-min.js
    jga-1.0.js
    jga-1.0.min.js
    """
    files = group['files']

    js = concat(files)
    js_min = jsmin(js)

    if group.has_key("plain") and group["plain"]:
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

    if group.has_key("plain") and group["plain"]:
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

def read_config():
    file = open('uimin.yaml', 'r')
    config = yaml.load(file)
    file.close()
    if not os.path.exists(config["output_dir"]):
        os.mkdir(config["output_dir"])
    return config

def main():
    if not os.path.exists("uimin.yaml"):
        print "Cannot find uimin.yaml"
        return

    config = read_config()

    [process_js_group(name, config["js"][name], config["output_dir"]) for name in config["js"]]
    [process_css_group(name, config["css"][name], config["output_dir"]) for name in config["css"]]
    print get_file('jga', 'js')
    print get_file('jga', 'css')

if __name__ == "__main__": main()

