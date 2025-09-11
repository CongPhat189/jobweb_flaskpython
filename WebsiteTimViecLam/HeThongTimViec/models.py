from WebsiteTimViecLam.HeThongTimViec import  db,app
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


class TaiKhoan(db.Model):
    __tablename__ = "tbl_taikhoan"
    id = Column("MaTaiKhoan", Integer, primary_key=True, autoincrement=True)
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

        # # Bảng quyền
        # q1 = Quyen(ten_quyen="Admin")
        # q2 = Quyen(ten_quyen="Nhà tuyển dụng")
        # q3 = Quyen(ten_quyen="Ứng viên")
        #
        # # Bảng cấp bậc
        # cb1 = CapBac(ten_cap_bac="Thực tập sinh")
        # cb2 = CapBac(ten_cap_bac="Nhân viên")
        # cb3 = CapBac(ten_cap_bac="Trưởng phòng")
        #
        # # Bảng mức lương
        # ml1 = MucLuong(ten_muc_luong="5-10 triệu")
        # ml2 = MucLuong(ten_muc_luong="10-20 triệu")
        #
        # # Bảng chuyên ngành
        # cn1 = ChuyenNganh(ten_cn="Công nghệ thông tin")
        # cn2 = ChuyenNganh(ten_cn="Kế toán")
        #
        # # Bảng loại công việc
        # lcv1 = LoaiCongViec(ten_loai_cv="Toàn thời gian")
        # lcv2 = LoaiCongViec(ten_loai_cv="Bán thời gian")
        #
        # # Nhà tuyển dụng
        # ntd1 = NhaTuyenDung(
        #     ten_ntd="Công ty ABC",
        #     dia_chi="Hà Nội",
        #     so_dien_thoai="0123456789",
        #     email="contact@abc.com",
        #     website="https://abc.com",
        #     anh_dai_dien="ntd1.png"
        # )
        #
        # # Ứng viên
        # uv1 = UngVien(
        #     ten_uv="Nguyễn Văn A",
        #     so_dien_thoai="0987654321",
        #     email="vana@gmail.com",
        #     ngay_sinh=datetime(1995, 5, 10),
        #     anh_dai_dien="a.png",
        #     so_thich="Đọc sách, du lịch",
        #     dia_chi="Hồ Chí Minh"
        # )
        #
        # # Hồ sơ xin việc
        # hs1 = HoSoXinViec(
        #     ten_hs="CV IT Nguyễn Văn A",
        #     ung_vien=uv1,
        #     chuyen_nganh=cn1,
        #     loai_cv=lcv1,
        #     cap_bac=cb2,
        #     muc_tieu_nghe_nghiep="Phát triển kỹ năng lập trình",
        #     kinh_nghiem="2 năm Java",
        #     ky_nang="Python, Django, React",
        #     hoc_van="ĐH CNTT HCM",
        #     giai_thuong="Top 10 sinh viên xuất sắc"
        # )
        #
        # # Tin tuyển dụng
        # ttd1 = TinTuyenDung(
        #     nha_tuyen_dung=ntd1,
        #     chuyen_nganh=cn1,
        #     loai_cv=lcv1,
        #     muc_luong=ml2,
        #     cap_bac=cb2,
        #     ten_cong_viec="Lập trình viên Python",
        #     dia_chi_lam_viec="Hà Nội",
        #     so_luong=2,
        #     gioi_tinh_yc="Không yêu cầu",
        #     mo_ta="Phát triển ứng dụng web bằng Django",
        #     yeu_cau="Có kinh nghiệm 1-2 năm",
        #     ky_nang_lien_quan="Python, Django, SQL",
        #     quyen_loi="Thưởng lễ, tết, bảo hiểm đầy đủ",
        #     ngay_dang=datetime(2025, 9, 1),
        #     han_nop=datetime(2025, 9, 30),
        #     trang_thai=True
        # )
        #
        # # Ứng tuyển
        # ut1 = UngTuyen(
        #     tin_tuyen_dung=ttd1,
        #     ung_vien=uv1,
        #     link_cv="cv_nguyenvana.pdf",
        #     ngay_ung_tuyen=datetime(2025, 9, 5)
        # )
        #
        # db.session.add_all([
        #     q1, q2, q3,
        #     cb1, cb2, cb3,
        #     ml1, ml2,
        #     cn1, cn2,
        #     lcv1, lcv2,
        #     ntd1, uv1, hs1, ttd1, ut1
        # ])
        #
        # db.session.commit()