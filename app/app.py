import os
import sqlite3
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from time import perf_counter

from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, session
)
from werkzeug.security import generate_password_hash, check_password_hash
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "booking-tour-dev-key")
DB_PATH = os.environ.get("DB_PATH", "/data/bookings.db")

REQUESTS = Counter(
    "booking_tour_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)
REQUEST_DURATION = Histogram(
    "booking_tour_http_request_duration_seconds",
    "HTTP request duration in seconds",
)

TOURS = [
    {"id": 1, "name": "Khám phá Đà Nẵng", "location": "Đà Nẵng", "days": "3 ngày 2 đêm", "price": 2500000, "description": "Biển Mỹ Khê, Sơn Trà và Bà Nà Hills.", "image": "https://images.unsplash.com/photo-1559592413-7cec4d0cae2b?auto=format&fit=crop&w=1200&q=85"},
    {"id": 2, "name": "Du lịch Đà Lạt", "location": "Đà Lạt", "days": "3 ngày 2 đêm", "price": 2200000, "description": "Hồ Xuân Hương, đồi chè và rừng thông.", "image": "https://images.unsplash.com/photo-1570168007204-dfb528c6958f?auto=format&fit=crop&w=1200&q=85"},
    {"id": 3, "name": "Khám phá Phú Quốc", "location": "Phú Quốc", "days": "4 ngày 3 đêm", "price": 3500000, "description": "Bãi biển, đảo nhỏ và hoạt động khám phá biển.", "image": "https://images.unsplash.com/photo-1518509562904-e7ef99cdcc86?auto=format&fit=crop&w=1200&q=85"},
    {"id": 4, "name": "Vịnh Hạ Long", "location": "Hạ Long", "days": "2 ngày 1 đêm", "price": 1800000, "description": "Du thuyền khám phá kỳ quan vịnh.", "image": "https://images.unsplash.com/photo-1530789253388-582c481c54b0?auto=format&fit=crop&w=1200&q=85"},
    {"id": 5, "name": "Sa Pa mùa mây", "location": "Sa Pa", "days": "3 ngày 2 đêm", "price": 2800000, "description": "Núi rừng Tây Bắc và bản làng.", "image": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=1200&q=85"},
    {"id": 6, "name": "Hà Nội nghìn năm", "location": "Hà Nội", "days": "2 ngày 1 đêm", "price": 1500000, "description": "Phố cổ, hồ Gươm và ẩm thực Hà Nội.", "image": "https://images.unsplash.com/photo-1509030450996-dd1a26dda07a?auto=format&fit=crop&w=1200&q=85"},
    {"id": 7, "name": "Ninh Bình non nước", "location": "Ninh Bình", "days": "2 ngày 1 đêm", "price": 1700000, "description": "Tràng An, Tam Cốc và cảnh núi đá vôi.", "image": "https://images.unsplash.com/photo-1470770841072-f978cf4d019e?auto=format&fit=crop&w=1200&q=85"},
    {"id": 8, "name": "Hà Giang hùng vĩ", "location": "Hà Giang", "days": "4 ngày 3 đêm", "price": 3200000, "description": "Cao nguyên đá và cung đường đèo.", "image": "https://images.unsplash.com/photo-1464278533981-50106e6176b1?auto=format&fit=crop&w=1200&q=85"},
    {"id": 9, "name": "Cao Bằng thác Bản Giốc", "location": "Cao Bằng", "days": "3 ngày 2 đêm", "price": 2600000, "description": "Thác nước và cảnh sắc vùng biên.", "image": "https://images.unsplash.com/photo-1433086966358-54859d0ed716?auto=format&fit=crop&w=1200&q=85"},
    {"id": 10, "name": "Mộc Châu xanh", "location": "Mộc Châu", "days": "2 ngày 1 đêm", "price": 1600000, "description": "Đồi chè, thung lũng và nông trại.", "image": "https://images.unsplash.com/photo-1470252649378-9c29740c9fa8?auto=format&fit=crop&w=1200&q=85"},
    {"id": 11, "name": "Phố cổ Hội An", "location": "Hội An", "days": "2 ngày 1 đêm", "price": 1900000, "description": "Phố cổ, đèn lồng và ẩm thực địa phương.", "image": "https://images.unsplash.com/photo-1528127269322-539801943592?auto=format&fit=crop&w=1200&q=85"},
    {"id": 12, "name": "Cố đô Huế", "location": "Huế", "days": "2 ngày 1 đêm", "price": 1800000, "description": "Đại Nội, lăng tẩm và di sản văn hóa.", "image": "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1200&q=85"},
    {"id": 13, "name": "Phong Nha kỳ thú", "location": "Phong Nha", "days": "3 ngày 2 đêm", "price": 2400000, "description": "Hang động và thiên nhiên xanh mát.", "image": "https://images.unsplash.com/photo-1473448912268-2022ce9509d8?auto=format&fit=crop&w=1200&q=85"},
    {"id": 14, "name": "Quy Nhơn biển xanh", "location": "Quy Nhơn", "days": "3 ngày 2 đêm", "price": 2300000, "description": "Bãi biển và các cung đường ven biển.", "image": "https://images.unsplash.com/photo-1500375592092-40eb2168fd21?auto=format&fit=crop&w=1200&q=85"},
    {"id": 15, "name": "Nha Trang nghỉ dưỡng", "location": "Nha Trang", "days": "3 ngày 2 đêm", "price": 2700000, "description": "Biển đảo và trải nghiệm nghỉ dưỡng.", "image": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1200&q=85"},
    {"id": 16, "name": "TP. Hồ Chí Minh", "location": "TP. Hồ Chí Minh", "days": "2 ngày 1 đêm", "price": 1400000, "description": "Địa danh đô thị và ẩm thực Sài Gòn.", "image": "https://images.unsplash.com/photo-1519501025264-65ba15a82390?auto=format&fit=crop&w=1200&q=85"},
    {"id": 17, "name": "Cần Thơ miền sông nước", "location": "Cần Thơ", "days": "2 ngày 1 đêm", "price": 1600000, "description": "Chợ nổi và văn hóa miền Tây.", "image": "https://images.unsplash.com/photo-1501785888041-af3ef285b470?auto=format&fit=crop&w=1200&q=85"},
    {"id": 18, "name": "Côn Đảo bình yên", "location": "Côn Đảo", "days": "3 ngày 2 đêm", "price": 3900000, "description": "Biển đảo và các điểm tham quan lịch sử.", "image": "https://images.unsplash.com/photo-1519046904884-53103b34b206?auto=format&fit=crop&w=1200&q=85"},
    {"id": 19, "name": "Mũi Né nắng vàng", "location": "Mũi Né", "days": "2 ngày 1 đêm", "price": 1900000, "description": "Đồi cát và bờ biển miền nhiệt đới.", "image": "https://images.unsplash.com/photo-1473116763249-2faaef81ccda?auto=format&fit=crop&w=1200&q=85"},
    {"id": 20, "name": "Bến Tre miệt vườn", "location": "Bến Tre", "days": "2 ngày 1 đêm", "price": 1500000, "description": "Vườn cây, kênh rạch và đặc sản địa phương.", "image": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=1200&q=85"},
]

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    directory = os.path.dirname(DB_PATH)
    if directory:
        os.makedirs(directory, exist_ok=True)

    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT NOT NULL,
                email TEXT NOT NULL,
                tour_id INTEGER NOT NULL,
                guests INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        user_columns = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(users)").fetchall()
        }

        if "role" not in user_columns:
            conn.execute(
                "ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'user'"
            )

        columns = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(bookings)").fetchall()
        }
        if "user_id" not in columns:
            conn.execute(
                "ALTER TABLE bookings ADD COLUMN user_id INTEGER REFERENCES users(id)"
            )


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Vui lòng đăng nhập để tiếp tục.", "error")
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped
def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Vui lòng đăng nhập.", "error")
            return redirect(url_for("login"))

        with get_db() as conn:
            user = conn.execute(
                "SELECT role FROM users WHERE id = ?",
                (session["user_id"],)
            ).fetchone()

        if not user or user["role"] != "admin":
            flash("Bạn không có quyền truy cập trang quản trị.", "error")
            return redirect(url_for("index"))

        return view(*args, **kwargs)
    return wrapped
@app.before_request
def start_timer():
    request._started_at = perf_counter()


@app.after_request
def record_request(response):
    if request.endpoint != "metrics":
        REQUESTS.labels(
            method=request.method,
            endpoint=request.endpoint or "unknown",
            status=str(response.status_code),
        ).inc()
        started = getattr(request, "_started_at", None)
        if started is not None:
            REQUEST_DURATION.observe(perf_counter() - started)
    return response


@app.context_processor
def inject_user():
    return {"logged_in_user": session.get("user_name")}


@app.route("/")
def index():
    return render_template("index.html", tours=TOURS)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if not name or len(name) > 100 or not email or "@" not in email:
            flash("Vui lòng nhập họ tên và email hợp lệ.", "error")
        elif len(password) < 8:
            flash("Mật khẩu phải có ít nhất 8 ký tự.", "error")
        elif password != confirm:
            flash("Mật khẩu xác nhận không khớp.", "error")
        else:
            try:
                with get_db() as conn:
                    conn.execute(
                        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                        (name, email, generate_password_hash(password)),
                    )
                flash("Đăng ký thành công. Hãy đăng nhập.", "success")
                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                flash("Email này đã được đăng ký.", "error")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        with get_db() as conn:
            user = conn.execute(
                "SELECT * FROM users WHERE email = ?", (email,)
            ).fetchone()

        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["user_role"] = user["role"]

            next_url = request.args.get("next", "")
            if next_url.startswith("/") and not next_url.startswith("//"):
                return redirect(next_url)
            return redirect(url_for("index"))

        flash("Email hoặc mật khẩu không chính xác.", "error")

    return render_template("login.html")


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("Bạn đã đăng xuất.", "success")
    return redirect(url_for("index"))


@app.route("/tour/<int:tour_id>")
def tour_detail(tour_id):
    tour = next((item for item in TOURS if item["id"] == tour_id), None)
    if tour is None:
        flash("Không tìm thấy tour.", "error")
        return redirect(url_for("index"))
    return render_template("tour_detail.html", tour=tour)


@app.route("/book/<int:tour_id>", methods=["POST"])
@login_required
def book(tour_id):
    tour = next((item for item in TOURS if item["id"] == tour_id), None)
    if tour is None:
        flash("Không tìm thấy tour.", "error")
        return redirect(url_for("index"))

    name = request.form.get("customer_name", "").strip()
    email = request.form.get("email", "").strip().lower()
    guests_text = request.form.get("guests", "1").strip()

    try:
        guests = int(guests_text)
    except ValueError:
        guests = 0

    if not name or len(name) > 100 or "@" not in email or not 1 <= guests <= 20:
        flash("Vui lòng nhập tên, email hợp lệ và số khách từ 1 đến 20.", "error")
        return redirect(url_for("index"))

    with get_db() as conn:
        conn.execute(
            """INSERT INTO bookings
               (customer_name, email, tour_id, guests, user_id)
               VALUES (?, ?, ?, ?, ?)""",
            (name, email, tour_id, guests, session["user_id"]),
        )

    flash(f"Đặt tour {tour['name']} thành công!", "success")
    return redirect(url_for("my_bookings"))


@app.route("/my-bookings")
@login_required
def my_bookings():
    with get_db() as conn:
        rows = conn.execute(
            """SELECT id, customer_name, email, tour_id, guests, created_at
               FROM bookings WHERE user_id = ?
               ORDER BY id DESC""",
            (session["user_id"],),
        ).fetchall()

    bookings = []
    for row in rows:
        item = dict(row)
        item["tour"] = next(
            (tour for tour in TOURS if tour["id"] == item["tour_id"]), None
        )
        bookings.append(item)

    return render_template("my_bookings.html", bookings=bookings)

@app.route("/admin")
@admin_required
def admin_dashboard():
    with get_db() as conn:
        users = conn.execute(
            """SELECT id, name, email, role, created_at
               FROM users ORDER BY id DESC"""
        ).fetchall()

        rows = conn.execute(
            """SELECT b.id, b.customer_name, b.email, b.tour_id,
                      b.guests, b.created_at, u.name AS account_name
               FROM bookings b
               LEFT JOIN users u ON u.id = b.user_id
               ORDER BY b.id DESC"""
        ).fetchall()

    bookings = []
    for row in rows:
        item = dict(row)
        item["tour"] = next(
            (tour for tour in TOURS if tour["id"] == item["tour_id"]),
            None
        )
        bookings.append(item)

    return render_template(
        "admin.html",
        users=users,
        bookings=bookings,
        tours=TOURS
    )
@app.route("/admin/user/<int:user_id>/role", methods=["POST"])
@admin_required
def change_user_role(user_id):
    new_role = request.form.get("role", "").strip()

    if new_role not in ("user", "admin"):
        flash("Quyền tài khoản không hợp lệ.", "error")
        return redirect(url_for("admin_dashboard"))

    current_user_id = session.get("user_id")

    # Không cho Admin tự đổi quyền của chính mình
    if user_id == current_user_id:
        flash("Bạn không thể tự thay đổi quyền của mình.", "error")
        return redirect(url_for("admin_dashboard"))

    with get_db() as conn:
        target = conn.execute(
            "SELECT id, role FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()

        if not target:
            flash("Không tìm thấy tài khoản.", "error")
            return redirect(url_for("admin_dashboard"))

        # Không để hệ thống mất Admin cuối cùng
        if target["role"] == "admin" and new_role == "user":
            admin_count = conn.execute(
                "SELECT COUNT(*) FROM users WHERE role = 'admin'"
            ).fetchone()[0]

            if admin_count <= 1:
                flash("Không thể hạ quyền Admin cuối cùng.", "error")
                return redirect(url_for("admin_dashboard"))

        conn.execute(
            "UPDATE users SET role = ? WHERE id = ?",
            (new_role, user_id)
        )

    flash("Đã cập nhật quyền tài khoản.", "success")
    return redirect(url_for("admin_dashboard"))
@app.route("/health")
def health():
    return {"status": "ok"}, 200


@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
