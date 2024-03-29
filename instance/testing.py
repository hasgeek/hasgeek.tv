#: Site title
SITE_TITLE = "Hasgeek.tv"
#: Site id (for network bar)
SITE_ID = "hgtv"
#: Database backend
SQLALCHEMY_DATABASE_URI = "sqlite:///test.db"
#: Secret key
SECRET_KEY = "make this something random"
#: Allowed Extensions for thumbnails
ALLOWED_EXTENSIONS = ["jpg", "jpeg", "png", "gif"]
#: Timezone
TIMEZONE = "Asia/Calcutta"
#: LastUser server
LASTUSER_SERVER = "https://auth.hasgeek.com/"
#: LastUser client id
LASTUSER_CLIENT_ID = ""
#: LastUser client secret
LASTUSER_CLIENT_SECRET = ""
#: YouTube Data API key for import
YOUTUBE_API_KEY = ""
#: Mail settings
#: MAIL_FAIL_SILENTLY : default True
#: MAIL_SERVER : default 'localhost'
#: MAIL_PORT : default 25
#: MAIL_USE_TLS : default False
#: MAIL_USE_SSL : default False
#: MAIL_USERNAME : default None
#: MAIL_PASSWORD : default None
#: DEFAULT_MAIL_SENDER : default None
MAIL_FAIL_SILENTLY = False
MAIL_SERVER = "localhost"
DEFAULT_MAIL_SENDER = ("Hasgeek.tv", "test@example.com")
#: Logging: recipients of error emails
ADMINS = []
#: Log file
LOGFILE = "error.log"
#: Video view mode (make this 'edit' to prevent autoplay)
VIDEO_VIEW_MODE = "view"
#: Are we livestreaming?
LIVESTREAM = []
#: Ustream key
USTREAM_KEY = ""
