from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
import os
import base64
import mysql.connector
from datetime import datetime
import cv2
import numpy as np
import re
import glob
from pathlib import Path
import logging
import time
import pickle
from flask import current_app

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

main = Blueprint('main', __name__)

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Panduammulu@24',  # Add your MySQL password here
    'database': 'smart_voting'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

def validate_email(email):
    pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    pattern = r'^[0-9]{10}$'
    return re.match(pattern, phone) is not None

def get_face_detector():
    """Initialize and return the face detector"""
    return cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def extract_face(image_path, face_detector):
    """Extract face from image and convert to grayscale"""
    try:
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not read image: {image_path}")
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = face_detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        if len(faces) == 0:
            raise ValueError(f"No face detected in image: {image_path}")
        
        # Get the first face
        (x, y, w, h) = faces[0]
        
        # Extract face ROI
        face_roi = gray[y:y+h, x:x+w]
        
        # Resize to standard size
        face_roi = cv2.resize(face_roi, (200, 200))
        
        return face_roi
    except Exception as e:
        raise Exception(f"Error processing image {image_path}: {str(e)}")

def load_face_recognizer():
    """Load the trained face recognizer and label mapping"""
    try:
        # Load the trained model
        model_path = os.path.join('model', 'face_recognizer.xml')
        if not os.path.exists(model_path):
            raise FileNotFoundError("Face recognition model not found. Please train the model first.")
        
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read(model_path)
        
        # Load label mapping
        label_map = {}
        label_map_path = os.path.join('model', 'label_mapping.txt')
        if os.path.exists(label_map_path):
            with open(label_map_path, 'r') as f:
                for line in f:
                    idx, voter_id = line.strip().split(':')
                    label_map[int(idx)] = voter_id
        
        return recognizer, label_map
    except Exception as e:
        raise Exception(f"Error loading face recognition model: {str(e)}")

def get_candidates():
    """Get list of candidates from database"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS candidates (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                party VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Check if candidates table is empty
        cursor.execute("SELECT COUNT(*) as count FROM candidates")
        if cursor.fetchone()['count'] == 0:
            # Insert new candidates
            sample_candidates = [
                ('Narendra Modi', 'Bharatiya Janata Party'),
                ('Rahul Gandhi', 'Indian National Congress'),
                ('Arvind Kejriwal', 'Aam Aadmi Party'),
                ('Mamata Banerjee', 'All India Trinamool Congress'),
                ('Nitish Kumar', 'Janata Dal (United)')
            ]
            cursor.executemany(
                "INSERT INTO candidates (name, party) VALUES (%s, %s)",
                sample_candidates
            )
            conn.commit()
        
        cursor.execute("SELECT * FROM candidates")
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

def check_vote_status(voter_id):
    """Check if user has already voted"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS votes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                voter_id VARCHAR(50) NOT NULL,
                candidate_id INT NOT NULL,
                voted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (voter_id) REFERENCES users(voter_id),
                FOREIGN KEY (candidate_id) REFERENCES candidates(id)
            )
        ''')
        
        cursor.execute("SELECT COUNT(*) FROM votes WHERE voter_id = %s", (voter_id,))
        return cursor.fetchone()[0] > 0
    finally:
        cursor.close()
        conn.close()

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name')
            voter_id = request.form.get('voter_id')
            phone = request.form.get('phone')
            email = request.form.get('email')
            gender = request.form.get('gender')
            country = request.form.get('country')
            region = request.form.get('region')
            image_data = request.form.get('imageData')

            print("Received form data:", {
                'name': name,
                'voter_id': voter_id,
                'phone': phone,
                'email': email,
                'gender': gender,
                'country': country,
                'region': region,
                'has_image': bool(image_data)
            })

            # Validate required fields
            if not all([name, voter_id, phone, email, gender, country, region, image_data]):
                missing_fields = []
                if not name: missing_fields.append('name')
                if not voter_id: missing_fields.append('voter ID')
                if not phone: missing_fields.append('phone')
                if not email: missing_fields.append('email')
                if not gender: missing_fields.append('gender')
                if not country: missing_fields.append('country')
                if not region: missing_fields.append('region')
                if not image_data: missing_fields.append('photo')
                
                return jsonify({
                    'success': False,
                    'message': f'Please fill in all required fields: {", ".join(missing_fields)}'
                })

            # Validate email format
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                return jsonify({
                    'success': False,
                    'message': 'Invalid email format'
                })

            # Validate phone format (10 digits)
            if not re.match(r"^\d{10}$", phone):
                return jsonify({
                    'success': False,
                    'message': 'Phone number must be 10 digits'
                })

            # Check if voter ID already exists
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT id FROM users WHERE voter_id = %s", (voter_id,))
            if cursor.fetchone():
                return jsonify({
                    'success': False,
                    'message': 'Voter ID already registered'
                })

            # Check if email already exists
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                return jsonify({
                    'success': False,
                    'message': 'Email already registered'
                })

            # Process and save image
            try:
                # Remove header from base64 string
                image_data = image_data.split(',')[1]
                image_bytes = base64.b64decode(image_data)
                
                # Create filename
                filename = f"{voter_id}_{int(time.time())}.jpg"
                filepath = os.path.join('dataset/uploads', filename)
                
                # Ensure directory exists
                os.makedirs('dataset/uploads', exist_ok=True)
                
                # Save image
                with open(filepath, 'wb') as f:
                    f.write(image_bytes)
                
            except Exception as e:
                print(f"Error saving image: {str(e)}")
                return jsonify({
                    'success': False,
                    'message': 'Error saving image. Please try again.'
                })

            # Save to database
            try:
                cursor.execute("""
                    INSERT INTO users (name, voter_id, phone_number, email, gender, country, region, image_path)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (name, voter_id, phone, email, gender, country, region, filepath))
                conn.commit()
                
                return jsonify({
                    'success': True,
                    'message': 'Registration successful! Redirecting to login...',
                    'redirect': url_for('main.login')
                })
                
            except Exception as e:
                print(f"Database error: {str(e)}")
                return jsonify({
                    'success': False,
                    'message': 'Database error. Please try again.'
                })
            finally:
                cursor.close()
                conn.close()

        except Exception as e:
            print(f"Registration error: {str(e)}")
            return jsonify({
                'success': False,
                'message': 'An error occurred during registration. Please try again.'
            })

    return render_template('register.html')

@main.route('/vote', methods=['GET', 'POST'])
def vote():
    if request.method == 'POST':
        try:
            # Check if this is a vote submission
            if 'candidate_id' in request.form:
                voter_id = request.form.get('voter_id')
                candidate_id = request.form.get('candidate_id')
                
                # Check if user has already voted
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM votes WHERE voter_id = %s", (voter_id,))
                if cursor.fetchone()[0] > 0:
                    return jsonify({
                        'success': False,
                        'message': 'You have already cast your vote'
                    })
                
                # Save vote
                cursor.execute(
                    "INSERT INTO votes (voter_id, candidate_id) VALUES (%s, %s)",
                    (voter_id, candidate_id)
                )
                conn.commit()
                cursor.close()
                conn.close()
                
                return jsonify({
                    'success': True,
                    'message': 'Vote cast successfully!',
                    'redirect': url_for('main.index')
                })

            # Get the image data from the form
            image_data = request.form.get('image_data')
            if not image_data:
                return jsonify({
                    'success': False,
                    'message': 'Please capture your photo'
                })

            # Check if model exists
            model_path = os.path.join(current_app.root_path, 'model', 'face_recognition_model.pkl')
            if not os.path.exists(model_path):
                logger.error("Face recognition model not found at: %s", model_path)
                return jsonify({
                    'success': False,
                    'message': 'Face recognition model needs to be trained. Please contact the administrator.'
                })

            # Process the image data
            try:
                # Remove the data URL prefix
                image_data = image_data.split(',')[1]
                # Decode base64 image
                image_bytes = base64.b64decode(image_data)
                # Convert to numpy array
                nparr = np.frombuffer(image_bytes, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if img is None:
                    logger.error("Failed to decode image data")
                    return jsonify({
                        'success': False,
                        'message': 'Error processing image'
                    })

                # Convert to grayscale
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

                # Initialize face detector
                face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                
                # Detect faces
                faces = face_detector.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(30, 30)
                )
                
                if len(faces) == 0:
                    logger.error("No face detected in the image")
                    return jsonify({
                        'success': False,
                        'message': 'No face detected in the image. Please try again.'
                    })

                # Get the first face
                (x, y, w, h) = faces[0]
                face_roi = gray[y:y+h, x:x+w]
                face_roi = cv2.resize(face_roi, (200, 200))

                # Load the face recognition model
                try:
                    with open(model_path, 'rb') as f:
                        model = pickle.load(f)
                    logger.info("Face recognition model loaded successfully")
                except Exception as e:
                    logger.error("Error loading face recognition model: %s", str(e))
                    return jsonify({
                        'success': False,
                        'message': 'Error loading face recognition model. Please try again.'
                    })

                # Compare with known faces
                min_dist = float('inf')
                matched_voter_id = None

                logger.info("Starting face comparison with %d known faces", len(model['encodings']))
                for known_face, voter_id in zip(model['encodings'], model['voter_ids']):
                    # Calculate difference between faces
                    diff = cv2.absdiff(face_roi, known_face)
                    dist = np.mean(diff)
                    logger.debug("Distance for voter %s: %f", voter_id, dist)
                    
                    if dist < min_dist:
                        min_dist = dist
                        matched_voter_id = voter_id

                logger.info("Minimum distance found: %f for voter %s", min_dist, matched_voter_id)

                # If the minimum distance is too high, face is not recognized
                if min_dist > 50:  # Adjust this threshold as needed
                    logger.error("Face not recognized. Minimum distance: %f", min_dist)
                    return jsonify({
                        'success': False,
                        'message': 'Face not recognized. Please register first or try again.'
                    })

                # Get user from database
                conn = get_db_connection()
                cursor = conn.cursor(dictionary=True)
                cursor.execute('SELECT * FROM users WHERE voter_id = %s', (matched_voter_id,))
                user = cursor.fetchone()
                cursor.close()
                conn.close()

                if not user:
                    logger.error("User not found in database for voter_id: %s", matched_voter_id)
                    return jsonify({
                        'success': False,
                        'message': 'User not found in database. Please register first.'
                    })

                logger.info("User found: %s", user['name'])

                # Get candidates
                conn = get_db_connection()
                cursor = conn.cursor(dictionary=True)
                cursor.execute('SELECT * FROM candidates')
                candidates = cursor.fetchall()
                cursor.close()
                conn.close()

                return jsonify({
                    'success': True,
                    'html': render_template('vote.html', user=user, candidates=candidates)
                })

            except Exception as e:
                logger.error("Error processing image: %s", str(e))
                return jsonify({
                    'success': False,
                    'message': 'Error processing image. Please try again.'
                })

        except Exception as e:
            logger.error("Error in vote route: %s", str(e))
            return jsonify({
                'success': False,
                'message': 'An error occurred. Please try again.'
            })

    # GET request - show voting page
    return render_template('vote.html')

@main.route('/results')
def results():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    # Get all candidates
    cursor.execute('SELECT id, name, party FROM candidates')
    candidates = cursor.fetchall()
    # Get vote counts per candidate
    cursor.execute('SELECT candidate_id, COUNT(*) as vote_count FROM votes GROUP BY candidate_id')
    vote_counts = {row['candidate_id']: row['vote_count'] for row in cursor.fetchall()}
    # Prepare data for table and chart
    results_data = []
    chart_labels = []
    chart_votes = []
    for candidate in candidates:
        count = vote_counts.get(candidate['id'], 0)
        results_data.append({
            'name': candidate['name'],
            'party': candidate['party'],
            'votes': count
        })
        chart_labels.append(candidate['name'])
        chart_votes.append(count)
    cursor.close()
    conn.close()
    return render_template('results.html', results=results_data, chart_labels=chart_labels, chart_votes=chart_votes)

@main.route('/train', methods=['GET', 'POST'])
def train_model():
    if request.method == 'POST':
        try:
            # Initialize face detector
            face_detector = get_face_detector()
            
            # Get all image files from dataset/uploads
            image_dir = os.path.join('dataset', 'uploads')
            image_files = glob.glob(os.path.join(image_dir, '*.jpg'))
            
            if not image_files:
                flash('No training images found in dataset/uploads directory', 'error')
                return redirect(url_for('main.train_model'))
            
            # Initialize lists for faces and labels
            faces = []
            labels = []
            label_dict = {}  # To map filenames to numeric labels
            
            # Process each image
            for idx, image_path in enumerate(image_files):
                try:
                    # Get voter_id from filename (remove .jpg extension)
                    voter_id = Path(image_path).stem
                    
                    # Extract face
                    face = extract_face(image_path, face_detector)
                    
                    # Add to training data
                    faces.append(face)
                    labels.append(idx)
                    label_dict[idx] = voter_id
                    
                except Exception as e:
                    flash(f'Error processing {image_path}: {str(e)}', 'error')
                    continue
            
            if not faces:
                flash('No valid faces found for training', 'error')
                return redirect(url_for('main.train_model'))
            
            # Convert lists to numpy arrays
            faces = np.array(faces, dtype=np.uint8)
            labels = np.array(labels, dtype=np.int32)
            
            # Initialize and train the recognizer
            recognizer = cv2.face.LBPHFaceRecognizer_create()
            recognizer.train(faces, labels)
            
            # Create model directory if it doesn't exist
            model_dir = 'model'
            if not os.path.exists(model_dir):
                os.makedirs(model_dir)
            
            # Save the trained model
            model_path = os.path.join(model_dir, 'face_recognizer.xml')
            recognizer.save(model_path)
            
            # Save label mapping
            label_map_path = os.path.join(model_dir, 'label_mapping.txt')
            with open(label_map_path, 'w') as f:
                for idx, voter_id in label_dict.items():
                    f.write(f"{idx}:{voter_id}\n")
            
            flash(f'Model trained successfully with {len(faces)} faces!', 'success')
            return redirect(url_for('main.index'))
            
        except Exception as e:
            flash(f'Error training model: {str(e)}', 'error')
            return redirect(url_for('main.train_model'))
    
    return render_template('train.html')

@main.route('/admin/users')
def view_users():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get all users
        cursor.execute("""
            SELECT id, name, voter_id, phone_number, email, gender, country, region, created_at 
            FROM users 
            ORDER BY created_at DESC
        """)
        users = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('admin/users.html', users=users)
    except Exception as e:
        flash(f'Error fetching users: {str(e)}', 'error')
        return redirect(url_for('main.index')) 