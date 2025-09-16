from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required

from WebsiteTimViecLam.HeThongTimViecLam import app, db, dao, Login

from WebsiteTimViecLam.HeThongTimViecLam.dao import loadTinTuyenDung,ungTuyen
from WebsiteTimViecLam.HeThongTimViecLam.decorater import annonymous_user
from WebsiteTimViecLam.HeThongTimViecLam.models import HoSoXinViec


@Login.user_loader #Nhiem vu,Tacdung ?
def get_user(user_id):
    return dao.get_user_by_ID(user_id)

@app.route("/")
def index():
    tintuyendung=loadTinTuyenDung()
    return  render_template("index.html",ttd=tintuyendung)

@app.route("/taocv", methods=["GET", "POST"])
def tao_cv_route():
    if request.method == "POST":
        hs = dao.tao_cv(
            ten_hs=request.form.get("ten_hs"),
            ma_uv=1,  # giả sử user đã đăng nhập
            muc_tieu=request.form.get("vitri"),
            file=request.files.get("file_cv")
        )
        flash("Tạo CV thành công!", "success")
        return redirect(url_for("tao_cv_route"))

    return render_template("taocv.html")


@app.route("/ungtuyen/<int:ma_ttd>", methods=["GET", "POST"])
def ung_tuyen(ma_ttd):
    if request.method == "POST":
        file = request.files.get("file")  # lấy file PDF từ form
        result = ungTuyen(ma_ttd=ma_ttd, file=file)
        if result:
            flash("Ứng tuyển thành công!", "success")
            return redirect(url_for("ung_tuyen", ma_ttd=ma_ttd))
        else:
            flash("Ứng tuyển thất bại. Vui lòng thử lại.", "danger")
            return redirect(url_for("ung_tuyen", ma_ttd=ma_ttd))

    # Nếu là GET thì hiển thị form upload
    return render_template("ungtuyen.html", ma_ttd=ma_ttd)


@app.route('/apply/<int:ma_ttd>', methods=['POST'])
def apply(ma_ttd):
    file = request.files.get('cv')
    if file and file.filename.endswith('.pdf'):
        # Lưu file hoặc xử lý hồ sơ ứng tuyển ở đây
        file.save(f"uploads/cv_{ma_ttd}.pdf")
        flash("Ứng tuyển thành công!")
    else:
        flash("Vui lòng tải lên file PDF hợp lệ.")

    return redirect(url_for('index'))  # quay lại trang chính

@app.route("/login", methods=['get','post'])
@annonymous_user

def login_process():
    if request.method.__eq__('POST'):
        username=request.form.get('username')
        password=request.form.get('password')
        u=dao.auth_user(username=username, password=password)
        if u:
            login_user(u)


            next = request.args.get('next')
            return redirect(next if next else '/')
    return render_template('login.html')

if __name__=="__main__":
    with app.app_context():
        app.run(debug=True, port=5000)