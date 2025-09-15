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

def ungTuyen(ma_ttd, file=None):
    try:
        # if not current_user.is_authenticated:
        #     print("Người dùng chưa đăng nhập.")
        #     return None

        cv_url = None
        if file:
            # Upload file PDF lên Cloudinary
            upload_result = cloudinary.uploader.upload(
                file,
                folder="cv_uploads",
                resource_type="raw"   # bắt buộc để nhận PDF, DOCX...
            )
            cv_url = upload_result["secure_url"]

        # Tạo bản ghi ứng tuyển
        ung_tuyen = UngTuyen(
            # ma_uv=current_user.id, dùng dòng này sau khi có login
            ma_uv=1,
            ma_ttd=ma_ttd,
            link_cv=cv_url,
            ngay_ung_tuyen=datetime.now()
        )

        db.session.add(ung_tuyen)
        db.session.commit()

        print("Ứng tuyển thành công!")
        return ung_tuyen

    except Exception as ex:
        db.session.rollback()
        print(f"Lỗi khi ứng tuyển: {ex}")
        return None

