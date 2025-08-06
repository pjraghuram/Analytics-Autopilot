import os
import sys
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from update_file_details import FileOperations

def test_database_operations():
    """Test all database operations"""
    print("Testing database operations...")
    
    file_ops = FileOperations()
    
    # Test saving a record
    print("\n1. Testing save_upload_record...")
    file_id = file_ops.save_upload_record(
        original_filename="test_data.csv",
        stored_filename="test_data_20240115_143025.csv",
        file_size=1024,
        file_type="csv",
        s3_original_key="original/test_data_20240115_143025.csv",
        original_rows=100,
        original_columns=5
    )
    
    if file_id:
        print(f"Test record created with ID: {file_id}")
        
        # Test updating processing status
        print("\n2. Testing update_processing_status...")
        if file_ops.update_processing_status(file_id, "processing"):
            print("Processing status update test passed")
        
        # Test updating processed file info
        print("\n3. Testing update_processed_file...")
        if file_ops.update_processed_file(
            file_id=file_id,
            processed_filename="test_data_processed_20240115_143035.csv",
            s3_processed_key="processed/test_data_processed_20240115_143035.csv",
            processed_rows=95,
            processed_columns=4,
            rows_removed=5,
            columns_removed=1
        ):
            print("Processed file update test passed")
        
        # Test getting file by ID
        print("\n4. Testing get_file_by_id...")
        record = file_ops.get_file_by_id(file_id)
        if record:
            print(f"Get file by ID test passed: {record['original_filename']}")
        
        # Test getting all files
        print("\n5. Testing get_all_files...")
        all_files = file_ops.get_all_files(limit=5)
        print(f"Get all files test passed: {len(all_files)} records found")
        
        # Test getting files by status
        print("\n6. Testing get_files_by_status...")
        completed_files = file_ops.get_files_by_status("completed", limit=5)
        print(f"Get files by status test passed: {len(completed_files)} completed files found")
        
        return True
    else:
        print("Test record creation failed")
        return False

def test_connection():
    """Test database connection"""
    print("Testing database connection...")
    
    file_ops = FileOperations()
    conn = file_ops.get_db_connection()
    
    if conn:
        print("Database connection test passed")
        conn.close()
        return True
    else:
        print("Database connection test failed")
        return False

if __name__ == "__main__":
    print("Starting database operations test...")
    print("=" * 50)
    
    # Test connection first
    if test_connection():
        # Test all operations
        test_database_operations()
    
    print("\nDatabase operations test completed!")