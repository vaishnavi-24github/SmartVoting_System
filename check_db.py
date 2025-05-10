import mysql.connector
from tabulate import tabulate
from datetime import datetime

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='Panduammulu@24',
        database='smart_voting'
    )

def view_all_users():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get all users
        cursor.execute("""
            SELECT 
                id,
                name,
                voter_id,
                phone_number,
                email,
                gender,
                country,
                region,
                created_at
            FROM users 
            ORDER BY created_at DESC
        """)
        
        users = cursor.fetchall()
        
        if not users:
            print("No users found in the database.")
            return
        
        # Format the data for display
        headers = ["ID", "Name", "Voter ID", "Phone", "Email", "Gender", "Country", "Region", "Registration Date"]
        table_data = []
        
        for user in users:
            table_data.append([
                user['id'],
                user['name'],
                user['voter_id'],
                user['phone_number'],
                user['email'],
                user['gender'],
                user['country'],
                user['region'],
                user['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        # Print the table
        print("\nRegistered Users:")
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        print(f"\nTotal Users: {len(users)}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

def search_user(voter_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("""
            SELECT * FROM users WHERE voter_id = %s
        """, (voter_id,))
        
        user = cursor.fetchone()
        
        if user:
            print("\nUser Details:")
            print(f"ID: {user['id']}")
            print(f"Name: {user['name']}")
            print(f"Voter ID: {user['voter_id']}")
            print(f"Phone: {user['phone_number']}")
            print(f"Email: {user['email']}")
            print(f"Gender: {user['gender']}")
            print(f"Country: {user['country']}")
            print(f"Region: {user['region']}")
            print(f"Registration Date: {user['created_at'].strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"No user found with voter ID: {voter_id}")
            
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    while True:
        print("\nDatabase Check Options:")
        print("1. View all users")
        print("2. Search user by voter ID")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ")
        
        if choice == '1':
            view_all_users()
        elif choice == '2':
            voter_id = input("Enter voter ID to search: ")
            search_user(voter_id)
        elif choice == '3':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.") 