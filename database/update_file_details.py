import psycopg2
import os
from datetime import datetime
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

# Load environment variables
load_dotenv()

class FileOperations:
    def __init__(self):
        """Initialize database connection parameters"""
        self.db_params = {
            'host': os.getenv('DB_HOST'),
            'port': os.getenv('DB_PORT'),
            'database': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD')
        }
    
    def get_db_connection(self):
        """Create and return database connection"""
        try:
            connection = psycopg2.connect(**self.db_params)
            return connection
        except Exception as e:
            print(f"Error connecting to database: {e}")
            return None
    
    def save_upload_record(self, original_filename, stored_filename, file_size, file_type, s3_original_key, original_rows=None, original_columns=None):
        """
        Save original file upload record to database
        
        Args:
            original_filename (str): User's original filename
            stored_filename (str): Filename stored in S3
            file_size (int): File size in bytes
            file_type (str): File extension (csv, xlsx, etc.)
            s3_original_key (str): S3 key for original file
            original_rows (int): Number of rows in original file
            original_columns (int): Number of columns in original file
        
        Returns:
            int: File record ID if successful, None if failed
        """
        conn = self.get_db_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            
            # Prepare original shape string
            original_shape = f"({original_rows}, {original_columns})" if original_rows and original_columns else None
            
            # Insert record
            insert_query = """
                INSERT INTO file_uploads (
                    original_filename, stored_filename, file_size, file_type,
                    upload_datetime, upload_status, original_rows, original_columns,
                    original_shape, is_processed, processing_status, s3_original_key,
                    created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                ) RETURNING id;
            """
            
            current_time = datetime.now()
            
            cursor.execute(insert_query, (
                original_filename,
                stored_filename,
                file_size,
                file_type,
                current_time,           # upload_datetime
                'uploaded',             # upload_status
                original_rows,
                original_columns,
                original_shape,
                False,                  # is_processed
                'pending',              # processing_status
                s3_original_key,
                current_time,           # created_at
                current_time            # updated_at
            ))
            
            # Get the inserted record ID
            file_id = cursor.fetchone()[0]
            conn.commit()
            
            print(f"File record saved to database with ID: {file_id}")
            print(f"   Original filename: {original_filename}")
            print(f"   S3 key: {s3_original_key}")
            
            cursor.close()
            conn.close()
            
            return file_id
            
        except Exception as e:
            print(f"Error saving upload record: {e}")
            if conn:
                conn.rollback()
                conn.close()
            return None
    
    def update_processing_status(self, file_id, status, processing_datetime=None):
        """
        Update processing status of a file
        
        Args:
            file_id (int): File record ID
            status (str): 'processing', 'completed', 'failed'
            processing_datetime (datetime): When processing started/completed
        
        Returns:
            bool: True if successful, False if failed
        """
        conn = self.get_db_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            
            # Use current time if not provided
            if processing_datetime is None:
                processing_datetime = datetime.now()
            
            update_query = """
                UPDATE file_uploads 
                SET processing_status = %s, 
                    processing_datetime = %s,
                    updated_at = %s
                WHERE id = %s;
            """
            
            cursor.execute(update_query, (
                status,
                processing_datetime,
                datetime.now(),
                file_id
            ))
            
            conn.commit()
            
            print(f"Processing status updated to '{status}' for file ID: {file_id}")
            
            cursor.close()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"Error updating processing status: {e}")
            if conn:
                conn.rollback()
                conn.close()
            return False
    
    def update_processed_file(self, file_id, processed_filename, s3_processed_key, processed_rows=None, processed_columns=None, rows_removed=None, columns_removed=None):
        """
        Update record with processed file information
        
        Args:
            file_id (int): File record ID
            processed_filename (str): Name of processed file
            s3_processed_key (str): S3 key for processed file
            processed_rows (int): Number of rows in processed file
            processed_columns (int): Number of columns in processed file
            rows_removed (int): Number of rows removed during processing
            columns_removed (int): Number of columns removed during processing
        
        Returns:
            bool: True if successful, False if failed
        """
        conn = self.get_db_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            
            # Prepare processed shape string
            processed_shape = f"({processed_rows}, {processed_columns})" if processed_rows and processed_columns else None
            
            update_query = """
                UPDATE file_uploads 
                SET processed_filename = %s,
                    s3_processed_key = %s,
                    processed_rows = %s,
                    processed_columns = %s,
                    processed_shape = %s,
                    rows_removed = %s,
                    columns_removed = %s,
                    is_processed = %s,
                    processing_status = %s,
                    updated_at = %s
                WHERE id = %s;
            """
            
            cursor.execute(update_query, (
                processed_filename,
                s3_processed_key,
                processed_rows,
                processed_columns,
                processed_shape,
                rows_removed,
                columns_removed,
                True,                   # is_processed
                'completed',            # processing_status
                datetime.now(),         # updated_at
                file_id
            ))
            
            conn.commit()
            
            print(f"Processed file info updated for file ID: {file_id}")
            print(f"   Processed filename: {processed_filename}")
            print(f"   S3 processed key: {s3_processed_key}")
            print(f"   Rows: {processed_rows}, Columns: {processed_columns}")
            
            cursor.close()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"Error updating processed file info: {e}")
            if conn:
                conn.rollback()
                conn.close()
            return False
    
    def get_file_by_id(self, file_id):
        """
        Get file record by ID
        
        Args:
            file_id (int): File record ID
        
        Returns:
            dict: File record or None if not found
        """
        conn = self.get_db_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            select_query = "SELECT * FROM file_uploads WHERE id = %s;"
            cursor.execute(select_query, (file_id,))
            
            record = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            return dict(record) if record else None
            
        except Exception as e:
            print(f"Error getting file by ID: {e}")
            if conn:
                conn.close()
            return None
    
    def get_all_files(self, limit=50):
        """
        Get all file records (most recent first)
        
        Args:
            limit (int): Maximum number of records to return
        
        Returns:
            list: List of file records
        """
        conn = self.get_db_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            select_query = """
                SELECT * FROM file_uploads 
                ORDER BY upload_datetime DESC 
                LIMIT %s;
            """
            cursor.execute(select_query, (limit,))
            
            records = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return [dict(record) for record in records]
            
        except Exception as e:
            print(f"Error getting all files: {e}")
            if conn:
                conn.close()
            return []
    
    # def delete_file_record(self, file_id):
    #     """
    #     Delete a file record from database
        
    #     Args:
    #         file_id (int): File record ID to delete
        
    #     Returns:
    #         bool: True if successful, False if failed
    #     """
    #     conn = self.get_db_connection()
    #     if not conn:
    #         return False
        
    #     try:
    #         cursor = conn.cursor()
            
    #         delete_query = "DELETE FROM file_uploads WHERE id = %s;"
    #         cursor.execute(delete_query, (file_id,))
            
    #         conn.commit()
            
    #         if cursor.rowcount > 0:
    #             print(f"Successfully deleted file record with ID: {file_id}")
    #             cursor.close()
    #             conn.close()
    #             return True
    #         else:
    #             print(f"No record found with ID: {file_id}")
    #             cursor.close()
    #             conn.close()
    #             return False
            
    #     except Exception as e:
    #         print(f"Error deleting file record: {e}")
    #         if conn:
    #             conn.rollback()
    #             conn.close()
    #         return False
    
    # def get_files_by_status(self, status, limit=50):
        """
        Get files by processing status
        
        Args:
            status (str): Processing status ('pending', 'processing', 'completed', 'failed')
            limit (int): Maximum number of records to return
        
        Returns:
            list: List of file records with specified status
        """
        conn = self.get_db_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            select_query = """
                SELECT * FROM file_uploads 
                WHERE processing_status = %s
                ORDER BY upload_datetime DESC 
                LIMIT %s;
            """
            cursor.execute(select_query, (status, limit))
            
            records = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return [dict(record) for record in records]
            
        except Exception as e:
            print(f"Error getting files by status: {e}")
            if conn:
                conn.close()
            return []