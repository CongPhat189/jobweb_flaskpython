from flask_login import UserMixin

from WebsiteTimViecLam.HeThongTimViecLam import  db,app
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Text, Date, DateTime
from sqlalchemy.orm import relationship, backref
from datetime import datetime


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
    mat_khau = Column("MatKhau", String(100), nullable=False)
    ngay_tao = Column("NgayTao", DateTime, default=datetime.now)
    trang_thai = Column("TrangThai", Boolean, default=True)
    loai_tai_khoan = Column("LoaiTaiKhoan", String(20))  # "ungvien" hoặc "nhatuyendung"

    __mapper_args__ = {
        "polymorphic_identity": "taikhoan",
        "polymorphic_on": loai_tai_khoan
    }


class UngVien(TaiKhoan):
    __tablename__ = "tbl_ungvien"
    id = Column("MaUngVien", Integer, ForeignKey("tbl_taikhoan.MaTaiKhoan"), primary_key=True)
    ten_uv = Column("TenUngVien", String(100), nullable=False)
    so_dien_thoai = Column("SoDienThoai", String(20))
    ngay_sinh = Column("NgaySinh", Date)
    anh_dai_dien = Column("AnhDaiDien", String(200))
    so_thich = Column("SoThich", String(200))
    dia_chi = Column("DiaChi", String(200))

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

    tin_tuyen_dung = relationship("TinTuyenDung", back_populates="nha_tuyen_dung")

    __mapper_args__ = {
        "polymorphic_identity": "nhatuyendung",
    }


class HoSoXinViec(db.Model):
    __tablename__ = "tbl_hosoxinviec"
    id = Column("MaHoSo", Integer, primary_key=True, autoincrement=True)
    ten_hs = Column("TenHoSo", String(200))
    ma_uv = Column("MaUngVien", Integer, ForeignKey("tbl_ungvien.MaUngVien"), nullable=False)
    ma_cn = Column("MaCN", Integer, ForeignKey("tbl_chuyennganh.MaCN"))
    ma_loai_cv = Column("MaLoaiCV", Integer, ForeignKey("tbl_loaicongviec.MaLoaiCV"))
    ma_cap_bac = Column("MaCapBac", Integer, ForeignKey("tbl_capbac.MaCapBac"))
    muc_tieu_nghe_nghiep = Column("MucTieuNgheNghiep", String(500))
    kinh_nghiem = Column("KinhNghiem", String(500))
    ky_nang = Column("KyNang", String(500))
    hoc_van = Column("HocVan", String(500))
    giai_thuong = Column("GiaiThuong", String(500))
    file_cv = db.Column("FileCV", String(500))  # lưu URL PDF hoặc path

    # Quan hệ
    ung_vien = relationship("UngVien", back_populates="ho_so")
    chuyen_nganh = relationship("ChuyenNganh", backref="ho_so")
    loai_cv = relationship("LoaiCongViec", backref="ho_so")
    cap_bac = relationship("CapBac", backref="ho_so")


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
    mo_ta = Column("MoTaCongViec", String(500))
    yeu_cau = Column("YeuCauCongViec", String(500))
    ky_nang_lien_quan = Column("KyNangLienQuan", String(500))
    quyen_loi = Column("QuyenLoi", String(500))
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


class UngTuyen(db.Model):
    __tablename__ = "tbl_ungtuyen"
    id = Column("MaUngTuyen", Integer, primary_key=True, autoincrement=True)
    ma_ttd = Column("MaTTD", Integer, ForeignKey("tbl_tintuyendung.MaTTD"), nullable=False)
    ma_uv = Column("MaUngVien", Integer, ForeignKey("tbl_ungvien.MaUngVien"), nullable=False)
    link_cv = Column("LinkCV", String(200))
    ngay_ung_tuyen = Column("NgayUngTuyen", Date, default=datetime.now)

    # Quan hệ
    tin_tuyen_dung = relationship("TinTuyenDung", back_populates="ung_tuyen")
    ung_vien = relationship("UngVien", back_populates="ung_tuyen")


if __name__=='__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()

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

        # Seed tài khoản
        uv1 = UngVien(
            email="uv1@example.com",
            username='a',
            mat_khau="123456",
            ten_uv="Nguyễn Văn A",
            so_dien_thoai="0912345678",
            ngay_sinh=datetime(1998, 5, 12),
            dia_chi="Hà Nội",
            so_thich="Đọc sách, du lịch"
        )

        uv2 = UngVien(
            email="uv2@example.com",
            username='b',
            mat_khau="123456",
            ten_uv="Trần Thị B",
            so_dien_thoai="0987654321",
            ngay_sinh=datetime(2000, 7, 20),
            dia_chi="TP.HCM",
            so_thich="Chạy bộ, nghe nhạc"
        )

        ntd1 = NhaTuyenDung(
            email="ntd1@company.com",
            username='c',
            mat_khau="123456",
            ten_ntd="Công ty TNHH ABC",
            dia_chi="TP.HCM",
            so_dien_thoai="0909123456"
        )

        db.session.add_all([uv1, uv2, ntd1])
        db.session.commit()

        # Seed hồ sơ xin việc
        hs1 = HoSoXinViec(
            ten_hs="CV Nguyễn Văn A",
            ma_uv=uv1.id,
            ma_cn=1,
            ma_loai_cv=1,
            ma_cap_bac=2,
            muc_tieu_nghe_nghiep="Phát triển kỹ năng lập trình backend",
            kinh_nghiem="2 năm làm Python Developer",
            ky_nang="Python, Django, SQL",
            hoc_van="Đại học CNTT",
            giai_thuong="Giải Nhất Hackathon 2022"
        )

        db.session.add(hs1)
        db.session.commit()

        # Seed tin tuyển dụng
        ttd1 = TinTuyenDung(
            ma_ntd=ntd1.id,
            ma_cn=1,
            ma_loai_cv=1,
            ma_muc_luong=2,
            ma_cap_bac=2,
            ten_cong_viec="Lập trình viên Python",
            dia_chi_lam_viec="Quận 1, TP.HCM",
            so_luong=2,
            gioi_tinh_yc="Không yêu cầu",
            mo_ta="Phát triển API cho hệ thống quản lý",
            yeu_cau="Có kinh nghiệm với Django/Flask",
            ky_nang_lien_quan="Python, REST API, SQL",
            quyen_loi="Bảo hiểm, lương tháng 13",
            ngay_dang=datetime.today(),
            han_nop=datetime(2025, 12, 31),
            trang_thai=True
        )

        db.session.add(ttd1)
        db.session.commit()

        # Seed ứng tuyển
        ut1 = UngTuyen(
            ma_ttd=ttd1.id,
            ma_uv=uv1.id,
            link_cv="http://example.com/cv_nguyenvana.pdf"
        )

        db.session.add(ut1)
        db.session.commit()