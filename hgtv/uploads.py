#! /usr/bin/env python

import boto3
import botocore
from datetime import datetime
from PIL import Image
import os
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from io import BytesIO
from hgtv import app


class UploadNotAllowed(Exception):
    pass


class S3Uploader:
    def __init__(self, folder):
        self.folder = folder

    def init_app(self, app):
        self._s3_resource = boto3.resource(
            "s3",
            aws_access_key_id=app.config["AWS_ACCESS_KEY"],
            aws_secret_access_key=app.config["AWS_SECRET_KEY"],
        )
        self._s3_bucket = self._s3_resource.Bucket(app.config["AWS_BUCKET"])

    def exists_in_s3(self, key):
        try:
            self._s3_bucket.Object(key).load()
        except botocore.exceptions.ClientError:
            return False
        return True

    def save(self, filestorage):
        """
        Uploads the given FileStorage object to S3 and returns the key.

        :param filestorage: FileStorage object that needs to be uploded.
        """
        # check if it's already uploaded on S3
        key = os.path.join(self.folder, filestorage.filename)
        if not self.exists_in_s3(key):
            # upload it to s3
            self._s3_bucket.put_object(
                ACL="public-read",
                Key=key,
                Body=filestorage.read(),
                CacheControl="max-age=31536000",
                ContentType=filestorage.content_type,
                Expires=datetime.utcnow() + timedelta(days=365),
            )
        return filestorage.filename

    def delete(self, thumbnail_name):
        key = os.path.join(self.folder, thumbnail_name)
        if self.exists_in_s3(key):
            # upload it to s3
            self._s3_resource.meta.client.delete_object(
                Bucket=app.config["AWS_BUCKET"], Key=key
            )

    def get_url(self, thumbnail_name):
        return os.path.join(app.config["MEDIA_DOMAIN"], self.folder, thumbnail_name)


thumbnails = S3Uploader(folder="thumbnails")


def return_werkzeug_filestorage(request, filename):
    extension = request.headers["content-type"].split("/")[-1]
    if extension not in app.config["ALLOWED_EXTENSIONS"]:
        raise UploadNotAllowed("Unsupported file format")
    new_filename = secure_filename(filename + "." + extension)
    if isinstance(request, FileStorage):
        tempfile = BytesIO(request.read())
    else:
        # this will be requests' Response object
        tempfile = BytesIO(request.content)
    tempfile.name = new_filename
    filestorage = FileStorage(
        tempfile, filename=new_filename, content_type=request.headers["content-type"]
    )
    return filestorage


def resize_image(requestfile, maxsize=(320, 240)):
    fileext = requestfile.filename.split(".")[-1].lower()
    if fileext not in app.config["ALLOWED_EXTENSIONS"]:
        raise UploadNotAllowed("Unsupported file format")
    img = Image.open(requestfile)
    img.load()
    if img.size[0] > maxsize[0] or img.size[1] > maxsize[1]:
        img.thumbnail(maxsize, Image.ANTIALIAS)
    boximg = Image.new("RGBA", (img.size[0], img.size[1]), (255, 255, 255, 0))
    boximg.paste(img, (0, 0))
    savefile = BytesIO()
    if fileext in ["jpg", "jpeg"]:
        savefile.name = secure_filename(
            ".".join(requestfile.filename.split(".")[:-1]) + ".png"
        )
        boximg.save(savefile, format="PNG")
        content_type = "image/png"
    else:
        savefile.name = secure_filename(requestfile.filename)
        boximg.save(savefile)
        content_type = requestfile.content_type
    savefile.seek(0)
    return FileStorage(savefile, filename=savefile.name, content_type=content_type)
