
# 🗳️ Smart Voting System through Facial Recognition

This project implements a smart voting system using facial recognition technology. It allows users to register, log in, and vote using their facial features. The backend is built using **Python** and **Flask**, with the facial recognition handled by **OpenCV** and **NumPy**. The voting data is stored in a **MySQL** database.

---

## 🚀 Features

- **User Registration**: Register with facial image and personal details.
- **Facial Recognition Login**: Secure login using facial recognition.
- **Voting**: Cast vote after authentication.
- **Voting Results**: Display results after voting ends.

---

## 🛠️ Technologies Used

- Python  
- Flask (GUI)  
- OpenCV  
- NumPy  
- MySQL  
- GitHub Copilot (for code suggestions)

---

## 📋 Prerequisites

Make sure you have the following installed:

- **Python 3.x**: [Download here](https://www.python.org/downloads/)
- **MySQL Server**: [Download here](https://dev.mysql.com/downloads/)
- **Python Packages**: Installed from `requirements.txt`

---

## 🧰 Install Dependencies

### 1. Clone this repository:

```bash
git clone https://github.com/vaishnavi-24github/Smart_Voting_System.git
cd Smart_Voting_System
```

### 2. Install the dependencies:

```bash
pip install -r requirements.txt
```

---

## 📄 Requirements File (`requirements.txt`)

```txt
Flask==2.0.3
opencv-python==4.5.5.64
numpy==1.21.2
mysql-connector-python==8.0.26
```

---

## 🗃️ Setting Up MySQL Database

### 1. Create a database:

```sql
CREATE DATABASE voting_system;
```

### 2. Create required tables:

```sql
CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100),
  email VARCHAR(100),
  face_encoding BLOB
);

CREATE TABLE votes (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT,
  vote VARCHAR(100),
  FOREIGN KEY (user_id) REFERENCES users(id)
);
```

Update MySQL credentials in `app.py` as needed.

---

## ▶️ Running the Application

### Step 1: Start MySQL

Ensure MySQL server is running.

### Step 2: Run the Flask App

```bash
python app.py
```

Visit [http://127.0.0.1:5000/](http://127.0.0.1:5000/) in your browser.

---

## 🧾 Registration Process

1. Go to the **Registration Page** and enter user details.
2. **Capture Face** using webcam (saves face encoding).
3. **Train Model** with:

```bash
python train_models.py
```

---

## 🔐 Login Process

1. Open the **Login Page**.
2. Facial recognition is used to verify identity.
3. On success, user proceeds to vote.

---

## 🗳️ Voting Process

- Select a candidate after login.
- Vote is stored securely in the database.

---

## 📊 Viewing Results

- After voting ends, results are displayed from the database.

---

## 🧩 Troubleshooting

- **Face Not Recognized**: Ensure good lighting and proper camera setup.
- **Database Errors**: Double-check `app.py` connection settings.
- **Training Issues**: Check if facial data exists and system has enough memory.
- **Dependency Issues**: Run:

```bash
pip install -r requirements.txt
```

---

© 2025 Smart Voting System

