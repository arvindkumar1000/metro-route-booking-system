# 🚇 Metro Route Booking System (Django REST API)

A production-ready Metro Route Booking System built using **Django** and **Django REST Framework**.  
This project simulates a real-world metro ticket booking workflow including payments, refunds, validation, and admin analytics.

---

## 📌 Features

### 👤 Authentication & Roles
- User Registration & Login
- Role-based access (User / Admin)
- Token Authentication

### 🚉 Metro Route Management
- Station creation
- Route management
- Distance & fare calculation logic

### 🎟 Ticket Booking System
- Book ticket between stations
- Auto fare calculation
- Booking status tracking

### 💳 Payment System
- Payment API
- ✔ Only allow payment if status = `PENDING`
- ✔ Prevent double payment
- ✔ Retry payment logic

### 🔁 Refund System
- Refund API
- Status validation before refund
- Prevent multiple refunds

### 🎫 Ticket Validation API
- Validate ticket before travel
- Prevent invalid/used ticket reuse

### 📊 Admin Analytics APIs
- Total Bookings
- Total Revenue
- Total Refunds
- Active Users

### 🧪 Testing
- Django Test Cases
- Separate test files for apps
- 100% core business logic covered

---

## 🛠 Tech Stack

- **Backend:** Django
- **API Framework:** Django REST Framework
- **Database:** SQLite (Development)
- **Authentication:** Token Auth
- **Testing:** Django TestCase
- **API Testing:** Postman


## 📂 Project Structure

metro_system/
│
├── accounts/
├── bookings/
├── payments/
├── routes/
├── admin_panel/
├── manage.py
└── requirements.txt


## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/arvindkumar1000/metro-route-booking-system.git
cd metro-route-booking-system
```

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5️⃣ Create Superuser

```bash
python manage.py createsuperuser
```

### 6️⃣ Run Server

```bash
python manage.py runserver
```

Server will run at:
```
http://127.0.0.1:8000/
```

---

## 🧪 Run Tests

```bash
python manage.py test
```

---

## 🔌 API Endpoints Overview

| Module | Endpoint Example |
|--------|------------------|
| Register | `/api/register/` |
| Login | `/api/login/` |
| Book Ticket | `/api/bookings/create/` |
| Make Payment | `/api/payments/pay/` |
| Retry Payment | `/api/payments/retry/` |
| Refund | `/api/payments/refund/` |
| Validate Ticket | `/api/bookings/validate/` |
| Admin Stats | `/api/admin/stats/` |

---

## 📈 Real-World Logic Implemented

- Payment allowed only if status = `PENDING`
- Double payment protection
- Refund validation rules
- Ticket validation security
- Admin revenue tracking
- Business rule-based APIs

---

## 🚀 Deployment Ready

This project is ready to deploy on:
- Render
- Railway
- AWS EC2
- DigitalOcean
- VPS

(Production database like PostgreSQL recommended)

---

## 👨‍💻 Author

**Arvind Kumar**  
Backend Developer (Django + DRF)  

📧 Email: arvindnagar58955@gmail.com  
📍 Location: Greater Noida, India  

---

## ⭐ Why This Project?

This project demonstrates:

- Clean API architecture
- Business logic implementation
- Real-world booking workflow
- Payment & refund lifecycle handling
- Admin analytics
- Unit testing
