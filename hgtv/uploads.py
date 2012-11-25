#! /usr/bin/env python

import os
from werkzeug import FileStorage
from StringIO import StringIO
from flask import current_app
from flask.ext.uploads import (UploadSet, configure_uploads,
     IMAGES, UploadNotAllowed)


thumbnails = UploadSet('thumbnails', IMAGES,
    default_dest=lambda app: os.path.join(app.static_folder, 'thumbnails'))


def configure(app):
    thumbnails_dir = os.path.join(app.static_folder, 'thumbnails')
    if not os.path.isdir(thumbnails_dir):
        os.mkdir(thumbnails_dir)
    configure_uploads(app, thumbnails)


def return_werkzeug_filestorage(request, filename, maxsize=(320, 240)):
    extension = request.headers['content-type'].split('/')[-1]
    if extension not in current_app.config['ALLOWED_EXTENSIONS']:
        raise UploadNotAllowed("Unsupported file format")
    new_filename = filename + '.' + extension
    tempfile = StringIO(buf=request.content)
    tempfile.name = new_filename
    filestorage = FileStorage(tempfile,
        filename=new_filename,
        content_type=request.headers['content-type'])
    return filestorage
