from flask import Flask, render_template, request, redirect, flash, url_for, session
import pyodbc
#from database import get_db_connection

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Để sử dụng flash message

# Thông tin kết nối SQL Server
DB_CONFIG = {
    "server": "localhost",
    "database": "ff",
    "username": "sa",
    "password": "tpln002977703",
    "driver": "{ODBC Driver 17 for SQL Server}"
}

# Hàm kết nối SQL Server
def get_db_connection(uid, pwd):
    conn = pyodbc.connect(
        f"DRIVER={DB_CONFIG['driver']};"
        f"SERVER={DB_CONFIG['server']};"
        f"DATABASE={DB_CONFIG['database']};"
        f"UID={DB_CONFIG['username']};"
        f"PWD={DB_CONFIG['password']}"
    )
    return conn


@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        uid = request.form["uid"]
        pwd = request.form["pwd"]

        conn = get_db_connection(uid, pwd)  # Thử kết nối đến SQL Server
        if isinstance(conn, str):  # Nếu trả về lỗi
            flash(f"Lỗi: {conn}", "danger")
        else:
            session["uid"] = uid  # Lưu session đăng nhập
            session["pwd"] = pwd
            flash("Đăng nhập thành công!", "success")
            return redirect(url_for("dashboard"))  # Chuyển hướng đến trang dashboard

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "uid" not in session:
        return redirect(url_for("login"))  # Nếu chưa đăng nhập, quay lại trang login
    return redirect(url_for("query"))

@app.route("/logout")
def logout():
    session.clear()  # Xóa session
    flash("Bạn đã đăng xuất!", "info")
    return redirect(url_for("login"))
    
# Trang chủ - Form nhập lệnh SQL
@app.route("/query", methods=["GET", "POST"])
def query():
    result = None
    if request.method == "POST":
        query = request.form.get("query")  # Lấy lệnh SQL từ form
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(query)
            if query.strip().lower().startswith("select"):
                result = cursor.fetchall()  # Nếu là SELECT, lấy dữ liệu
            else:
                conn.commit()  # Nếu là INSERT, UPDATE, DELETE, commit thay đổi
                flash("Query executed successfully!", "success")
            cursor.close()
            conn.close()
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")
    return render_template("query.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
