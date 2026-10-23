# Booking Tour Monitoring

## Công nghệ
- Docker Compose
- Prometheus
- Node Exporter
- Grafana

## Truy cập
- Prometheus: http://localhost:9091
- Grafana: http://localhost:3002
+ Tài khoản : admin
+ Mật khẩu : admin
- Node Exporter: http://localhost:9100/metrics
- Website Booking Tour:	http://localhost:5000

## Khởi chạy
docker compose up -d

## Kiểm tra
docker compose ps
## Cấu trúc thư mục dự án
Đường dẫn trên Ubuntu Server của bạn:

/root/booking-tour-monitoring
booking-tour-monitoring/

README.md

Giới thiệu dự án và hướng dẫn sử dụng


docker-compose.yml

Khai báo và kết nối 4 container


app/

Ứng dụng Booking Tour viết bằng Python Flask

app.py · Dockerfile · requirements.txt

templates/ · static/


prometheus/

Cấu hình thu thập metrics

prometheus.yml


grafana/

Cấu hình nguồn dữ liệu giám sát

booking-tour-monitoring/
├── app/
│   ├── app.py
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── templates/
│   └── static/
├── prometheus/
│   └── prometheus.yml
├── grafana/
│   └── provisioning/
│       └── datasources/
├── docker-compose.yml
├── README.md
└── .gitignore

provisioning/datasources/prometheus.yml


.gitignore
