import os
import cv2
import numpy as np
import mysql.connector
from pathlib import Path
import logging
import pickle

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Panduammulu@24',
    'database': 'smart_voting'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

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

def train_model():
    try:
        # Initialize face detector
        face_detector = get_face_detector()
        
        # Get all registered users from database
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT voter_id, image_path FROM users")
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if not users:
            logger.error("No registered users found in database")
            return False
        
        # Initialize lists for faces and labels
        known_face_encodings = []
        known_voter_ids = []
        
        # Process each user's image
        for user in users:
            try:
                image_path = user['image_path']
                voter_id = user['voter_id']
                
                if not os.path.exists(image_path):
                    logger.warning(f"Image not found for user {voter_id}: {image_path}")
                    continue
                
                # Extract face
                face = extract_face(image_path, face_detector)
                
                # Add to training data
                known_face_encodings.append(face)
                known_voter_ids.append(voter_id)
                
                logger.info(f"Processed image for user {voter_id}")
                
            except Exception as e:
                logger.error(f"Error processing user {user['voter_id']}: {str(e)}")
                continue
        
        if not known_face_encodings:
            logger.error("No valid faces found for training")
            return False
        
        # Create model dictionary
        model = {
            'encodings': known_face_encodings,
            'voter_ids': known_voter_ids
        }
        
        # Create model directory if it doesn't exist
        model_dir = 'model'
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)
        
        # Save the trained model
        model_path = os.path.join(model_dir, 'face_recognition_model.pkl')
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        
        logger.info(f"Model trained successfully with {len(known_face_encodings)} faces!")
        return True
        
    except Exception as e:
        logger.error(f"Error training model: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Starting face recognition model training...")
    if train_model():
        logger.info("Training completed successfully!")
    else:
        logger.error("Training failed!") 