from routes.main_routes import get_db_connection

def update_candidates():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Clear existing candidates
        cursor.execute("TRUNCATE TABLE candidates")
        
        # Insert new candidates
        candidates = [
            ('Narendra Modi', 'Bharatiya Janata Party'),
            ('Rahul Gandhi', 'Indian National Congress'),
            ('Arvind Kejriwal', 'Aam Aadmi Party'),
            ('Mamata Banerjee', 'All India Trinamool Congress'),
            ('Nitish Kumar', 'Janata Dal (United)')
        ]
        
        cursor.executemany(
            "INSERT INTO candidates (name, party) VALUES (%s, %s)",
            candidates
        )
        
        conn.commit()
        print("Candidates updated successfully!")
        
    except Exception as e:
        print(f"Error updating candidates: {str(e)}")
        conn.rollback()
    
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    update_candidates() 