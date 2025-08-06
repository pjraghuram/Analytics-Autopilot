import pandas as pd
import numpy as np

def load_dataset(file_path):
    """Load dataset and show shape"""
    print("Loading dataset...")
    df = pd.read_csv(file_path)
    print(f"Dataset shape: {df.shape[0]} rows, {df.shape[1]} columns")
    return df

def detect_data_types(df):
    """Detect and categorize column types"""
    print("\nDetecting data types...")
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()
    
    print(f"Numeric columns: {len(numeric_cols)}")
    print(f"Categorical columns: {len(categorical_cols)}")
    
    if len(numeric_cols) > 0:
        print(f"Numeric column names: {numeric_cols}")
    if len(categorical_cols) > 0:
        print(f"Categorical column names: {categorical_cols}")
    
    return numeric_cols, categorical_cols

def generate_summary(df, numeric_cols, categorical_cols):
    """Generate comprehensive data summary"""
    print("\nGenerating data summary...")
    
    # Numeric summary
    if len(numeric_cols) > 0:
        print("Numeric columns summary:")
        numeric_summary = df[numeric_cols].describe()
        print(numeric_summary)
    
    # Categorical summary
    if len(categorical_cols) > 0:
        print("\nCategorical columns summary:")
        for col in categorical_cols:
            print(f"\n{col}:")
            value_counts = df[col].value_counts().head(5)
            print(value_counts)

def remove_duplicates(df):
    """Remove duplicate rows and columns"""
    print("\nRemoving duplicates...")
    initial_rows = len(df)
    
    # Remove duplicate rows
    df = df.drop_duplicates()
    rows_after_duplicate_removal = len(df)
    
    # Remove duplicate columns
    df = df.loc[:, ~df.columns.duplicated()]
    
    print(f"Removed {initial_rows - rows_after_duplicate_removal} duplicate rows")
    print(f"Dataset shape after removing duplicates: {df.shape[0]} rows, {df.shape[1]} columns")
    
    return df

def analyze_missing_values(df):
    """Analyze and report missing values"""
    print("\nAnalyzing missing values...")
    null_info = df.isnull().sum()
    null_percentages = (df.isnull().sum() / len(df)) * 100
    
    print("Missing values per column:")
    for col in df.columns:
        null_count = null_info[col]
        null_pct = null_percentages[col]
        if null_count > 0:
            print(f"{col}: {null_count} missing values ({null_pct:.2f}%)")
    
    return null_percentages

def handle_missing_values(df, numeric_cols, categorical_cols, null_percentages):
    """Handle missing values based on thresholds"""
    print("\nHandling missing values...")
    
    columns_to_drop = []
    
    for col in df.columns:
        null_pct = null_percentages[col]
        
        if null_pct > 50:
            # Drop columns with more than 50% missing values
            columns_to_drop.append(col)
            print(f"Dropping column '{col}' - {null_pct:.2f}% missing values")
        
        elif null_pct < 10 and null_pct > 0:
            # Fill missing values for columns with less than 10% missing
            if col in numeric_cols:
                # Fill numeric columns with median
                median_value = df[col].median()
                df[col].fillna(median_value, inplace=True)
                print(f"Filled '{col}' with median value: {median_value}")
            else:
                # Fill categorical columns with mode
                if len(df[col].dropna()) > 0:
                    mode_value = df[col].mode()[0]
                    df[col].fillna(mode_value, inplace=True)
                    print(f"Filled '{col}' with mode value: {mode_value}")
        
        elif 10 <= null_pct <= 50:
            # Fill missing values between 10-50%
            if col in numeric_cols:
                # Use interpolation for numeric columns
                df[col].interpolate(inplace=True)
                # Fill any remaining nulls with median
                df[col].fillna(df[col].median(), inplace=True)
                print(f"Filled '{col}' using interpolation")
            else:
                # Fill categorical columns with 'Unknown'
                df[col].fillna('Unknown', inplace=True)
                print(f"Filled '{col}' with 'Unknown'")
    
    # Drop columns that have too many missing values
    if columns_to_drop:
        df.drop(columns=columns_to_drop, inplace=True)
        print(f"Dropped {len(columns_to_drop)} columns with excessive missing values")
    
    return df

def preprocess_dataset(file_path):
    """Main preprocessing pipeline using method calls"""
    
    # Step 1: Load dataset
    df = load_dataset(file_path)
    
    # Step 2: Detect data types
    numeric_cols, categorical_cols = detect_data_types(df)
    
    # Step 3: Generate summary
    generate_summary(df, numeric_cols, categorical_cols)
    
    # Step 4: Remove duplicates
    df = remove_duplicates(df)
    
    # Step 5: Analyze missing values
    null_percentages = analyze_missing_values(df)
    
    # Step 6: Handle missing values
    df = handle_missing_values(df, numeric_cols, categorical_cols, null_percentages)
    
    # Final summary
    print("\nPreprocessing completed!")
    print(f"Final dataset shape: {df.shape[0]} rows, {df.shape[1]} columns")
    
    # Check if there are any remaining null values
    remaining_nulls = df.isnull().sum().sum()
    print(f"Remaining null values: {remaining_nulls}")
    
    return df
