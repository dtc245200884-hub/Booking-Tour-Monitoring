import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from time import perf_counter

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
    {
        "id": 1,
        "name": "Khám phá Đà Nẵng",
        "location": "Đà Nẵng",
        "days": "3 ngày 2 đêm",
        "price": 2500000,
        "description": "Khám phá biển Mỹ Khê, bán đảo Sơn Trà và Bà Nà Hills.",
    },
    {
        "id": 2,
        "name": "Du lịch Đà Lạt",
        "location": "Lâm Đồng",
        "days": "3 ngày 2 đêm",
        "price": 2200000,
        "description": "Tham quan hồ Xuân Hương, đồi chè và các điểm du lịch nổi tiếng.",
    },
    {
        "id": 3,
        "name": "Khám phá Phú Quốc",
        "location": "Kiên Giang",
        "days": "4 ngày 3 đêm",
        "price": 4200000,
        "description": "Tận hưởng biển xanh, cát trắng và những trải nghiệm đảo.",
    },
]


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
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


@app.route("/")
def index():
    return render_template("index.html", tours=TOURS)


@app.route("/book/<int:tour_id>", methods=["POST"])
def book(tour_id):
    tour = next((item for item in TOURS if item["id"] == tour_id), None)

    if tour is None:
        flash("Không tìm thấy tour.", "error")
        return redirect(url_for("index"))

    name = request.form.get("customer_name", "").strip()
    email = request.form.get("email", "").strip()
    guests_text = request.form.get("guests", "1").strip()

    try:
        guests = int(guests_text)
    except ValueError:
        guests = 0

    if not name or not email or "@" not in email or not 1 <= guests <= 20:
        flash("Vui lòng nhập tên, email hợp lệ và số khách từ 1 đến 20.", "error")
        return redirect(url_for("index"))

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """INSERT INTO bookings (customer_name, email, tour_id, guests)
               VALUES (?, ?, ?, ?)""",
            (name, email, tour_id, guests),
        )

    flash(f"Đặt tour {tour['name']} thành công! Đây là xác nhận demo.", "success")
    return redirect(url_for("index"))


@app.route("/health")
def health():
    return {"status": "ok"}, 200


@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
