#! /usr/bin/env python

import os
from io import BytesIO

from flask import current_app
from flask_uploads import IMAGES, UploadNotAllowed, UploadSet, configure_uploads
from PIL import Image
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

thumbnails = UploadSet(
    'thumbnails',
    IMAGES,
    default_dest=lambda app: os.path.join(app.static_folder, 'thumbnails'),
)


def configure(app):
    thumbnails_dir = os.path.join(app.static_folder, 'thumbnails')
    if not os.path.isdir(thumbnails_dir):
        os.mkdir(thumbnails_dir)
    configure_uploads(app, thumbnails)


def return_werkzeug_filestorage(request, filename):
    extension = request.headers['content-type'].split('/')[-1]
    if extension not in current_app.config['ALLOWED_EXTENSIONS']:
        raise UploadNotAllowed("Unsupported file format")
    new_filename = secure_filename(filename + '.' + extension)
    if isinstance(request, FileStorage):
        tempfile = BytesIO(request.read())
    else:
        # this will be requests' Response object
        tempfile = BytesIO(request.content)
    tempfile.name = new_filename
    filestorage = FileStorage(
        tempfile, filename=new_filename, content_type=request.headers['content-type']
    )
    return filestorage


def resize_image(requestfile, maxsize=(320, 240)):
    fileext = requestfile.filename.split('.')[-1].lower()
    if fileext not in current_app.config['ALLOWED_EXTENSIONS']:
        raise UploadNotAllowed("Unsupported file format")
    img = Image.open(requestfile)
    img.load()
    if img.size[0] > maxsize[0] or img.size[1] > maxsize[1]:
        img.thumbnail(maxsize, Image.ANTIALIAS)
    boximg = Image.new('RGBA', (img.size[0], img.size[1]), (255, 255, 255, 0))
    boximg.paste(img, (0, 0))
    savefile = BytesIO()
    if fileext in ['jpg', 'jpeg']:
        savefile.name = secure_filename(
            ".".join(requestfile.filename.split('.')[:-1]) + ".png"
        )
        boximg.save(savefile, format="PNG")
        content_type = "image/png"
    else:
        savefile.name = secure_filename(requestfile.filename)
        boximg.save(savefile)
        content_type = requestfile.content_type
    savefile.seek(0)
    return FileStorage(savefile, filename=savefile.name, content_type=content_type)
