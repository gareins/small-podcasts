#!/bin/python

from flask import Flask, Response, request, abort
from requests import head, get
from urllib.parse import urlparse
from xml.etree import ElementTree
# from base_setup import Session, File

import subprocess
import re
import os

# Django url parser
valid_url_regex = re.compile(
    r'^https?://'  # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)

# parser for mp3 links
valid_mp3_regex = re.compile(r'https?://([^\s]+)\.(mp3|ogg|m4a|aac)', re.IGNORECASE)

# good audio mimetypes
AUDIO_MIMETYPES = ['audio/ogg', 'audio/ogg', 'audio/mpeg']

# good rss mimetypes
FEED_MIMETYPES = ['text/xml', 'application/rss+xml', 'application/rdf+xml', 'application/atom+xml', 'application/xml']


def is_valid_url(url):
    return bool(url is not None and valid_url_regex.search(url))


def check_params(dct, types):
    if "url" not in dct:
        return 400
    else:
        file_url = dct["url"]

    # Test if valid
    if not is_valid_url(file_url):
        return 402

    # Test if valid
    if not is_valid_url(file_url):
        return 403

    # Test if online
    try:
        hd = head(file_url, allow_redirects=True)
    except Exception as e:
        app.logger.debug(e)
        return 404

    # Test if 2xx status
    if not (200 <= hd.status_code <= 299):
        return 405

    # Test if audio file
    typ = hd.headers['Content-type']
    if typ.find(";") != -1:
        typ = typ[0:typ.find(";")]

    if typ not in types:
        return 406

    return file_url


def compute_new_url(old_url):
    p = urlparse(old_url)
    fname = os.path.basename(p.path)
    fname = "".join(fname.split(".")[:-1]) + ".opus"

    return request.url_root + "file/" + fname + "?url=" + old_url

app = Flask(__name__)


@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/file/<string:file_name>')
def file_handler(_, methods=['GET']):
    file_url = check_params(request.args, AUDIO_MIMETYPES)
    if type(file_url) is int:
        abort(file_url)

    # All tests pass, run conversion
    def opus_generator():
        ps1 = subprocess.Popen(('wget', '-qO-', file_url), stdout=subprocess.PIPE)
        ps2 = subprocess.Popen(('ffmpeg', '-i', '-', '-f', 'opus', '-loglevel', 'panic', '-b:a', '32k', '-vbr', 'on',
                                '-compression_level', '3', '-'), stdin=ps1.stdout, stdout=subprocess.PIPE)

        while ps2.poll() is None:
            yield ps2.stdout.read(1024)

        yield ps2.communicate()[0]

    return Response(opus_generator(), mimetype='audio/ogg')


def xml_parser(txt):
    xml_root = ElementTree.fromstring(txt)
    xml_parse_node(xml_root)
    return ElementTree.tostring(xml_root, encoding='utf8', method='xml')


def xml_parse_node(node):
    if node.text:            
        rgx = valid_mp3_regex.search(node.text)
        if rgx:
            node.text = compute_new_url(node.text)

    if "url" in node.attrib:
        rgx = valid_mp3_regex.search(node.attrib["url"])
        if rgx:
            node.attrib["url"] = compute_new_url(node.attrib["url"])

    for child in node:
        xml_parse_node(child)


@app.route('/feed/<string:feed_name>')
def feed_handler(_, methods=['GET']):
    feed_url = check_params(request.args, FEED_MIMETYPES)
    if type(feed_url) is int:
        abort(feed_url)

    ret = xml_parser(get(feed_url).text)
    return ret


if __name__ == '__main__':
    app.run(debug=True)
