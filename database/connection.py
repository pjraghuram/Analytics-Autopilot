import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_db_connection():
    """Create and return a database connection"""
    try:
        connection = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            database='postgres',
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
        return connection
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def test_connection():
    """Test database connection"""
    conn = get_db_connection()
    if conn:
        print("Database connection successful!")
        conn.close()
        return True
    else:
        print("Database connection failed!")
        return False

def test_tables():
    """Test if tables exist and show their structure"""
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
        tables = cursor.fetchall()
        print(f"Tables in database: {tables}")
        
        # Show table structure
        cursor.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'file_uploads'
            ORDER BY ordinal_position;
        """)
        columns = cursor.fetchall()
        print(f"file_uploads table structure:")
        for col in columns:
            print(f"  {col[0]} - {col[1]} - Nullable: {col[2]}")
        
        cursor.close()
        conn.close()    

if __name__ == "__main__":
    test_connection()
    test_tables()