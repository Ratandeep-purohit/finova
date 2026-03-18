# 🚀 Finova Quick Start Guide

This guide will help you quickly set up and run the Finova project on your local machine.

## 🛠️ Prerequisites

Before you begin, ensure you have the following installed on your machine:
- **Python 3.8+**
- **MySQL Server** (Running locally)

---

## 💾 Database Setup

1. Open your MySQL client or command line.
2. Create a database named `finova`:
   ```sql
   CREATE DATABASE finova;
   ```
3. Update the database credentials in `Finova/settings.py` if your local MySQL configuration differs (default user is `root`, password is `jaanvi4211`).

---

## 📦 Installation & Setup

1. Open a terminal and navigate to the project directory:
   ```bash
   cd Finova
   ```

2. Install the required Python dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```

---

## ▶️ Running the Application

1. Apply the existing database migrations to set up the schema:
   ```bash
   python manage.py migrate
   ```

2. Start the Django development server:
   ```bash
   python manage.py runserver
   ```

3. **Success!** You can access the application by navigating to the following URL in your web browser:
   [http://localhost:8000](http://localhost:8000)
