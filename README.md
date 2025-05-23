# 🧑‍💼 Job Portal – Flask Web Application

A simple job portal web application built using Flask, SQLAlchemy, and Flask-Login. It supports user registration/login, job listing, and user management features.

---

## 🚀 Features

- User authentication (login/logout)
- Password hashing using Werkzeug
- Job listings and applications
- Admin/HR and Applicant roles 
- Database migrations using Flask-Migrate
- Secure file uploads (e.g. resumes)
- Modular Flask structure

---

## 🛠 Tech Stack

- Python 3.x
- Flask
- Flask-Login
- Flask-SQLAlchemy
- SQLAlchemy
- Jinja2 Templates

---

## 📦 Installation

1. **Clone the Repository**

```bash
git clone 🔗 https://github.com/Renna922/flask-job-portal
cd job-portal

2. **Create and Activate Virtual Environment**

# Create virtual environment
python -m venv venv

# Activate on Windows CMD
venv\Scripts\activate

# OR activate on PowerShell
.\venv\Scripts\Activate

# OR activate on macOS/Linux
source venv/bin/activate

3. **Install Dependencies**

pip install -r requirements.txt

🧱 Database Setup

This project uses db.create_all() to create the database schema without migrations.

Make sure you are inside your project directory and the virtual environment is activated.

1. **Open a Python shell**

python


2. **Create the database tables**

from app import db
db.create_all()

Ensure the db object is properly imported from your Flask app and initialized with your app context.

- Database schema creation using : db.create_all()




▶️ Run the Application

1. flask run

2. Visit http://127.0.0.1:5000 in your browser.

📁 Project Structure

job-portal/
├── app.py                  # Main Flask app
├── models.py               # SQLAlchemy models
├── templates/              # HTML templates
├── static/                 # CSS, JS, images
├── venv/                   # Virtual environment
├── requirements.txt        # Python packages
└── README.md               # Project documentation

✅ Dependencies (from requirements.txt)


alembic==1.12.1
click==8.1.8
colorama==0.4.6
Flask==2.2.5
Flask-Login==0.6.3
Flask-Migrate==4.1.0
flask-sqlalchemy==3.0.5
greenlet==3.1.1
importlib-metadata==6.7.0
importlib-resources==5.12.0
itsdangerous==2.1.2
jinja2==3.1.6
Mako==1.2.4
MarkupSafe==2.1.5
SQLAlchemy==2.0.41
typing-extensions==4.7.1
Werkzeug==2.2.3
zipp==3.15.0








