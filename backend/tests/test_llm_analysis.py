import sys
import os

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.src.llm_analyzer import LLMAnalyzer
import pandas as pd

def test_llm_analyzer():
    """Test LLM analyzer functionality"""
    print("Starting LLM analyzer test...")
    
    analyzer = LLMAnalyzer()
    
    # Create sample data directly in test
    sample_data = {
        'name': ['John', 'Jane', 'Bob', 'Alice', 'Charlie'],
        'age': [25, 30, 35, 28, 32],
        'salary': [50000, 60000, 70000, 55000, 65000],
        'department': ['IT', 'HR', 'IT', 'Marketing', 'HR']
    }
    
    df = pd.DataFrame(sample_data)
    df.to_csv('test_sample.csv', index=False)
    
    # Test analysis
    result = analyzer.analyze_processed_data('test_sample.csv')
    
    # Clean up
    if os.path.exists('test_sample.csv'):
        os.remove('test_sample.csv')
    
    if result['success']:
        print("LLM analysis test passed!")
        print("Column Descriptions:")
        print(result['column_descriptions'])
        print(f"\nGenerated {len(result['plot_codes'])} visualizations")
        print("\nInsights:")
        print(result['insights_summary'])
    else:
        print(f"LLM analysis test failed: {result['error']}")
    
    print(f"\nLLM analyzer test completed!")
    print(f"Success: {result['success']}")
    
    return result

if __name__ == "__main__":
    test_llm_analyzer()