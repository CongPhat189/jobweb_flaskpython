import uuid

from WebsiteTimViecLam.HeThongTimViecLam.models import *
from flask_login import current_user
from WebsiteTimViecLam.HeThongTimViecLam import app, db
import hashlib
import cloudinary
import cloudinary.uploader
from datetime import datetime
from sqlalchemy import func, extract



def auth_user(username, password, role=None):
    mat_khau = hashlib.md5(password.encode("utf-8")).hexdigest()
    query = TaiKhoan.query.filter(
        TaiKhoan.username == username,
        TaiKhoan.mat_khau == mat_khau
    )
    if role:
        query = query.filter(TaiKhoan.loai_tai_khoan == role.lower())
    return query.first()


def get_user_by_ID(id):
    return TaiKhoan.query.get(id)

def get_applied_jobs(ma_uv):
    print(ma_uv)
    return (db.session.query(TinTuyenDung)
            .join(UngTuyen, TinTuyenDung.id == UngTuyen.ma_ttd)
            .filter(UngTuyen.ma_uv == ma_uv)
            .all())



def add_user(name, username, email, password, role="ungvien", avatar=None,
             so_dien_thoai=None, ngay_sinh=None, so_thich=None, dia_chi=None):
    mat_khau = hashlib.md5(password.encode("utf-8")).hexdigest()
    avatar_url = None
    if avatar:
        res = cloudinary.uploader.upload(avatar)
        avatar_url = res.get("secure_url")

    if role.lower() == "ungvien":
        user = UngVien(
            username=username,
            email=email,
            mat_khau=mat_khau,
            ten_uv=name,
            so_dien_thoai=so_dien_thoai,
            ngay_sinh=ngay_sinh,
            so_thich=so_thich,
            dia_chi=dia_chi,
            anh_dai_dien=avatar_url
        )
    elif role.lower() == "nhatuyendung":
        user = NhaTuyenDung(
            username=username,
            email=email,
            mat_khau=mat_khau,
            ten_ntd=name,
            so_dien_thoai=so_dien_thoai,
            dia_chi=dia_chi,
            anh_dai_dien=avatar_url
        )
    else:
        raise ValueError("Role không hợp lệ")

    db.session.add(user)
    db.session.commit()
    return user


def loadTinTuyenDung(
    id=None, page=1,
    keyword=None,   # tìm kiếm
    ma_cn=None, ma_loai_cv=None, ma_cap_bac=None, ma_muc_luong=None, ma_dia_chi=None,
    only_active=True
):
    query = TinTuyenDung.query

    # chỉ lấy tin còn hoạt động
    if only_active:
        query = query.filter(TinTuyenDung.trang_thai == True)

    # tìm kiếm theo keyword (tên công việc hoặc tên NTD)
    if keyword:
        query = query.join(NhaTuyenDung).filter(
            (TinTuyenDung.ten_cong_viec.ilike(f"%{keyword}%")) |
            (NhaTuyenDung.ten_ntd.ilike(f"%{keyword}%"))
        )

    # lọc theo danh mục
    if ma_cn:
        query = query.filter(TinTuyenDung.ma_cn == ma_cn)
    if ma_loai_cv:
        query = query.filter(TinTuyenDung.ma_loai_cv == ma_loai_cv)
    if ma_cap_bac:
        query = query.filter(TinTuyenDung.ma_cap_bac == ma_cap_bac)
    if ma_muc_luong:
        query = query.filter(TinTuyenDung.ma_muc_luong == ma_muc_luong)
    if ma_dia_chi:
        query = query.filter(TinTuyenDung.dia_chi_lam_viec.like(f"%{ma_dia_chi}%"))

    if id:
        return query.get(id)

    page_size = app.config["PAGE_SIZE"]
    start = (page - 1) * page_size
    return query.slice(start, start + page_size).all()



def createHoSoXinViec(
        ten_hs,
        ma_cn=None,
        ma_loai_cv=None,
        ma_cap_bac=None,
        muc_tieu=None,
        kinh_nghiem=None,
        ky_nang=None,
        hoc_van=None,
        giai_thuong=None
):
    """
    Hàm tạo hồ sơ xin việc cho ứng viên hiện tại (current_user).
    Trả về HoSoXinViec vừa tạo nếu thành công, None nếu thất bại.
    """
    try:
        # Kiểm tra đăng nhập
        if not current_user.is_authenticated:
            return None

        # Tạo hồ sơ mới
        hoso = HoSoXinViec(
            ten_hs=ten_hs.strip(),
            ma_uv=current_user.id,  # Gán theo user hiện tại
            ma_cn=ma_cn,
            ma_loai_cv=ma_loai_cv,
            ma_cap_bac=ma_cap_bac,
            muc_tieu_nghe_nghiep=muc_tieu,
            kinh_nghiem=kinh_nghiem,
            ky_nang=ky_nang,
            hoc_van=hoc_van,
            giai_thuong=giai_thuong
        )

        db.session.add(hoso)
        db.session.commit()

        return hoso
    except Exception as ex:
        db.session.rollback()
        print(f"Lỗi khi tạo hồ sơ xin việc: {ex}")
        return None

def tao_cv(
        ten_hs,
        ma_uv,
        ma_cn=None,
        ma_loai_cv=None,
        ma_cap_bac=None,
        muc_tieu=None,
        kinh_nghiem=None,
        ky_nang=None,
        hoc_van=None,
        giai_thuong=None,
        file=None
):
    """
    Tạo hồ sơ xin việc (CV) cho ứng viên.
    Upload file CV (PDF) lên Cloudinary, sau đó lưu vào DB.
    Trả về object HoSoXinViec đã được lưu.
    """
    file_url = None
    if file:
        upload_result = cloudinary.uploader.upload(
            file,
            folder="cv_uploads",
            resource_type="raw"  # cho phép PDF/Word
        )
        file_url = upload_result.get("secure_url")

    hs = HoSoXinViec(
        ten_hs=ten_hs,
        ma_uv=ma_uv,
        ma_cn=ma_cn,
        ma_loai_cv=ma_loai_cv,
        ma_cap_bac=ma_cap_bac,
        muc_tieu_nghe_nghiep=muc_tieu,
        kinh_nghiem=kinh_nghiem,
        ky_nang=ky_nang,
        hoc_van=hoc_van,
        giai_thuong=giai_thuong,
        file_cv=file_url
    )

    db.session.add(hs)
    db.session.commit()
    return hs

def ungTuyen(ma_ttd,ma_uv, file=None):
    try:
        # Kiểm tra nếu user hiện tại không phải ứng viên
        if current_user.loai_tai_khoan != "ungvien":
            print("Chỉ ứng viên mới có thể ứng tuyển")
            return None

        # Kiểm tra trùng ứng tuyển
        existing = UngTuyen.query.filter_by(ma_uv=current_user.id, ma_ttd=ma_ttd).first()
        if existing:
            print("Ứng viên đã ứng tuyển tin này rồi.")
            return None

        cv_url = None
        if file:
            try:
                upload_result = cloudinary.uploader.upload(
                    file,
                    folder="cv_uploads",
                    resource_type="raw"  # nhận PDF, DOCX...
                )
                cv_url = upload_result.get("secure_url")
            except Exception as ex:
                print(f"Lỗi upload CV: {ex}")
                return None

        # Tạo bản ghi ứng tuyển
        ung_tuyen = UngTuyen(
            ma_uv=current_user.id,   # dùng id từ current_user (ứng viên)
            ma_ttd=ma_ttd,
            link_cv=cv_url,
            ngay_ung_tuyen=datetime.now(),
            trang_thai="Đang chờ"
        )

        db.session.add(ung_tuyen)
        db.session.commit()
        print("Ứng tuyển thành công!")
        return ung_tuyen

    except Exception as ex:
        db.session.rollback()
        print(f"Lỗi khi ứng tuyển: {ex}")
        return None



# chucnangcuanhatuyendung
def count_job_posts_by_ntd(ma_ntd):
    return TinTuyenDung.query.filter_by(ma_ntd=ma_ntd).count()

def add_job_post(ma_ntd, ten_cong_viec, dia_chi, so_luong, gioi_tinh_yc,
                 ma_cn, ma_loai_cv, ma_cap_bac, ma_muc_luong,
                 mo_ta, yeu_cau, ky_nang, quyen_loi, han_nop):
    try:
        # Kiểm tra số tin đã đăng
        so_tin = count_job_posts_by_ntd(ma_ntd)

        # Nếu là tin đầu tiên -> miễn phí
        if so_tin == 0:
            job = TinTuyenDung(
                ma_ntd=ma_ntd,
                ten_cong_viec=ten_cong_viec,
                dia_chi_lam_viec=dia_chi,
                so_luong=so_luong,
                gioi_tinh_yc=gioi_tinh_yc,
                ma_cn=ma_cn,
                ma_loai_cv=ma_loai_cv,
                ma_cap_bac=ma_cap_bac,
                ma_muc_luong=ma_muc_luong,
                mo_ta=mo_ta,
                yeu_cau=yeu_cau,
                ky_nang_lien_quan=ky_nang,
                quyen_loi=quyen_loi,
                ngay_dang=datetime.now(),
                han_nop=han_nop,
                trang_thai=True
            )
            db.session.add(job)
            db.session.commit()
            return job
        else:
            # Tạo job -> trạng thái chờ thanh toán
            job = TinTuyenDung(
                ma_ntd=ma_ntd,
                ten_cong_viec=ten_cong_viec,
                dia_chi_lam_viec=dia_chi,
                so_luong=so_luong,
                gioi_tinh_yc=gioi_tinh_yc,
                ma_cn=ma_cn,
                ma_loai_cv=ma_loai_cv,
                ma_cap_bac=ma_cap_bac,
                ma_muc_luong=ma_muc_luong,
                mo_ta=mo_ta,
                yeu_cau=yeu_cau,
                ky_nang_lien_quan=ky_nang,
                quyen_loi=quyen_loi,
                ngay_dang=datetime.now(),
                han_nop=han_nop,
                trang_thai=False   # chưa active vì chưa thanh toán
            )
            db.session.add(job)
            db.session.commit()

            # Tạo giao dịch MoMo cho job này
            create_transaction(ma_ntd=ma_ntd, ma_ttd=job.id, so_tien=10000)

            return job
    except Exception as e:
        db.session.rollback()
        print(f"Lỗi khi đăng tin: {e}")
        return None


def create_transaction(ma_ntd, ma_ttd=None, so_tien=10000, noi_dung="Thanh toán đăng tin"):
    try:
        gd = GiaoDich(
            ma_ntd=ma_ntd,
            ma_ttd=ma_ttd,
            so_tien=so_tien,
            noi_dung=noi_dung,
            request_id=str(uuid.uuid4()),
            order_id=str(uuid.uuid4()),
            trang_thai="Chờ xử lý"
        )
        db.session.add(gd)
        db.session.commit()
        return gd
    except Exception as ex:
        db.session.rollback()
        print(f"Lỗi khi tạo giao dịch: {ex}")
        return None

def delete_job_post(ma_ttd, ma_ntd):
    try:
        tin = TinTuyenDung.query.filter_by(id=ma_ttd, ma_ntd=ma_ntd).first()
        if tin:
            db.session.delete(tin)
            db.session.commit()
            return True
        return False
    except Exception as e:
        db.session.rollback()
        print(f"Lỗi xóa tin: {e}")
        return False

def cap_nhat_trang_thai_ung_tuyen(ma_ung_tuyen, trang_thai):
    try:
        ut = UngTuyen.query.get(ma_ung_tuyen)
        if not ut:
            return None

        ut.trang_thai = trang_thai  # "Phê duyệt" hoặc "Từ chối"
        db.session.commit()
        return ut
    except Exception as ex:
        db.session.rollback()
        print("Lỗi cập nhật trạng thái:", ex)
        return None
def get_hoso_by_current_user():
    if not current_user.is_authenticated:
        return None  # Chưa login thì không có hồ sơ

    if current_user.loai_tai_khoan != "ungvien":
        return None  # Chỉ ứng viên mới có hồ sơ

    return HoSoXinViec.query.filter_by(ma_uv=current_user.id).all()

def get_cap_bac():
    return CapBac.query.all()

def get_chuyen_nganh():
    return ChuyenNganh.query.all()

def get_loai_cong_viec():
    return  LoaiCongViec.query.all()


# Chuc nang cua admin

# 1. Doanh thu MoMo theo tháng (group by month/year, chỉ tính giao dịch Thành công)
def admin_doanhthu_momo_group_by_month():
    rows = db.session.query(
        extract('year', GiaoDich.ngay_tao).label('y'),
        extract('month', GiaoDich.ngay_tao).label('m'),
        func.sum(GiaoDich.so_tien).label('total')
    ).filter(GiaoDich.trang_thai == "Thành công") \
     .group_by('y', 'm') \
     .order_by('y', 'm') \
     .all()
    return [{'year': int(y), 'month': int(m), 'total': int(total or 0)} for (y, m, total) in rows]

# 2. Lượt ứng tuyển giữa các ngành theo tháng (tham số month/year)
def admin_ungtuyen_theo_nganh(month: int, year: int):
    rows = db.session.query(
        ChuyenNganh.ten_cn,
        func.count(UngTuyen.id)
    ).join(TinTuyenDung, UngTuyen.ma_ttd == TinTuyenDung.id) \
     .join(ChuyenNganh, TinTuyenDung.ma_cn == ChuyenNganh.id) \
     .filter(
        extract('month', UngTuyen.ngay_ung_tuyen) == month,
        extract('year', UngTuyen.ngay_ung_tuyen) == year
     ).group_by(ChuyenNganh.ten_cn).all()
    return [{'nganh': ten, 'so_luong': int(c or 0)} for (ten, c) in rows]

# 3. Danh sách toàn bộ tin (cho Admin)
def admin_list_all_jobs():
    return db.session.query(TinTuyenDung).join(NhaTuyenDung).order_by(TinTuyenDung.ngay_dang.desc()).all()

# 4. Toggle trạng thái tin (ẩn/hiện)
def admin_toggle_job(ma_ttd: int):
    tin = TinTuyenDung.query.get(ma_ttd)
    if not tin:
        return None
    tin.trang_thai = not bool(tin.trang_thai)
    db.session.commit()
    return tin.trang_thai

# 5. Danh sách tài khoản (ứng viên + NTD), có thể lọc theo role nếu muốn
def admin_list_accounts(role: str = None):
    q = TaiKhoan.query
    if role:
        q = q.filter(TaiKhoan.loai_tai_khoan == role.lower())
    return q.order_by(TaiKhoan.ngay_tao.desc()).all()

# 6. Toggle khóa/mở khóa tài khoản
def admin_toggle_account(user_id: int):
    tk = TaiKhoan.query.get(user_id)
    if not tk:
        return None
    tk.trang_thai = not bool(tk.trang_thai)
    db.session.commit()
    return tk.trang_thai

# 7. CRUD danh mục (chung) – truyền vào model class & tên trường
def admin_list_category(model):
    return model.query.order_by(model.id.desc()).all()

def admin_add_category(model, field_name: str, value: str):
    obj = model()
    setattr(obj, field_name, value.strip())
    db.session.add(obj)
    db.session.commit()
    return obj

def admin_update_category(model, pk: int, field_name: str, value: str):
    obj = model.query.get(pk)
    if not obj:
        return None
    setattr(obj, field_name, value.strip())
    db.session.commit()
    return obj

def admin_delete_category(model, pk: int):
    obj = model.query.get(pk)
    if not obj:
        return False
    db.session.delete(obj)
    db.session.commit()
    return True


