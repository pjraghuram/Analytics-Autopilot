import boto3
import os
from datetime import datetime
from dotenv import load_dotenv
from botocore.exceptions import ClientError

# Load environment variables
load_dotenv()

class S3FileUploader:
    def __init__(self):
        """Initialize S3 client"""
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION')
        )
        self.bucket_name = os.getenv('AWS_S3_BUCKET_NAME')
    
    def generate_s3_key(self, filename, file_type="original"):
        """
        Generate S3 key with datetime
        
        Args:
            filename (str): Original filename (e.g., 'sales_data.csv')
            file_type (str): 'original' or 'processed'
        
        Returns:
            str: S3 key (e.g., 'original/sales_data_20240115_143025.csv')
        """
        # Get current datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Split filename and extension
        name, ext = os.path.splitext(filename)
        
        # Create new filename with timestamp
        if file_type == "processed":
            new_filename = f"{name}_processed_{timestamp}{ext}"
        else:
            new_filename = f"{name}_{timestamp}{ext}"
        
        # Create S3 key with folder structure
        s3_key = f"{file_type}/{new_filename}"
        
        return s3_key
    
    def upload_file(self, file_path, original_filename, file_type="original"):
        """
        Upload file to S3
        
        Args:
            file_path (str): Local path to file
            original_filename (str): Original filename from user
            file_type (str): 'original' or 'processed'
        
        Returns:
            dict: Upload result with S3 key and URL
        """
        try:
            # Generate S3 key
            s3_key = self.generate_s3_key(original_filename, file_type)
            
            print(f"Attempting to upload file: {file_path}")
            print(f"To S3 bucket: {self.bucket_name}")
            print(f"With S3 key: {s3_key}")
            
            # Upload file to S3
            self.s3_client.upload_file(
                file_path,
                self.bucket_name,
                s3_key,
                ExtraArgs={'ContentType': 'text/csv'}
            )
            
            # Generate S3 URL
            s3_url = f"https://{self.bucket_name}.s3.{os.getenv('AWS_REGION')}.amazonaws.com/{s3_key}"
            
            print(f"File uploaded successfully to S3: {s3_key}")
            
            return {
                'success': True,
                's3_key': s3_key,
                's3_url': s3_url,
                'bucket': self.bucket_name,
                'filename': os.path.basename(s3_key)
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            print(f"AWS Error Code: {error_code}")
            print(f"Error Message: {e.response['Error']['Message']}")
            print(f"Error uploading file to S3: {e}")
            return {
                'success': False,
                'error': str(e),
                'error_code': error_code
            }
        except Exception as e:
            print(f"Unexpected error during upload: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def upload_original_file(self, file_path, original_filename):
        """Upload original file to S3"""
        return self.upload_file(file_path, original_filename, "original")
    
    def upload_processed_file(self, file_path, original_filename):
        """Upload processed file to S3"""
        return self.upload_file(file_path, original_filename, "processed")
    
    def test_connection(self):
        """Test S3 connection"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            print(f"Successfully connected to S3 bucket: {self.bucket_name}")
            return True
        except ClientError as e:
            print(f"Error connecting to S3: {e}")
            return False
    
    def list_bucket_contents(self):
        """List all files in the S3 bucket"""
        try:
            response = self.s3_client.list_objects_v2(Bucket=self.bucket_name)
            
            if 'Contents' in response:
                files = []
                for obj in response['Contents']:
                    files.append({
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified']
                    })
                return files
            else:
                return []
                
        except ClientError as e:
            print(f"Error listing bucket contents: {e}")
            return []
    
    def delete_file(self, s3_key):
        """Delete a file from S3"""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            print(f"Successfully deleted file: {s3_key}")
            return True
        except ClientError as e:
            print(f"Error deleting file: {e}")
            return False
    
    def get_file_url(self, s3_key, expiration=3600):
        """Generate a presigned URL for file download"""
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            print(f"Error generating presigned URL: {e}")
            return None