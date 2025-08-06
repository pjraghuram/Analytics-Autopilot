import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_tables():
    """Create database tables"""
    try:
        # Connect to database
        connection = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            database='postgres',
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
        
        cursor = connection.cursor()
        
        # Read SQL file
        with open('tables/file_storage.sql', 'r') as sql_file:
            sql_commands = sql_file.read()
        
        # Execute SQL commands
        cursor.execute(sql_commands)
        connection.commit()
        
        print("Tables created successfully!")
        
        # Close connections
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"Error creating tables: {e}")

if __name__ == "__main__":
    create_tables()