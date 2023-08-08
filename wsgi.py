import os.path
import sys

from flask.cli import load_dotenv
from flask.helpers import get_load_dotenv

__all__ = ['application']

sys.path.insert(0, os.path.dirname(__file__))
if get_load_dotenv():
    load_dotenv()

# pylint: disable=wrong-import-position
from hgtv import app as application
