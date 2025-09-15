from flask import Flask, render_template, request, redirect, url_for, flash
from WebsiteTimViecLam.HeThongTimViecLam import app

from WebsiteTimViecLam.HeThongTimViecLam.dao import loadTinTuyenDung,ungTuyen



@app.route("/")
def index():
    tintuyendung=loadTinTuyenDung()
    return  render_template("index.html",ttd=tintuyendung)


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


if __name__=="__main__":
    with app.app_context():
        app.run(debug=True, port=5000)