from WebsiteTimViecLam.HeThongTimViecLam.models import HoSoXinViec,LoaiCongViec,CapBac,ChuyenNganh,DiaChi,MucLuong,NhaTuyenDung,TinTuyenDung,UngTuyen,UngVien,TaiKhoan
from flask_login import current_user
from WebsiteTimViecLam.HeThongTimViecLam import app,db
import hashlib
import cloudinary
import cloudinary.uploader
from sqlalchemy import func
from datetime import datetime

def loadTinTuyenDung(id=None,page=1):
    query=TinTuyenDung.query

    page_size=app.config["PAGE_SIZE"]
    start = (page - 1) * page_size
    query = query.slice(start, start + page_size)

    return query.all()

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

def ungTuyen(ma_ttd, ma_hoso=None, cv_url=None):
    try:
        if not current_user.is_authenticated:
            return None

        ung_tuyen = UngTuyen(
            ma_uv=current_user.id,
            ma_ttd=ma_ttd,
            ma_hoso=ma_hoso,
            cv=cv_url,
            ngay_nop=datetime.now()
        )

        db.session.add(ung_tuyen)
        db.session.commit()

        return ung_tuyen
    except Exception as ex:
        db.session.rollback()
        print(f"Lỗi khi ứng tuyển: {ex}")
        return None

