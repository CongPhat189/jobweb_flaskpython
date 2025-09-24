from flask import Blueprint, url_for, redirect, session, request, flash
from authlib.integrations.flask_client import OAuth
from flask_login import login_user, logout_user, current_user
from WebsiteTimViecLam.HeThongTimViecLam import  db,oauth
from WebsiteTimViecLam.HeThongTimViecLam.models import TaiKhoan



auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/google/login')
def google_login():
    redirect_uri = url_for('auth.google_authorize', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@auth_bp.route('/google/authorize')
def google_authorize():
    token = oauth.google.authorize_access_token()
    # Lấy thông tin user: dùng id_token hoặc userinfo endpoint
    # Thường dùng userinfo:
    user_info = oauth.google.parse_id_token(token) if token.get('id_token') else oauth.google.get('userinfo').json()

    # user_info típical contains: sub, email, email_verified, name, picture
    google_sub = user_info.get('sub')
    email = user_info.get('email')
    name = user_info.get('name')
    picture = user_info.get('picture')

    if not email:
        flash("Không thể lấy email từ Google. Vui lòng thử phương thức khác.", "danger")
        return redirect(url_for('main.index'))

    # 1) Nếu có user đã liên kết google_id -> đăng nhập
    user = TaiKhoan.query.filter_by(google_id=google_sub).first()
    if not user:
        # 2) Nếu chưa có, check có user bằng email (đã đăng ký trước đó)
        user = TaiKhoan.query.filter_by(email=email).first()
        if user:
            # OPTION: liên kết tài khoản hiện có với google
            user.google_id = google_sub
            user.avatar = picture
            db.session.commit()
        else:
            # 3) Tạo user mới
            username_base = email.split('@')[0]
            username = username_base
            # ensure unique username
            i = 1
            while TaiKhoan.query.filter_by(username=username).first():
                username = f"{username_base}{i}"
                i += 1

            user = TaiKhoan(
                username=username,
                email=email,
                google_id=google_sub,
                avatar=picture,
                loai_tai_khoan='ungvien'  # hoặc mặc định bạn muốn
            )
            db.session.add(user)
            db.session.commit()

    # login user với Flask-Login
    login_user(user)
    flash("Đăng nhập thành công bằng Google", "success")
    next_url = session.pop('next', None) or url_for('main.index')
    return redirect(next_url)