from flask_login import UserMixin

from WebsiteTimViecLam.HeThongTimViecLam import  db,app
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Text, Date, DateTime, Enum
from sqlalchemy.orm import relationship, backref
from datetime import datetime
import hashlib


class DiaChi(db.Model):
    __tablename__ = "tbl_diachi"
    id = Column("MaDiaChi", Integer, primary_key=True, autoincrement=True)
    ten_dia_chi = Column("TenDiaChi", String(200), nullable=False)

    def __str__(self):
        return self.ten_dia_chi



class CapBac(db.Model):
    __tablename__ = "tbl_capbac"
    id = Column("MaCapBac", Integer, primary_key=True, autoincrement=True)
    ten_cap_bac = Column("TenCapBac", String(100), nullable=False)


class MucLuong(db.Model):
    __tablename__ = "tbl_mucluong"
    id = Column("MaMucLuong", Integer, primary_key=True, autoincrement=True)
    ten_muc_luong = Column("TenMucLuong", String(100), nullable=False)


class ChuyenNganh(db.Model):
    __tablename__ = "tbl_chuyennganh"
    id = Column("MaCN", Integer, primary_key=True, autoincrement=True)
    ten_cn = Column("TenCN", String(200), nullable=False)


class LoaiCongViec(db.Model):
    __tablename__ = "tbl_loaicongviec"
    id = Column("MaLoaiCV", Integer, primary_key=True, autoincrement=True)
    ten_loai_cv = Column("TenLoaiCV", String(100), nullable=False)



class TaiKhoan(db.Model,UserMixin):
    __tablename__ = "tbl_taikhoan"
    id = Column("MaTaiKhoan", Integer, primary_key=True, autoincrement=True)
    username=Column(String(50),nullable=False, unique=True)
    email = Column("Email", String(100), unique=True, nullable=False)
    google_id = Column("GoogleId", String(255), unique=True, nullable=True)
    mat_khau = Column("MatKhau", String(100), nullable=True)
    ngay_tao = Column("NgayTao", DateTime, default=datetime.now)
    trang_thai = Column("TrangThai", Boolean, default=True)
    loai_tai_khoan = Column("LoaiTaiKhoan", String(20))  # "ungvien" hoặc "nhatuyendung"
    ungvien = relationship("UngVien", uselist=False, back_populates="tai_khoan")
    nhatuyendung = relationship("NhaTuyenDung", uselist=False, back_populates="tai_khoan")

    __mapper_args__ = {
        "polymorphic_identity": "taikhoan",
        "polymorphic_on": loai_tai_khoan
    }
class Admin(TaiKhoan):
    __tablename__ = "tbl_admin"
    id = Column("MaAdmin", Integer, ForeignKey("tbl_taikhoan.MaTaiKhoan"), primary_key=True)
    ten_admin = Column("TenAdmin", String(100), nullable=False)

    __mapper_args__ = {"polymorphic_identity": "admin"}

class UngVien(TaiKhoan):
    __tablename__ = "tbl_ungvien"
    id = Column("MaUngVien", Integer, ForeignKey("tbl_taikhoan.MaTaiKhoan"), primary_key=True)
    ten_uv = Column("TenUngVien", String(100), nullable=False)
    so_dien_thoai = Column("SoDienThoai", String(20))
    ngay_sinh = Column("NgaySinh", Date)
    anh_dai_dien = Column("AnhDaiDien", String(200))
    so_thich = Column("SoThich", String(200))
    dia_chi = Column("DiaChi", String(200))

    tai_khoan = relationship("TaiKhoan", back_populates="ungvien")

    ho_so = relationship("HoSoXinViec", back_populates="ung_vien")
    ung_tuyen = relationship("UngTuyen", back_populates="ung_vien")

    __mapper_args__ = {
        "polymorphic_identity": "ungvien",
    }


class NhaTuyenDung(TaiKhoan):
    __tablename__ = "tbl_nhatuyendung"
    id = Column("MaNTD", Integer, ForeignKey("tbl_taikhoan.MaTaiKhoan"), primary_key=True)
    ten_ntd = Column("TenNTD", String(100), nullable=False)
    dia_chi = Column("DiaChi", String(200))
    so_dien_thoai = Column("SoDienThoai", String(20))
    anh_dai_dien = Column("AnhDaiDien", String(200))

    tai_khoan = relationship("TaiKhoan", back_populates="nhatuyendung")
    tin_tuyen_dung = relationship("TinTuyenDung", back_populates="nha_tuyen_dung")
    giao_dich = relationship("GiaoDich", back_populates="nha_tuyen_dung")

    __mapper_args__ = {
        "polymorphic_identity": "nhatuyendung",
    }


class HoSoXinViec(db.Model):
    __tablename__ = "tbl_hosoxinviec"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ma_uv = db.Column(db.Integer, db.ForeignKey("tbl_ungvien.MaUngVien"), nullable=False)

    # Thông tin cá nhân
    ten_hs = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255))
    address = db.Column(db.String(255))
    phone = db.Column(db.String(50))
    email = db.Column(db.String(120))

    # Nội dung CV
    muc_tieu_nghe_nghiep = db.Column(db.Text)
    ky_nang = db.Column(db.Text)
    hoc_van = db.Column(db.Text)
    kinh_nghiem = db.Column(db.Text)
    giai_thuong = db.Column(db.Text)

    projects = db.Column(db.Text)
    file_cv = db.Column(db.String(500))

    # Foreign keys chính xác
    ma_cn = db.Column(db.Integer, db.ForeignKey("tbl_chuyennganh.MaCN"), nullable=True)
    ma_loai_cv = db.Column(db.Integer, db.ForeignKey("tbl_loaicongviec.MaLoaiCV"), nullable=True)
    ma_cap_bac = db.Column(db.Integer, db.ForeignKey("tbl_capbac.MaCapBac"), nullable=True)

    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    # Quan hệ
    ung_vien = relationship("UngVien", back_populates="ho_so")




class TinTuyenDung(db.Model):
    __tablename__ = "tbl_tintuyendung"
    id = Column("MaTTD", Integer, primary_key=True, autoincrement=True)
    ma_ntd = Column("MaNTD", Integer, ForeignKey("tbl_nhatuyendung.MaNTD"), nullable=False)
    ma_cn = Column("MaCN", Integer, ForeignKey("tbl_chuyennganh.MaCN"))
    ma_loai_cv = Column("MaLoaiCV", Integer, ForeignKey("tbl_loaicongviec.MaLoaiCV"))
    ma_muc_luong = Column("MaMucLuong", Integer, ForeignKey("tbl_mucluong.MaMucLuong"))
    ma_cap_bac = Column("MaCapBac", Integer, ForeignKey("tbl_capbac.MaCapBac"))
    ten_cong_viec = Column("TenCongViec", String(200))
    dia_chi_lam_viec = Column("DiaChiLamViec", String(200))
    so_luong = Column("SoLuong", Integer)
    gioi_tinh_yc = Column("GioiTinhYC", String(50))


    mo_ta = Column("MoTaCongViec", Text)
    yeu_cau = Column("YeuCauCongViec", Text)
    ky_nang_lien_quan = Column("KyNangLienQuan", Text)
    quyen_loi = Column("QuyenLoi", Text)

    ngay_dang = Column("NgayDang", Date)
    han_nop = Column("HanNop", Date)
    trang_thai = Column("TrangThai", Boolean, default=True)

    # Quan hệ
    nha_tuyen_dung = relationship("NhaTuyenDung", back_populates="tin_tuyen_dung")
    chuyen_nganh = relationship("ChuyenNganh", backref="tin_tuyen_dung")
    loai_cv = relationship("LoaiCongViec", backref="tin_tuyen_dung")
    muc_luong = relationship("MucLuong", backref="tin_tuyen_dung")
    cap_bac = relationship("CapBac", backref="tin_tuyen_dung")
    ung_tuyen = relationship("UngTuyen", back_populates="tin_tuyen_dung")
    giao_dich = relationship("GiaoDich", back_populates="tin_tuyen_dung")


class UngTuyen(db.Model):
    __tablename__ = "tbl_ungtuyen"
    id = Column("MaUngTuyen", Integer, primary_key=True, autoincrement=True)
    ma_ttd = Column("MaTTD", Integer, ForeignKey("tbl_tintuyendung.MaTTD"), nullable=False)
    ma_uv = Column("MaUngVien", Integer, ForeignKey("tbl_ungvien.MaUngVien"), nullable=False)

    # 2 cách ứng tuyển
    link_cv = Column("LinkCV", String(500))  # nếu upload file (Cloudinary URL)
    ma_hs = Column("MaHoSo", Integer, ForeignKey("tbl_hosoxinviec.id"), nullable=True)  # nếu dùng hồ sơ đã tạo

    ngay_ung_tuyen = Column("NgayUngTuyen", DateTime, default=datetime.now)
    trang_thai = Column(
        "TrangThai",
        Enum("Đang chờ", "Phê duyệt", "Từ chối", name="trangthai_enum"),
        default="Đang chờ",
        nullable=False
    )

    # Quan hệ
    tin_tuyen_dung = relationship("TinTuyenDung", back_populates="ung_tuyen")
    ung_vien = relationship("UngVien", back_populates="ung_tuyen")
    ho_so = relationship("HoSoXinViec")   # thêm để join vào hồ sơ

class GiaoDich(db.Model):
    __tablename__ = "tbl_giaodich"
    id = Column("MaGD", Integer, primary_key=True, autoincrement=True)
    ma_ntd = Column("MaNTD", Integer, ForeignKey("tbl_nhatuyendung.MaNTD"), nullable=False)
    ma_ttd = Column("MaTTD", Integer, ForeignKey("tbl_tintuyendung.MaTTD"), nullable=True)
    so_tien = Column("SoTien", Integer, nullable=False)
    noi_dung = Column("NoiDung", String(255))
    ngay_tao = Column("NgayTao", DateTime, default=datetime.now)
    trang_thai = Column("TrangThai", String(20), default="Chờ xử lý")  # Chờ xử lý | Thành công | Thất bại
    request_id = Column("RequestId", String(64))
    order_id = Column("OrderId", String(64))

    nha_tuyen_dung = relationship("NhaTuyenDung", back_populates="giao_dich")
    tin_tuyen_dung = relationship("TinTuyenDung", back_populates="giao_dich")


if __name__=='__main__':
    with app.app_context():
        print(db.engine.url)
        db.drop_all()
        print("✅ DB connected")
        db.create_all()
        Admin.__table__.create(bind=db.engine, checkfirst=True)


        diachis = [
            DiaChi(ten_dia_chi="Hà Nội"),
            DiaChi(ten_dia_chi="TP. Hồ Chí Minh"),
            DiaChi(ten_dia_chi="Đà Nẵng")
        ]

        capbacs = [
            CapBac(ten_cap_bac="Thực tập"),
            CapBac(ten_cap_bac="Nhân viên"),
            CapBac(ten_cap_bac="Trưởng nhóm"),
            CapBac(ten_cap_bac="Quản lý")
        ]

        mucluongs = [
            MucLuong(ten_muc_luong="Dưới 10 triệu"),
            MucLuong(ten_muc_luong="10 - 20 triệu"),
            MucLuong(ten_muc_luong="Trên 20 triệu")
        ]

        chuyennganhs = [
            ChuyenNganh(ten_cn="Công nghệ thông tin"),
            ChuyenNganh(ten_cn="Kế toán"),
            ChuyenNganh(ten_cn="Marketing")
        ]

        loaicongviecs = [
            LoaiCongViec(ten_loai_cv="Full-time"),
            LoaiCongViec(ten_loai_cv="Part-time"),
            LoaiCongViec(ten_loai_cv="Remote")
        ]

        db.session.add_all(diachis + capbacs + mucluongs + chuyennganhs + loaicongviecs)
        db.session.commit()

        admin = Admin(
            username="admin",
            email="admin@jobconnect.com",
            mat_khau=hashlib.md5("admin123".encode("utf-8")).hexdigest(),
            ten_admin="Quản trị viên",
            loai_tai_khoan="admin"
        )

        db.session.add(admin)
        db.session.commit()

