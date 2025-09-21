from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required

from WebsiteTimViecLam.HeThongTimViecLam import app, db, dao, Login

from WebsiteTimViecLam.HeThongTimViecLam.dao import loadTinTuyenDung, ungTuyen, get_cap_bac, get_chuyen_nganh, \
    get_loai_cong_viec
from WebsiteTimViecLam.HeThongTimViecLam.decorater import annonymous_user
from WebsiteTimViecLam.HeThongTimViecLam.models import HoSoXinViec


@Login.user_loader #Nhiem vu,Tacdung ?
def get_user(user_id):
    return dao.get_user_by_ID(user_id)

@app.route("/")
def index():
    ten_ntd=request.args.get('ten_ntd')
    tintuyendung = loadTinTuyenDung(ten_ntd=ten_ntd)
    return  render_template("index.html",ttd=tintuyendung)

@app.route("/hoso")
@login_required
def view_hoso():
    from WebsiteTimViecLam.HeThongTimViecLam import dao
    ho_sos = dao.get_hoso_by_current_user()
    return render_template("hoso.html", ho_sos=ho_sos)

@app.route("/taocv", methods=["GET", "POST"])
@login_required
def tao_cv_route():
    capbac=get_cap_bac()
    chuyennganh=get_chuyen_nganh()
    loaicv=get_loai_cong_viec()
    if request.method == "POST":
        hs = dao.tao_cv(
            ten_hs=request.form.get("ten_hs"),
            ma_uv=current_user.id,
            muc_tieu=request.form.get("muc_tieu_nghe_nghiep"),
            kinh_nghiem=request.form.get("kinh_nghiem"),
            ky_nang=request.form.get("ky_nang"),
            hoc_van=request.form.get("hoc_van"),
            file=request.files.get("file_cv")
        )
        flash("Tạo CV thành công!", "success")
        return redirect(url_for("tao_cv_route"))

    return render_template("taocv.html",chuyen_nganhs=chuyennganh,loai_cvs=loaicv,cap_bacs=capbac)


@app.route("/ungtuyen/<int:ma_ttd>", methods=["GET", "POST"])
@login_required
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
@login_required
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

@app.route("/register", methods=['GET', 'POST'])
@annonymous_user
def register_process():
    err_msg = None
    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        avatar = request.files.get('avatar')

        if password != confirm:
            err_msg = 'Mật khẩu không khớp!'
        else:
            try:
                from WebsiteTimViecLam.HeThongTimViecLam import dao
                dao.add_user(name=name, username=username, email=email,
                             password=password, avatar=avatar)
                return redirect('/login')
            except Exception as ex:
                err_msg = f'Đăng ký thất bại: {str(ex)}'

    return render_template('register.html', err_msg=err_msg)


if __name__=="__main__":
    with app.app_context():
        app.run(debug=True, port=5000)