from urllib.parse import quote
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import cloudinary


app=Flask(__name__)
app.secret_key='KJHKHJKYGJYGBJNMK@^*&$^*#@!#*(>?<'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/jobweb?charset=utf8mb4" % quote('Admin123')

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config['PAGE_SIZE']=4

db=SQLAlchemy(app=app)
Login=LoginManager(app=app)
Login.login_view = "login_process"
Login.login_message = u"⚠️ Bạn cần đăng nhập để tiếp tục."
Login.login_message_category = "warning"  # có thể là success, danger, info, warning


cloudinary.config(
    cloud_name = "dvlwb6o7e",
    api_key = "315637758944728",
    api_secret = "A34d8SUWJZnBLiGAgOPEIhqRB_c",
    secure=True
)