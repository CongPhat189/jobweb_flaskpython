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

from flask import request, redirect, render_template, url_for
from flask_login import login_user
from WebsiteTimViecLam.HeThongTimViecLam import dao, app


@app.route("/login", methods=["GET", "POST"])
@annonymous_user
def login_process():
    err_msg = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        role = request.form.get("role")  # lấy role từ form nếu có (admin/ungvien/nhatuyendung)

        # Gọi DAO để kiểm tra user
        u = dao.auth_user(username=username, password=password, role=role)
        if u:
            login_user(u)

            # Sau khi login, điều hướng về trang được yêu cầu hoặc trang chủ
            next_url = request.args.get("next")
            return redirect(next_url if next_url else "/")
        else:
            err_msg = "Sai tên đăng nhập, mật khẩu hoặc quyền truy cập!"

    return render_template("login.html", err_msg=err_msg)


@app.route("/register", methods=["GET", "POST"])
@annonymous_user
def register_process():
    err_msg = None
    if request.method == "POST":
        name = request.form.get("name")
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        role = request.form.get("role") or "UNGVIEN"  # mặc định ứng viên nếu không chọn
        avatar = request.files.get("avatar")

        if not all([name, username, email, password, confirm]):
            err_msg = "Vui lòng nhập đầy đủ thông tin!"
        elif password != confirm:
            err_msg = "Mật khẩu xác nhận không khớp!"
        else:
            try:
                dao.add_user(
                    name=name,
                    username=username,
                    email=email,
                    password=password,
                    role=role,
                    avatar=avatar,
                )
                return redirect(url_for("login_process"))
            except Exception as ex:
                err_msg = f"Đăng ký thất bại: {str(ex)}"

    return render_template("register.html", err_msg=err_msg)


@app.route("/ungvien/applied_jobs")
@login_required
def applied_jobs():
    jobs = dao.get_applied_jobs(current_user.id)
    for job in jobs:
        print(job.nha_tuyen_dung)
        print(job.muc_luong.ten_muc_luong)
    return render_template("applied_jobs.html", jobs=jobs)

@app.route("/logout")
def logout_process():
    logout_user()
    return redirect('/login')




if __name__=="__main__":
    with app.app_context():
        app.run(debug=True, port=5000)