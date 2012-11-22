#! /usr/bin/env python

from os.path import join
from werkzeug import FileStorage
from StringIO import StringIO

from flask.ext.uploads import (UploadSet, configure_uploads,
     IMAGES, UploadNotAllowed)

from hgtv import app


uploaded_thumbnails = UploadSet('thumbnails', IMAGES,
    default_dest=lambda app:  join(app.static_folder, app.config['UPLOAD_DIRECTORY']))


def configure():
    configure_uploads(app, uploaded_thumbnails)


def return_werkzeug_filestorage(request, filename, maxsize=(320, 240)):
    extension = request.headers['content-type'].split('/')[-1]
    if extension not in app.config['ALLOWED_EXTENSIONS']:
        raise UploadNotAllowed("Unsupported file format")
    new_filename = filename + '.' + extension
    tempfile = StringIO(buf=request.content)
    tempfile.name = new_filename
    filestorage = FileStorage(tempfile,
        filename=new_filename,
        content_type=request.headers['content-type'])
    return filestorage
