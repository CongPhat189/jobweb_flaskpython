from flask import Flask, render_template
from WebsiteTimViecLam.HeThongTimViecLam import app

from WebsiteTimViecLam.HeThongTimViecLam.dao import loadTinTuyenDung



@app.route("/")
def index():
    tintuyendung=loadTinTuyenDung()
    return  render_template("index.html",ttd=tintuyendung)


if __name__=="__main__":
    with app.app_context():
        app.run(debug=True, port=5000)