import os
import sys
from cloud.S3.uploader import S3FileUploader

def test_s3_connection():
    """Test S3 connection"""
    print("Testing S3 connection...")
    
    uploader = S3FileUploader()
    
    if uploader.test_connection():
        print("S3 connection test passed!")
        return True
    else:
        print("S3 connection test failed!")
        return False

def test_key_generation():
    """Test S3 key generation"""
    print("Testing S3 key generation...")
    
    uploader = S3FileUploader()
    
    # Test original file key
    original_key = uploader.generate_s3_key("sales_data.csv", "original")
    print(f"Generated original key: {original_key}")
    
    # Test processed file key
    processed_key = uploader.generate_s3_key("sales_data.csv", "processed")
    print(f"Generated processed key: {processed_key}")
    
    # Verify format
    assert "original/sales_data_" in original_key
    assert "processed/sales_data_processed_" in processed_key
    
    print("Key generation test passed!")

def test_bucket_listing():
    """Test listing bucket contents"""
    print("Testing bucket listing...")
    
    uploader = S3FileUploader()
    files = uploader.list_bucket_contents()
    
    print(f"Found {len(files)} files in bucket")
    for file_info in files[:5]:  # Show first 5 files
        print(f"  - {file_info['key']} ({file_info['size']} bytes)")

if __name__ == "__main__":
    print("Starting S3 uploader tests...")
    print("=" * 50)
    
    # Test connection
    if test_s3_connection():
        # Test key generation
        test_key_generation()
        
        # Test bucket listing
        test_bucket_listing()
    
    print("\nS3 uploader tests completed!")