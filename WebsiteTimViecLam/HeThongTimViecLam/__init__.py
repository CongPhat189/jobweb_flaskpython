from datetime import datetime
from urllib.parse import quote

from authlib.integrations.flask_client import OAuth
from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user
import cloudinary
import os

# from WebsiteTimViecLam.HeThongTimViecLam.models import TaiKhoan

app=Flask(__name__)
app.secret_key='KJHKHJKYGJYGBJNMK@^*&$^*#@!#*(>?<'
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://jobweb_user:8Qx2CALsMwvLjPVFbt65fkuzFpHMLdyk@dpg-d3aef195pdvs73cq1tsg-a.oregon-postgres.render.com:5432/jobweb"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config['PAGE_SIZE']=4
db=SQLAlchemy(app=app)
Login=LoginManager(app=app)
Login.login_view = "login_process"
Login.login_message = u"⚠️ Bạn cần đăng nhập để tiếp tục."
Login.login_message_category = "warning"
app.jinja_env.globals.update(getattr=getattr)




oauth = OAuth(app)
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_id="1084782842046-ad4md49afb5n5um3cmr9totdr0kscimq.apps.googleusercontent.com",
    client_secret="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",
    access_token_url="https://oauth2.googleapis.com/token",
    access_token_params=None,
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    authorize_params={"prompt": "consent", "access_type": "offline"},
    api_base_url="https://www.googleapis.com/oauth2/v2/",
    client_kwargs={"scope": "openid email profile"},
)


cloudinary.config(
    cloud_name = "dvlwb6o7e",
    api_key = "315637758944728",
    api_secret = "A34d8SUWJZnBLiGAgOPEIhqRB_c",
    secure=True
)

app.config['MOMO_PARTNER_CODE'] = "MOMO21KI20250819_TEST"
app.config['MOMO_ACCESS_KEY'] = "W0G8ZaNtjc91prgE"
app.config['MOMO_SECRET_KEY'] = "90HHIW0ENvoHJJL4ScE09vxqpQOMq5ZW"
app.config['MOMO_ENDPOINT'] = "https://test-payment.momo.vn/v2/gateway/api/create"
app.config['MOMO_RETURN_URL'] = "http://127.0.0.1:5000/momo/return"
app.config['MOMO_NOTIFY_URL'] = "http://127.0.0.1:5000/momo/notify"

