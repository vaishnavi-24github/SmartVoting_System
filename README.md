Smart Voting System through Facial Recognition
This project implements a smart voting system using facial recognition technology. It allows users to register, log in, and vote using their facial features. The backend is built using Python and Flask, with the facial recognition handled by OpenCV and NumPy. The voting data is stored in a MySQL database.

Features
User Registration: Users can register by capturing their face image and entering personal details.

Facial Recognition Login: Users can log in by matching their face to the registered database.

Voting: After login, users can cast their vote securely.

Voting Results: The system displays the voting results once voting ends.

Technologies Used
Python

Flask (GUI)

OpenCV

NumPy

MySQL

GitHub Copilot for code suggestions

Prerequisites
Before running the code, ensure you have the following installed:

Python 3.x: The code is written in Python, so ensure you have Python 3 installed.

Install Python from here.

MySQL Database: You will need a MySQL server to store the user data and voting results.

Install MySQL from here.

Required Python Packages: Install the necessary Python packages listed in the requirements.txt file. You can install them using pip.

Install Dependencies
Clone this repository to your local machine:

bash
Copy
Edit
git clone https://github.com/vaishnavi-24github/Smart_Voting_System.git
cd Smart_Voting_System
Install the dependencies:

bash
Copy
Edit
pip install -r requirements.txt
Requirements File (requirements.txt)
Your requirements.txt should include:

txt
Copy
Edit
Flask==2.0.3
opencv-python==4.5.5.64
numpy==1.21.2
mysql-connector-python==8.0.26
Setting Up MySQL Database
Create a database in MySQL called voting_system:

sql
Copy
Edit
CREATE DATABASE voting_system;
Use the following table structure to store user data and votes:

sql
Copy
Edit
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
Update the database connection details in the app.py file, including your MySQL username, password, and database name.

Running the Application
Step 1: Start MySQL
Ensure your MySQL server is running.

Step 2: Run the Flask App
Start the Flask application to run the voting system:

bash
Copy
Edit
python app.py
The app will be running locally on http://127.0.0.1:5000/. Open this URL in your browser to interact with the voting system.

Registration Process
Open Registration Page: Navigate to the registration page where users can enter their details (e.g., name, email).

Capture Face: The user will be prompted to capture their face. This will store the facial features (encoding) in the database for future login verification.

Run the Model Training Script: After the registration is complete, you need to run the train_models.py script to train the facial recognition model with the captured face data.

Run the following command:

bash
Copy
Edit
python train_models.py
This script will process the registered facial data and train the model for face recognition. The trained model will be saved and used for future login authentication.

Login Process
Facial Recognition Login: Once the model is trained, users can log in by facing the camera. The system will match the live image with the registered face encodings in the database.

Successful Authentication: Once authenticated, users will be able to proceed to cast their vote.

Voting Process
After successful login, users will be able to cast their vote by selecting the desired option.

The vote will be stored securely in the database, associated with the user's ID.

Viewing Results
After the voting period ends, the system will display the results stored in the database.

Troubleshooting
Face Recognition Issues: If the system is not recognizing faces properly, ensure that the camera is properly configured, and the user’s face is well-lit.

Database Connection: If there are errors related to the database, check the connection details in app.py and make sure the MySQL server is running.

Model Training: If you encounter issues while training the facial recognition model, ensure that the train_models.py script has access to sufficient data and that your system has enough resources for model training.

Dependencies: Ensure all dependencies are correctly installed by running pip install -r requirements.txt.
