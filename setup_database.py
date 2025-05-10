import mysql.connector
from mysql.connector import Error

def create_database():
    try:
        # First, connect to MySQL server without specifying a database
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Panduammulu@24'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Create database
            print("Creating database...")
            cursor.execute("CREATE DATABASE IF NOT EXISTS smart_voting")
            print("Database created successfully!")
            
            # Use the database
            cursor.execute("USE smart_voting")
            
            # Create users table
            print("Creating users table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    voter_id VARCHAR(50) UNIQUE NOT NULL,
                    phone_number VARCHAR(15) NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    gender VARCHAR(10) NOT NULL,
                    country VARCHAR(100) NOT NULL,
                    region VARCHAR(50) NOT NULL,
                    image_path VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("Users table created successfully!")
            
            # Verify the table was created
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print("\nTables in database:")
            for table in tables:
                print(f"- {table[0]}")
            
            # Show table structure
            cursor.execute("DESCRIBE users")
            columns = cursor.fetchall()
            print("\nTable structure:")
            for column in columns:
                print(f"- {column[0]}: {column[1]}")
            
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("\nMySQL connection closed.")

if __name__ == "__main__":
    create_database() 