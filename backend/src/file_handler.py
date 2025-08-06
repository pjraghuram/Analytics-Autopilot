import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from cloud.S3.uploader import S3FileUploader
from database.update_file_details import FileOperations
from backend.src.data_processing import preprocess_dataset
from backend.src.llm_analyzer import LLMAnalyzer

# Load environment variables
load_dotenv()

class FileHandler:
    def __init__(self):
        """Initialize S3 uploader and database operations"""
        self.s3_uploader = S3FileUploader()
        self.file_ops = FileOperations()
        self.llm_analyzer = LLMAnalyzer()
    
    def handle_file_upload(self, file_path, original_filename):
        """
        Complete workflow for file upload: S3 + Database
        
        Args:
            file_path (str): Local path to uploaded file
            original_filename (str): Original filename from user
        
        Returns:
            dict: Result with file_id and upload info
        """
        print(f"Starting file upload workflow for: {original_filename}")
        
        try:
            # Step 1: Get file information
            file_size = os.path.getsize(file_path)
            file_extension = os.path.splitext(original_filename)[1].lower()
            file_type = file_extension.replace('.', '')
            
            print(f"File info - Size: {file_size} bytes, Type: {file_type}")
            
            # Step 2: Get data dimensions (rows, columns)
            try:
                import pandas as pd
                df = pd.read_csv(file_path)
                original_rows, original_columns = df.shape
                print(f"Data dimensions: {original_rows} rows, {original_columns} columns")
            except Exception as e:
                print(f"Could not read file dimensions: {e}")
                original_rows, original_columns = None, None
            
            # Step 3: Upload original file to S3
            print("Uploading original file to S3...")
            s3_result = self.s3_uploader.upload_original_file(file_path, original_filename)
            
            if not s3_result['success']:
                return {
                    'success': False,
                    'error': f"S3 upload failed: {s3_result['error']}",
                    'step': 'S3_upload'
                }
            
            print(f"S3 upload successful: {s3_result['s3_key']}")
            
            # Step 4: Save record to database
            print("Saving record to database...")
            file_id = self.file_ops.save_upload_record(
                original_filename=original_filename,
                stored_filename=s3_result['filename'],
                file_size=file_size,
                file_type=file_type,
                s3_original_key=s3_result['s3_key'],
                original_rows=original_rows,
                original_columns=original_columns
            )
            
            if not file_id:
                return {
                    'success': False,
                    'error': "Database save failed",
                    'step': 'database_save'
                }
            
            print(f"Database record created with ID: {file_id}")
            
            # Step 5: Return success result
            return {
                'success': True,
                'file_id': file_id,
                's3_key': s3_result['s3_key'],
                's3_url': s3_result['s3_url'],
                'stored_filename': s3_result['filename'],
                'original_rows': original_rows,
                'original_columns': original_columns,
                'upload_datetime': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Unexpected error in file upload workflow: {e}")
            return {
                'success': False,
                'error': str(e),
                'step': 'unexpected_error'
            }
    
    def handle_file_processing(self, file_id, original_file_path):
        """
        Complete workflow for file processing: Process + S3 + Database
        
        Args:
            file_id (int): Database record ID
            original_file_path (str): Path to original file
        
        Returns:
            dict: Result with processing info
        """
        print(f"Starting file processing workflow for file ID: {file_id}")
        
        try:
            # Step 1: Update processing status to 'processing'
            print("Updating processing status to 'processing'...")
            if not self.file_ops.update_processing_status(file_id, "processing"):
                return {
                    'success': False,
                    'error': "Failed to update processing status",
                    'step': 'status_update'
                }
            
            # Step 2: Process the file
            print("Processing file data...")
            processed_df = preprocess_dataset(original_file_path)
            
            if processed_df is None or processed_df.empty:
                self.file_ops.update_processing_status(file_id, "failed")
                return {
                    'success': False,
                    'error': "File processing returned empty result",
                    'step': 'data_processing'
                }
            
            # Step 3: Save processed file temporarily
            original_filename = self.file_ops.get_file_by_id(file_id)['original_filename']
            processed_file_path = f"temp_processed_{original_filename}"
            processed_df.to_csv(processed_file_path, index=False)
            
            print(f"Processed file saved temporarily: {processed_file_path}")
            
            # Step 4: Upload processed file to S3
            print("Uploading processed file to S3...")
            s3_result = self.s3_uploader.upload_processed_file(processed_file_path, original_filename)
            
            if not s3_result['success']:
                self.file_ops.update_processing_status(file_id, "failed")
                return {
                    'success': False,
                    'error': f"S3 upload failed: {s3_result['error']}",
                    'step': 'S3_processed_upload'
                }
            
            print(f"Processed file uploaded to S3: {s3_result['s3_key']}")
            
            # Step 5: LLM Analysis 
            print("Starting LLM analysis...")
            llm_result = self.llm_analyzer.analyze_processed_data(processed_file_path, file_id)
            
            if not llm_result['success']:
                print(f"LLM analysis failed: {llm_result['error']}")
                # Continue with workflow even if LLM fails
                llm_result = {
                    'success': False,
                    'error': llm_result['error'],
                    'column_descriptions': '',
                    'plot_codes': [],
                    'insights_summary': 'LLM analysis failed'
                }
            else:
                print("LLM analysis completed successfully!")
            
            # Step 6: Calculate processing stats
            original_record = self.file_ops.get_file_by_id(file_id)
            original_rows = original_record['original_rows'] or 0
            original_columns = original_record['original_columns'] or 0
            
            processed_rows, processed_columns = processed_df.shape
            rows_removed = max(0, original_rows - processed_rows)
            columns_removed = max(0, original_columns - processed_columns)
            
            # Step 7: Update database with processed file info
            print("Updating database with processed file info...")
            if not self.file_ops.update_processed_file(
                file_id=file_id,
                processed_filename=s3_result['filename'],
                s3_processed_key=s3_result['s3_key'],
                processed_rows=processed_rows,
                processed_columns=processed_columns,
                rows_removed=rows_removed,
                columns_removed=columns_removed
            ):
                return {
                    'success': False,
                    'error': "Failed to update processed file info in database",
                    'step': 'database_update'
                }
            
            # Step 8: Clean up temporary file
            if os.path.exists(processed_file_path):
                os.remove(processed_file_path)
                print(f"Cleaned up temporary file: {processed_file_path}")
            
            print("File processing completed successfully!")
            
            return {
                'success': True,
                'file_id': file_id,
                'processed_s3_key': s3_result['s3_key'],
                'processed_s3_url': s3_result['s3_url'],
                'processed_filename': s3_result['filename'],
                'original_rows': original_rows,
                'original_columns': original_columns,
                'processed_rows': processed_rows,
                'processed_columns': processed_columns,
                'rows_removed': rows_removed,
                'columns_removed': columns_removed,
                'processing_datetime': datetime.now().isoformat(),
                'llm_analysis': llm_result
            }
            
        except Exception as e:
            print(f"Unexpected error in file processing workflow: {e}")
            self.file_ops.update_processing_status(file_id, "failed")
            return {
                'success': False,
                'error': str(e),
                'step': 'unexpected_error'
            }
    
    def complete_workflow(self, file_path, original_filename):
        """
        Complete workflow: Upload + Process (Steps 1 & 2 combined)
        
        Args:
            file_path (str): Local path to uploaded file
            original_filename (str): Original filename from user
        
        Returns:
            dict: Complete workflow result
        """
        print(f"Starting complete workflow for: {original_filename}")
        
        # Step 1: Handle file upload
        upload_result = self.handle_file_upload(file_path, original_filename)
        
        if not upload_result['success']:
            return upload_result
        
        file_id = upload_result['file_id']
        
        # Step 2: Handle file processing
        processing_result = self.handle_file_processing(file_id, file_path)
        
        if not processing_result['success']:
            return processing_result
        
        # Combine results
        return {
            'success': True,
            'file_id': file_id,
            'upload_info': upload_result,
            'processing_info': processing_result,
            'message': f"Complete workflow successful for {original_filename}"
        }