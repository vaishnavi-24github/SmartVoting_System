from flask import Flask, render_template, flash
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for flash messages

# Configure upload folder for face images
UPLOAD_FOLDER = os.path.join('dataset', 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Import and register blueprint
from routes import main_routes
app.register_blueprint(main_routes.main)

if __name__ == '__main__':
    app.run(debug=True) 