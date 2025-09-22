from flask import Flask, render_template, request, redirect, url_for, flash,jsonify
from flask_login import login_user, logout_user, current_user, login_required

from WebsiteTimViecLam.HeThongTimViecLam import app, db, dao, Login

from WebsiteTimViecLam.HeThongTimViecLam.dao import loadTinTuyenDung,ungTuyen
from WebsiteTimViecLam.HeThongTimViecLam.decorater import annonymous_user
from WebsiteTimViecLam.HeThongTimViecLam.models import *
from datetime import datetime



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
        role = request.form.get("role")  # lấy role từ form

        u = dao.auth_user(username=username, password=password, role=role)
        if u:
            login_user(u)

            # Điều hướng theo role
            if u.loai_tai_khoan == "ungvien":
                return redirect(url_for("index"))  # hoặc "/"
            elif u.loai_tai_khoan == "nhatuyendung":
                return redirect(url_for("nhatuyendung_dashboard"))
            elif u.loai_tai_khoan == "admin":
                return redirect(url_for("admin_dashboard"))
            else:
                return redirect(url_for("index"))
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
@app.route("/nhatuyendungdashboard")
@login_required
def nhatuyendung_dashboard():
    chuyen_nganhs = ChuyenNganh.query.all()
    loai_congviecs = LoaiCongViec.query.all()
    cap_bacs = CapBac.query.all()
    muc_luongs = MucLuong.query.all()

    danh_sach_tin = TinTuyenDung.query.filter_by(ma_ntd=current_user.id).all()

    tong_tin = len(danh_sach_tin)
    tong_ung_vien = sum(len(t.ung_tuyen) for t in danh_sach_tin)
    tin_dang_hoat_dong = len([t for t in danh_sach_tin if t.trang_thai])

    return render_template("nhatuyendung/nhatuyendung_dashboard.html",
                           chuyen_nganhs=chuyen_nganhs,
                           loai_congviecs=loai_congviecs,
                           cap_bacs=cap_bacs,
                           muc_luongs=muc_luongs,
                           danh_sach_tin=danh_sach_tin,
                           tong_tin=tong_tin,
                           tong_ung_vien=tong_ung_vien,
                           tin_dang_hoat_dong=tin_dang_hoat_dong)


@app.route("/nhatuyendung/dangtin", methods=["POST"])
@login_required
def dang_tin_tuyen_dung():
    ten_cong_viec = request.form.get("ten_cong_viec")
    dia_chi = request.form.get("dia_chi_lam_viec")
    so_luong = request.form.get("so_luong")
    gioi_tinh_yc = request.form.get("gioi_tinh_yc")
    mo_ta = request.form.get("mo_ta")
    yeu_cau = request.form.get("yeu_cau")
    ky_nang = request.form.get("ky_nang_lien_quan")
    quyen_loi = request.form.get("quyen_loi")
    han_nop = request.form.get("han_nop")

    ma_cn = request.form.get("ma_cn")
    ma_loai_cv = request.form.get("ma_loai_cv")
    ma_cap_bac = request.form.get("ma_cap_bac")
    ma_muc_luong = request.form.get("ma_muc_luong")

    result = dao.add_job_post(
        ma_ntd=current_user.id,
        ten_cong_viec=ten_cong_viec,
        dia_chi=dia_chi,
        so_luong=int(so_luong) if so_luong else None,
        gioi_tinh_yc=gioi_tinh_yc,
        ma_cn=int(ma_cn) if ma_cn else None,
        ma_loai_cv=int(ma_loai_cv) if ma_loai_cv else None,
        ma_cap_bac=int(ma_cap_bac) if ma_cap_bac else None,
        ma_muc_luong=int(ma_muc_luong) if ma_muc_luong else None,
        mo_ta=mo_ta,
        yeu_cau=yeu_cau,
        ky_nang=ky_nang,
        quyen_loi=quyen_loi,
        han_nop=datetime.strptime(han_nop, "%Y-%m-%d")
    )
    if result:
        flash("Đăng tin thành công!", "success")
    else:
        flash("Đăng tin thất bại!", "danger")

    return redirect(url_for("nhatuyendung_dashboard"))


@app.route("/nhatuyendung/xoa/<int:ma_ttd>", methods=["DELETE"])
@login_required
def xoa_tin_tuyen_dung(ma_ttd):
    try:
        tin = TinTuyenDung.query.get(ma_ttd)

        if not tin:
            flash("Tin tuyển dụng không tồn tại!", "danger")
            return redirect(url_for("nhatuyendung_dashboard"))

        # Chỉ NTD chủ tin mới được xóa
        if tin.ma_ntd != current_user.id:
            flash("Bạn không có quyền xóa tin này!", "danger")
            return redirect(url_for("nhatuyendung_dashboard"))

        db.session.delete(tin)
        db.session.commit()
        flash("Đã xóa tin tuyển dụng!", "success")

    except Exception as ex:
        db.session.rollback()
        flash(f"Lỗi khi xóa tin: {str(ex)}", "danger")

    return redirect(url_for("nhatuyendung_dashboard"))



@app.route("/nhatuyendung/pheduyet/<int:ma_ut>", methods=["POST"])
@login_required
def phe_duyet_ung_vien(ma_ut):
    # Kiểm tra quyền
    ut = UngTuyen.query.get(ma_ut)
    if not ut:
        flash("Ứng tuyển không tồn tại!", "danger")
        return redirect(url_for("nhatuyendung_dashboard"))
    if ut.tin_tuyen_dung.ma_ntd != current_user.id:
        flash("Bạn không có quyền phê duyệt ứng viên này!", "danger")
        return redirect(url_for("nhatuyendung_dashboard"))
    result = dao.cap_nhat_trang_thai_ung_tuyen(ma_ut, "Phê duyệt")

    if result:
        flash("Đã phê duyệt ứng viên!", "success")
    else:
        flash("Lỗi khi phê duyệt ứng viên!", "danger")

    return redirect(url_for("nhatuyendung_dashboard"))


@app.route("/nhatuyendung/tuchoi/<int:ma_ut>", methods=["POST"])
@login_required
def tu_choi_ung_vien(ma_ut):
    ut = UngTuyen.query.get(ma_ut)
    if not ut:
        flash("Ứng tuyển không tồn tại!", "danger")
        return redirect(url_for("nhatuyendung_dashboard"))
    if ut.tin_tuyen_dung.ma_ntd != current_user.id:
        flash("Bạn không có quyền từ chối ứng viên này!", "danger")
        return redirect(url_for("nhatuyendung_dashboard"))
    result = dao.cap_nhat_trang_thai_ung_tuyen(ma_ut, "Từ chối")

    if result:
        flash("Đã từ chối ứng viên!", "info")
    else:
        flash("Lỗi khi từ chối ứng viên!", "danger")

    return redirect(url_for("nhatuyendung_dashboard"))

@app.route("/nhatuyendung/<int:ma_ttd>/ungvien")
@login_required
def api_ds_ung_vien(ma_ttd):
    tin = TinTuyenDung.query.get(ma_ttd)
    if not tin:
        return jsonify([])  # tin không tồn tại

    if tin.ma_ntd != current_user.id:
        return jsonify([])  # không có quyền xem

    ds = []
    for ut in tin.ung_tuyen:
        ds.append({
            "id": ut.id,
            "ten_uv": ut.ung_vien.ten_uv,
            "email": ut.ung_vien.email,
            "link_cv": ut.link_cv,
            "ngay_ung_tuyen": ut.ngay_ung_tuyen.strftime("%d/%m/%Y"),
            "trang_thai": ut.trang_thai or "Đang chờ"
        })

    return jsonify(ds)


@app.route("/admindashboard")
def admin_dashboard():
    return render_template("admin_dashboard.html")




if __name__=="__main__":
    with app.app_context():
        app.run(debug=True, port=5000)