import os
import sys

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.src.file_handler import FileHandler

def test_complete_workflow():
    """Test the complete workflow with existing test data"""
    print("Testing complete file workflow...")
    
    # Use existing test data file
    test_dir = os.path.dirname(os.path.abspath(__file__))
    test_file_path = os.path.join(test_dir, '..', 'src', 'test_data.csv')
    
    # Check if test file exists
    if not os.path.exists(test_file_path):
        print(f"Error: Test data file not found at: {test_file_path}")
        print("Please make sure test_data.csv exists in backend/src/")
        return {'success': False, 'error': 'Test file not found'}
    
    print(f"Using test file: {test_file_path}")
    
    # Initialize handler and test workflow
    handler = FileHandler()
    result = handler.complete_workflow(test_file_path, "test_data.csv")
    
    if result['success']:
        print("Complete workflow test passed!")
        print(f"   File ID: {result['file_id']}")
        print(f"   Original rows: {result['processing_info']['original_rows']}")
        print(f"   Processed rows: {result['processing_info']['processed_rows']}")
        print(f"   Rows removed: {result['processing_info']['rows_removed']}")
        print(f"   Columns removed: {result['processing_info']['columns_removed']}")
    else:
        print(f"Workflow test failed: {result['error']}")
        print(f"Failed at step: {result.get('step', 'Unknown')}")
    
    return result

def test_individual_steps():
    """Test individual steps of the workflow"""
    print("\nTesting individual workflow steps...")
    
    test_dir = os.path.dirname(os.path.abspath(__file__))
    test_file_path = os.path.join(test_dir, '..', 'src', 'test_data.csv')
    
    if not os.path.exists(test_file_path):
        print("Test file not found, skipping individual tests")
        return
    
    handler = FileHandler()
    
    # Test Step 1: File Upload
    print("Testing file upload...")
    upload_result = handler.handle_file_upload(test_file_path, "test_data.csv")
    
    if upload_result['success']:
        print(f"   Upload test passed! File ID: {upload_result['file_id']}")
        
        # Test Step 2: File Processing
        print("Testing file processing...")
        processing_result = handler.handle_file_processing(
            upload_result['file_id'], 
            test_file_path
        )
        
        if processing_result['success']:
            print("   Processing test passed!")
        else:
            print(f"   Processing test failed: {processing_result['error']}")
    else:
        print(f"   Upload test failed: {upload_result['error']}")

if __name__ == "__main__":
    print("Starting file handler test...")
    print("=" * 50)
    
    # Test complete workflow
    result = test_complete_workflow()
    
    # Test individual steps (optional)
    test_individual_steps()
    
    print("\n" + "=" * 50)
    print(f"File handler test completed!")
    print(f"Overall success: {result['success']}")