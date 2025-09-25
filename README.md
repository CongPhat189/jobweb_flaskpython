# 🏢 OpenJob – Hệ Thống Tìm Việc Làm

**OpenJob** là một ứng dụng web hỗ trợ **kết nối nhà tuyển dụng và ứng viên**.  
Dự án được xây dựng bằng **Flask (Python)** với cơ sở dữ liệu **MySQL**, hỗ trợ đăng nhập Google, upload CV, quản lý tin tuyển dụng, thanh toán MoMo, và trang quản trị cho admin.

---

## 🚀 Tính năng chính

### 👨‍💼 Ứng viên
- Đăng ký / đăng nhập (hỗ trợ Google OAuth).  
- Tạo hồ sơ xin việc (CV online).  
- Ứng tuyển bằng **CV đã upload** hoặc **hồ sơ đã tạo trên hệ thống**.  
- Quản lý thông tin cá nhân.  

### 🏢 Nhà tuyển dụng
- Đăng tin tuyển dụng (theo **ngành nghề**, **mức lương**, **địa chỉ**, **cấp bậc**, **loại công việc**).  
- Quản lý tin (ẩn/hiện, sửa, xóa).  
- Nhận danh sách ứng viên ứng tuyển kèm CV/Hồ sơ.  
- Thanh toán qua **MoMo** để đăng tin.  

### 🔑 Quản trị viên (Admin)
- Thống kê **doanh thu MoMo theo tháng**.  
- Thống kê **số lượt ứng tuyển theo ngành**.  
- Quản lý tin tuyển dụng (ẩn tin spam).  
- Quản lý tài khoản (khóa/mở).  
- Quản lý **danh mục hệ thống**: Địa chỉ, Cấp bậc, Mức lương, Chuyên ngành, Loại công việc.  

---

## 🛠️ Công nghệ sử dụng

- **Backend**: Flask 3.x, Flask-SQLAlchemy, Flask-Login, Authlib (Google OAuth2)  
- **Database**: MySQL  
- **Frontend**: Bootstrap 5, Jinja2 Template, Chart.js  
- **Cloud Storage**: Cloudinary (lưu ảnh avatar, CV)  
- **Thanh toán**: MoMo Payment Gateway  
- **Khác**: PyMySQL, Werkzeug, Pandas (thống kê)

🌐 **Link website**: [https://jobweb-flaskpython.onrender.com/](https://jobweb-flaskpython.onrender.com/)
