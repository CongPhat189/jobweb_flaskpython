from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, Blueprint, session
from flask_login import login_user, logout_user, current_user, login_required


from WebsiteTimViecLam.HeThongTimViecLam import app, db, dao, Login, oauth

from WebsiteTimViecLam.HeThongTimViecLam.dao import loadTinTuyenDung, ungTuyen, get_cap_bac, get_chuyen_nganh, \
    get_loai_cong_viec
from WebsiteTimViecLam.HeThongTimViecLam.decorater import annonymous_user
from WebsiteTimViecLam.HeThongTimViecLam.models import *
from datetime import datetime
import hmac, hashlib, json, requests
from sqlalchemy import extract, func

# # ==== GOOGLE LOGIN ====
@app.route("/login/google")
def login_google():
    redirect_uri = url_for("authorize_google", _external=True)
    print("Redirect URI:", redirect_uri)
    return oauth.google.authorize_redirect(redirect_uri)



@app.route("/authorize/google")
def authorize_google():
    # Lấy token từ Google
    token = oauth.google.authorize_access_token()
    resp = oauth.google.get("userinfo")
    info = resp.json()

    email = info.get("email")
    google_id = info.get("id")
    name = info.get("name") or email.split("@")[0]  # fallback tên

    # Tìm user trong DB
    user = TaiKhoan.query.filter_by(email=email).first()

    if not user:
        # Nếu chưa tồn tại → tạo mới TaiKhoan
        user = UngVien(
            username=email.split("@")[0],
            email=email,
            google_id=google_id,
            ten_uv=name,
            mat_khau=None,
            loai_tai_khoan="ungvien",
            ngay_tao=datetime.now()
        )
        db.session.add(user)
        db.session.commit()
    else:
        # Nếu có rồi mà chưa có google_id thì cập nhật
        if not user.google_id:
            user.google_id = google_id
            db.session.commit()

    # Đăng nhập với Flask-Login
    login_user(user)
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))  # index là trang chủ, bạn thay theo route của mình

@Login.user_loader #Nhiem vu,Tacdung ?
def get_user(user_id):
    return dao.get_user_by_ID(user_id)

@app.template_filter("from_json")
def from_json_filter(value):
    try:
        return json.loads(value) if value else {}
    except Exception:
        return {}

@app.route("/")
def index():
    keyword = request.args.get("keyword")
    ma_cn = request.args.get("ma_cn", type=int)
    ma_loai_cv = request.args.get("ma_loai_cv", type=int)
    ma_cap_bac = request.args.get("ma_cap_bac", type=int)
    ma_muc_luong = request.args.get("ma_muc_luong", type=int)
    ma_dia_chi = request.args.get("ma_dia_chi")

    tintuyendung = dao.loadTinTuyenDung(
        keyword=keyword,
        ma_cn=ma_cn,
        ma_loai_cv=ma_loai_cv,
        ma_cap_bac=ma_cap_bac,
        ma_muc_luong=ma_muc_luong,
        ma_dia_chi=ma_dia_chi,
        only_active=True
    )

    return render_template(
        "index.html",
        ttd=tintuyendung,
        chuyen_nganhs=dao.get_chuyen_nganh(),
        loai_cvs=dao.get_loai_cong_viec(),
        cap_bacs=dao.get_cap_bac(),
        muc_luongs=MucLuong.query.all(),
        dia_chis=DiaChi.query.all()
    )



@app.route("/hoso")
@login_required
def view_hoso():
    from WebsiteTimViecLam.HeThongTimViecLam import dao
    ho_sos = dao.get_hoso_by_current_user()
    return render_template("hoso.html", ho_sos=ho_sos)




@app.route("/ungtuyen/<int:ma_ttd>", methods=["GET", "POST"])
@login_required
def ung_tuyen(ma_ttd):
    tin = TinTuyenDung.query.get(ma_ttd)
    if not tin:
        flash("Tin tuyển dụng không tồn tại!", "apply_error")
        return redirect(url_for("index"))

    if request.method == "POST":
        apply_type = request.form.get("apply_type")

        result = None
        if apply_type == "upload":  # Cách 1: upload CV
            file = request.files.get("file")
            if not file or not file.filename.endswith(".pdf"):
                flash("Vui lòng upload CV định dạng PDF!", "apply_error")
                return redirect(url_for("ung_tuyen", ma_ttd=ma_ttd))

            result = dao.ungTuyen(ma_ttd=ma_ttd, ma_uv=current_user.id, file=file)

        elif apply_type == "hoso":  # Cách 2: chọn hồ sơ hệ thống
            ma_hs = request.form.get("ma_hs")
            if not ma_hs:
                flash("Vui lòng chọn hồ sơ!", "apply_error")
                return redirect(url_for("ung_tuyen", ma_ttd=ma_ttd))

            result = dao.ungTuyen(ma_ttd=ma_ttd, ma_uv=current_user.id, ma_hs=int(ma_hs))

        if result:
            flash("Ứng tuyển thành công!", "apply_success")
        else:
            flash("Ứng tuyển thất bại. Vui lòng thử lại.", "apply_error")

        return redirect(url_for("ung_tuyen", ma_ttd=ma_ttd))

    # GET: load danh sách hồ sơ ứng viên
    ho_sos = HoSoXinViec.query.filter_by(ma_uv=current_user.id).all()
    return render_template("ungtuyen.html", tin=tin, ho_sos=ho_sos)




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

    job = dao.add_job_post(
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

    if job:
        if job.trang_thai:
            # tin đầu tiên: active ngay
            flash("Đăng tin thành công (miễn phí lần đầu)!", "success")
            return redirect(url_for("nhatuyendung_dashboard"))
        else:
            # tin thứ 2 trở đi: cần thanh toán
            giao_dich = GiaoDich.query.filter_by(ma_ttd=job.id, ma_ntd=current_user.id).first()
            if giao_dich:
                flash("Bạn cần thanh toán 10.000đ để kích hoạt tin này!", "warning")
                return redirect(url_for("momo_pay", giaodich_id=giao_dich.id))
            else:
                flash("Không tìm thấy giao dịch cho tin này!", "danger")
                return redirect(url_for("nhatuyendung_dashboard"))
    else:
        flash("Đăng tin thất bại!", "danger")
        return redirect(url_for("nhatuyendung_dashboard"))



@app.route("/momo/pay/<int:giaodich_id>")
@login_required
def momo_pay(giaodich_id):
    gd = GiaoDich.query.get(giaodich_id)
    if not gd or gd.ma_ntd != current_user.id:
        flash("Giao dịch không tồn tại hoặc không hợp lệ!", "danger")
        return redirect(url_for("nhatuyendung_dashboard"))

    endpoint = app.config['MOMO_ENDPOINT']
    partnerCode = app.config['MOMO_PARTNER_CODE']
    accessKey = app.config['MOMO_ACCESS_KEY']
    secretKey = app.config['MOMO_SECRET_KEY']

    requestId = gd.request_id
    orderId = gd.order_id
    orderInfo = gd.noi_dung
    amount = str(gd.so_tien)
    returnUrl = app.config['MOMO_RETURN_URL']
    notifyUrl = app.config['MOMO_NOTIFY_URL']
    extraData = ""

    raw_signature = f"accessKey={accessKey}&amount={amount}&extraData={extraData}&ipnUrl={notifyUrl}&orderId={orderId}&orderInfo={orderInfo}&partnerCode={partnerCode}&redirectUrl={returnUrl}&requestId={requestId}&requestType=captureWallet"

    h = hmac.new(secretKey.encode("utf-8"), raw_signature.encode("utf-8"), hashlib.sha256)
    signature = h.hexdigest()

    data = {
        'partnerCode': partnerCode,
        'accessKey': accessKey,
        'requestId': requestId,
        'amount': amount,
        'orderId': orderId,
        'orderInfo': orderInfo,
        'redirectUrl': returnUrl,
        'ipnUrl': notifyUrl,
        'extraData': extraData,
        'requestType': 'captureWallet',
        'signature': signature,
        'lang': 'vi'
    }

    res = requests.post(endpoint, json=data)
    result = res.json()

    if result.get("payUrl"):
        return redirect(result["payUrl"])
    else:
        flash("Không thể tạo thanh toán MoMo", "danger")
        return redirect(url_for("nhatuyendung_dashboard"))

@app.route("/momo/return")
def momo_return():
    result = request.args.to_dict()
    orderId = result.get("orderId")
    gd = GiaoDich.query.filter_by(order_id=orderId).first()

    if result.get("resultCode") == "0":  # 0 = thành công
        gd.trang_thai = "Thành công"
        # Mở tin tuyển dụng
        if gd.ma_ttd:
            tin = TinTuyenDung.query.get(gd.ma_ttd)
            if tin:
                tin.trang_thai = True
        db.session.commit()
        flash("Thanh toán thành công, tin đã được kích hoạt!", "success")
    else:
        gd.trang_thai = "Thất bại"
        db.session.commit()
        flash("Thanh toán thất bại!", "danger")

    return redirect(url_for("nhatuyendung_dashboard"))
@app.route("/momo/notify", methods=["POST"])
def momo_notify():
    data = request.json
    orderId = data.get("orderId")
    gd = GiaoDich.query.filter_by(order_id=orderId).first()

    if not gd:
        return jsonify({"message": "Order not found"}), 404

    if data.get("resultCode") == 0:
        gd.trang_thai = "Thành công"
        if gd.ma_ttd:
            tin = TinTuyenDung.query.get(gd.ma_ttd)
            if tin:
                tin.trang_thai = True
    else:
        gd.trang_thai = "Thất bại"

    db.session.commit()
    return jsonify({"message": "OK"}), 200



@app.route("/nhatuyendung/xoa/<int:ma_ttd>", methods=["POST"])
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

    # chỉ cho phép đúng nhà tuyển dụng xem
    if tin.ma_ntd != current_user.id:
        return jsonify([])

    ds = []
    for ut in tin.ung_tuyen:
        ds.append({
            "id": ut.id,
            "ten_uv": ut.ung_vien.ten_uv,
            "email": ut.ung_vien.tai_khoan.email if ut.ung_vien and ut.ung_vien.tai_khoan else None,
            # Ưu tiên lấy file_cv từ hồ sơ, nếu không có thì lấy link_cv upload
            "link_cv": ut.ho_so.file_cv if ut.ma_hs and ut.ho_so else ut.link_cv,
            "ma_hs": ut.ma_hs,
            "ngay_ung_tuyen": ut.ngay_ung_tuyen.strftime("%d/%m/%Y") if ut.ngay_ung_tuyen else None,
            "trang_thai": ut.trang_thai or "Đang chờ"
        })

    return jsonify(ds)


@app.route("/api/thongke/ungtuyen")
@login_required
def api_thongke_ungtuyen():
    month = int(request.args.get("month", datetime.now().month))
    year = int(request.args.get("year", datetime.now().year))

    # Lấy 3 tháng: tháng chọn và 2 tháng trước
    months = []
    for i in range(2, -1, -1):
        m = month - i
        y = year
        if m <= 0:  # lùi sang năm trước
            m += 12
            y -= 1
        months.append((m, y))

    data = []
    for m, y in months:
        count = db.session.query(func.count(UngTuyen.id))\
            .join(TinTuyenDung)\
            .filter(
                extract('month', UngTuyen.ngay_ung_tuyen) == m,
                extract('year', UngTuyen.ngay_ung_tuyen) == y,
                TinTuyenDung.ma_ntd == current_user.id
            ).scalar() or 0
        data.append({"month": m, "year": y, "count": count})

    return jsonify(data)

@app.route("/api/thongke/tongquan")
@login_required
def api_thongke_tongquan():
    month = int(request.args.get("month"))
    year = int(request.args.get("year"))

    # Tổng tin đã đăng trong tháng
    tong_tin = db.session.query(func.count(TinTuyenDung.id))\
        .filter(
            extract('month', TinTuyenDung.ngay_dang) == month,
            extract('year', TinTuyenDung.ngay_dang) == year,
            TinTuyenDung.ma_ntd == current_user.id
        ).scalar() or 0

    # Tổng lượt ứng tuyển trong tháng
    tong_ung_vien = db.session.query(func.count(UngTuyen.id))\
        .join(TinTuyenDung)\
        .filter(
            extract('month', UngTuyen.ngay_ung_tuyen) == month,
            extract('year', UngTuyen.ngay_ung_tuyen) == year,
            TinTuyenDung.ma_ntd == current_user.id
        ).scalar() or 0

    # Số tin đang hoạt động trong tháng
    tin_dang_hoat_dong = db.session.query(func.count(TinTuyenDung.id))\
        .filter(
            extract('month', TinTuyenDung.ngay_dang) == month,
            extract('year', TinTuyenDung.ngay_dang) == year,
            TinTuyenDung.ma_ntd == current_user.id,
            TinTuyenDung.trang_thai == True
        ).scalar() or 0

    return jsonify({
        "tong_tin": tong_tin,
        "tong_ung_vien": tong_ung_vien,
        "tin_dang_hoat_dong": tin_dang_hoat_dong
    })


# Decorator kiểm tra quyền admin
def admin_required(fn):
    from functools import wraps
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.loai_tai_khoan != 'admin':
            flash("Bạn không có quyền truy cập trang quản trị!", "danger")
            return redirect(url_for("index"))
        return fn(*args, **kwargs)
    return wrapper

# Trang Admin Dashboard
@app.route("/admin")
@login_required
@admin_required
def admin_dashboard():
    # Render trước một ít data để có bảng danh mục & bảng job/account
    danh_sach_tin = dao.admin_list_all_jobs()
    danh_sach_tai_khoan = dao.admin_list_accounts()

    # Danh mục
    d_diachi = dao.admin_list_category(DiaChi)
    d_capbac = dao.admin_list_category(CapBac)
    d_mucluong = dao.admin_list_category(MucLuong)
    d_chuyennganh = dao.admin_list_category(ChuyenNganh)
    d_loaicv = dao.admin_list_category(LoaiCongViec)

    now = datetime.datetime.now()
    return render_template(
        "admin/admin_dashboard.html",
        danh_sach_tin=danh_sach_tin,
        danh_sach_tai_khoan=danh_sach_tai_khoan,
        diachis=d_diachi,
        capbacs=d_capbac,
        mucluongs=d_mucluong,
        chuyennganhs=d_chuyennganh,
        loaicvs=d_loaicv,
        current_month=now.month,
        current_year=now.year
    )

# API: Doanh thu MoMo theo tháng (tất cả tháng có giao dịch)
@app.route("/api/admin/doanhthu")
@login_required
@admin_required
def api_admin_doanhthu():
    data = dao.admin_doanhthu_momo_group_by_month()
    return jsonify(data)

# API: Lượt ứng tuyển theo ngành (trong tháng/year)
@app.route("/api/admin/ungtuyen-nganh")
@login_required
@admin_required
def api_admin_ungtuyen_nganh():
    try:
        month = int(request.args.get("month"))
        year = int(request.args.get("year"))
    except:
        now = datetime.datetime.now()
        month, year = now.month, now.year
    data = dao.admin_ungtuyen_theo_nganh(month, year)
    return jsonify(data)

# Toggle tin (ẩn/hiện)
@app.route("/admin/tin/<int:ma_ttd>/toggle", methods=["POST"])
@login_required
@admin_required
def admin_toggle_tin(ma_ttd):
    status = dao.admin_toggle_job(ma_ttd)
    if status is None:
        return jsonify({"error": "Không tìm thấy tin"}), 404
    return jsonify({"status": "success", "trang_thai": bool(status)})

# Toggle tài khoản (khóa/mở)
@app.route("/admin/tai-khoan/<int:user_id>/toggle", methods=["POST"])
@login_required
@admin_required
def admin_toggle_taikhoan(user_id):
    status = dao.admin_toggle_account(user_id)
    if status is None:
        return jsonify({"error": "Không tìm thấy tài khoản"}), 404
    return jsonify({"status": "success", "trang_thai": bool(status)})

# ==== CRUD Danh mục (gom chung) ====
# Map entity -> (Model, field_name)
CATEGORY_MAP = {
    "diachi": (DiaChi, "ten_dia_chi"),
    "capbac": (CapBac, "ten_cap_bac"),
    "mucluong": (MucLuong, "ten_muc_luong"),
    "chuyennganh": (ChuyenNganh, "ten_cn"),
    "loaicongviec": (LoaiCongViec, "ten_loai_cv"),
}

@app.route("/admin/category/<string:entity>/create", methods=["POST"])
@login_required
@admin_required
def admin_category_create(entity):
    model, field = CATEGORY_MAP.get(entity, (None, None))
    if not model:
        return jsonify({"error": "Danh mục không hợp lệ"}), 400
    value = request.form.get("value")
    if not value or not value.strip():
        return jsonify({"error": "Giá trị không hợp lệ"}), 400
    obj = dao.admin_add_category(model, field, value)
    return jsonify({"id": obj.id, "value": getattr(obj, field)})

@app.route("/admin/category/<string:entity>/<int:pk>/update", methods=["POST"])
@login_required
@admin_required
def admin_category_update(entity, pk):
    model, field = CATEGORY_MAP.get(entity, (None, None))
    if not model:
        return jsonify({"error": "Danh mục không hợp lệ"}), 400
    value = request.form.get("value")
    obj = dao.admin_update_category(model, pk, field, value)
    if not obj:
        return jsonify({"error": "Không tìm thấy bản ghi"}), 404
    return jsonify({"id": obj.id, "value": getattr(obj, field)})

@app.route("/admin/category/<string:entity>/<int:pk>/delete", methods=["POST"])
@login_required
@admin_required
def admin_category_delete(entity, pk):
    model, field = CATEGORY_MAP.get(entity, (None, None))
    if not model:
        return jsonify({"error": "Danh mục không hợp lệ"}), 400
    ok = dao.admin_delete_category(model, pk)
    if not ok:
        return jsonify({"error": "Không tìm thấy bản ghi"}), 404
    return jsonify({"status": "deleted"})
@app.route("/admin/tin/<int:ma_ttd>")
@login_required
@admin_required
def admin_view_tin(ma_ttd):
    tin = TinTuyenDung.query.get(ma_ttd)
    if not tin:
        flash("Tin tuyển dụng không tồn tại!", "danger")
        return redirect(url_for("admin_dashboard"))

    return render_template("admin/admin_tin_detail.html", tin=tin)




@app.route("/taocv", methods=["GET", "POST"])
@login_required
def tao_cv_route():
    if request.method == "POST":
        full_name = request.form.get("full_name")
        title = request.form.get("title")
        address = request.form.get("address")
        phone = request.form.get("phone")
        email = request.form.get("email")
        summary = request.form.get("summary")

        # skills
        skills = {
            "Programming Languages": request.form.get("skills_programming"),
            "Frontend": request.form.get("skills_frontend"),
            "Backend": request.form.get("skills_backend"),
            "Deployment": request.form.get("skills_deployment"),
            "Database": request.form.get("skills_database"),
            "Version Control": request.form.get("skills_version_control"),
        }

        education = request.form.get("education")

        # projects (list)
        project_titles = request.form.getlist("project_title[]")
        project_descs = request.form.getlist("project_desc[]")
        project_techs = request.form.getlist("project_tech[]")
        project_links = request.form.getlist("project_link[]")

        projects = []
        for i in range(len(project_titles)):
            if project_titles[i].strip():
                projects.append({
                    "name": project_titles[i],
                    "desc": project_descs[i],
                    "tech": project_techs[i],
                    "github": project_links[i],
                    "time": ""  # có thể cho người dùng nhập thêm
                })

        # gọi dao để tạo cv
        hs = dao.tao_cv(
            ten_uv=full_name,
            title=title,
            dia_chi=address,
            phone=phone,
            email=email,
            muc_tieu=summary,
            ky_nang=skills,
            hoc_van=education,
            projects=projects
        )

        flash("Tạo CV thành công!", "success")
        return redirect("/hoso")

    return render_template("taocv.html")

@app.route("/suacv/<int:cv_id>", methods=["GET", "POST"])
@login_required
def sua_cv_route(cv_id):
    cv = HoSoXinViec.query.get_or_404(cv_id)

    try:
        cv.ky_nang = json.loads(cv.ky_nang) if cv.ky_nang else []
    except Exception:
        cv.ky_nang = []

    if request.method == "POST":
        full_name = request.form.get("full_name")
        title = request.form.get("title")
        address = request.form.get("address")
        phone = request.form.get("phone")
        email = request.form.get("email")
        summary = request.form.get("summary")

        skills = {
            "Programming Languages": request.form.get("skills_programming"),
            "Frontend": request.form.get("skills_frontend"),
            "Backend": request.form.get("skills_backend"),
            "Deployment": request.form.get("skills_deployment"),
            "Database": request.form.get("skills_database"),
            "Version Control": request.form.get("skills_version_control"),
        }

        education = request.form.get("education")

        project_titles = request.form.getlist("project_title[]")
        project_descs = request.form.getlist("project_desc[]")
        project_techs = request.form.getlist("project_tech[]")
        project_links = request.form.getlist("project_link[]")

        projects = []
        for i in range(len(project_titles)):
            if project_titles[i].strip():
                projects.append({
                    "name": project_titles[i],
                    "desc": project_descs[i],
                    "tech": project_techs[i],
                    "github": project_links[i],
                    "time": ""
                })


        dao.sua_cv(
            cv_id=cv_id,
            ten_uv=full_name,
            title=title,
            dia_chi=address,
            phone=phone,
            email=email,
            muc_tieu=summary,
            ky_nang=skills,
            hoc_van=education,
            projects=projects
        )

        flash("Cập nhật CV thành công!", "success")
        return redirect(url_for("view_hoso", cv_id=cv_id))

    # truyền dữ liệu CV sang template
    return render_template("suacv.html", cv=cv)




if __name__=="__main__":
    with app.app_context():
        app.run(debug=True, port=5000)


