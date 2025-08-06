import sys
import os

# Add the parent directory to the path so we can import from src
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.data_processing import preprocess_dataset

# Test your preprocessing function
if __name__ == "__main__":
    try:
        print("Starting preprocessing test...")
        print("=" * 50)
        
        # More robust path handling
        # Get the directory where this test file is located
        test_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Navigate to the test data file
        csv_path = os.path.join(test_dir, '..', 'src', 'test_data.csv')
        
        # Check if file exists
        if not os.path.exists(csv_path):
            print(f"❌ Test data file not found at: {csv_path}")
            print("Please make sure test_data.csv exists in backend/src/")
            exit(1)
        
        print(f"📄 Using test file: {csv_path}")
        
        processed_df = preprocess_dataset(csv_path)
        
        print("\n" + "=" * 50)
        print("TEST COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        
        # Show final results
        print(f"Final dataset shape: {processed_df.shape}")
        print(f"Final columns: {list(processed_df.columns)}")
        print("\nFirst 5 rows of processed data:")
        print(processed_df.head())
        
    except Exception as e:
        print(f"Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()