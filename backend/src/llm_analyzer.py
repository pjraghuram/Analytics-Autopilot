import openai
import pandas as pd
import os
from datetime import datetime
from dotenv import load_dotenv
import json
import sys

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Load environment variables
load_dotenv()

class LLMAnalyzer:
    def __init__(self):
        """Initialize OpenAI client"""
        api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        if not api_key.startswith('sk-'):
            raise ValueError("Invalid OpenAI API key format")
        
        # Set API key for OpenAI 0.28
        openai.api_key = api_key
        self.model = "gpt-3.5-turbo"
        
        print("OpenAI client initialized successfully")
    
    def prepare_data_summary(self, df):
        """
        Prepare dataset summary for LLM analysis
        
        Args:
            df (DataFrame): Processed dataset
        
        Returns:
            str: Formatted data summary for LLM
        """
        # Basic dataset info
        rows, cols = df.shape
        
        # Column information
        column_info = []
        for col in df.columns:
            dtype = str(df[col].dtype)
            non_null_count = df[col].count()
            unique_count = df[col].nunique()
            
            # Sample values for context
            sample_values = df[col].dropna().head(5).tolist()
            
            column_info.append({
                'name': col,
                'dtype': dtype,
                'non_null_count': non_null_count,
                'unique_count': unique_count,
                'sample_values': sample_values
            })
        
        # Create data summary
        data_summary = f"""
Dataset Shape: {rows} rows, {cols} columns

Column Information:
"""
        
        for col_info in column_info:
            data_summary += f"""
- {col_info['name']}:
  Type: {col_info['dtype']}
  Non-null values: {col_info['non_null_count']}/{rows}
  Unique values: {col_info['unique_count']}
  Sample values: {col_info['sample_values']}
"""
        
        # Add first few rows as sample
        data_summary += f"\nFirst 5 rows:\n{df.head().to_string()}"
        
        return data_summary
    
    def create_analysis_prompt(self, data_summary):
        """
        Create the complete prompt for LLM analysis
        
        Args:
            data_summary (str): Prepared dataset summary
        
        Returns:
            str: Complete prompt for OpenAI
        """
        prompt = f"""You are a professional data analyst. You will receive a cleaned dataset and your task is to analyze it and generate insights for the user.

Follow these steps:
1. Dataset Overview:
- Report the dataset shape as "X rows, Y columns".
- Provide short, one-line descriptions for each column. If a column has a vague name (e.g., "X"), infer its purpose from its values and annotate it like: X (possibly: Salary).

2. Visual Analysis:
- Choose 2 to 4 relevant visualizations that reveal patterns or trends in the data.
- Return valid Python code (matplotlib, seaborn, or plotly) to generate these visualizations.
- Do not explain the code or describe the libraries.
- Example plots: value counts for categorical columns, distribution of numeric features, comparisons across groups.

3. Insights and Relationships:
- Based on the data and visuals, write a plain-English summary of your findings.
- Include interesting patterns, outliers, or relationships between columns.
- Use language that a non-technical person can easily understand.

Return your output in three sections:
1. Column Descriptions (markdown-style list)
2. Plot Code Blocks (delimited clearly, one per plot)
3. Insights Summary (paragraph)

Here is the dataset information:
{data_summary}
Please analyze this dataset and provide your response in the specified format."""
        return prompt
    
    def call_openai_api(self, prompt):
        """
        Make API call to OpenAI using legacy API
        """
        try:
            print("Sending request to OpenAI API...")

            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional data analyst specializing in generating clear, actionable insights from datasets."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=2000,
                temperature=0.7
            )

            analysis_result = response.choices[0].message.content
            tokens_used = response.usage.total_tokens

            print("OpenAI API call successful")

            return {
                'success': True,
                'analysis': analysis_result,
                'tokens_used': tokens_used,
                'model': self.model
            }

        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def parse_llm_response(self, llm_response):
        """
        Parse LLM response into structured format

        Args:
            llm_response (str): Raw LLM response

        Returns:
            dict: Structured analysis components
        """
        try:
            # Split response into sections
            sections = llm_response.split('---')

            parsed_response = {
                'column_descriptions': '',
                'plot_codes': [],
                'insights_summary': llm_response, 
                'raw_response': llm_response
            }

            for section in sections:
                section = section.strip()

                if 'Column Descriptions:' in section:
                    parsed_response['column_descriptions'] = section.replace('Column Descriptions:', '').strip()

                elif 'Plot Code:' in section:
                    # Extract code blocks
                    import re
                    code_blocks = re.findall(r'```python(.*?)```', section, re.DOTALL)
                    parsed_response['plot_codes'] = [code.strip() for code in code_blocks]

                elif section and not any(keyword in section for keyword in ['Column Descriptions:', 'Plot Code:']):
                    # This is likely the insights summary
                    if len(section) > 50:  # Avoid capturing small fragments
                        parsed_response['insights_summary'] = section.strip()

            return parsed_response

        except Exception as e:
            print(f"Error parsing LLM response: {e}")
            return {
                'column_descriptions': '',
                'plot_codes': [],
                'insights_summary': llm_response,  # Fallback to raw response
                'raw_response': llm_response,
                'parse_error': str(e)
            }

    def analyze_processed_data(self, processed_file_path, file_id=None):
        """Complete LLM analysis workflow"""
        print(f"Starting LLM analysis for: {processed_file_path}")

        try:
            # Load processed dataset
            print("Loading processed dataset...")
            df = pd.read_csv(processed_file_path)

            if df.empty:
                return {
                    'success': False,
                    'error': 'Dataset is empty'
                }

            print(f"Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")

            # Prepare data summary
            data_summary = self.prepare_data_summary(df)
            print(f"Data summary prepared, length: {len(data_summary)}")

            # Create analysis prompt
            prompt = self.create_analysis_prompt(data_summary)
            print(f"Prompt created, type: {type(prompt)}, length: {len(prompt)}")
            
            # Debug: Print first 200 characters of prompt
            print(f"Prompt preview: {prompt[:200]}...")

            # Call OpenAI API
            print("About to call OpenAI API...")
            api_response = self.call_openai_api(prompt)
            print(f"API response received: {api_response.get('success', 'Unknown')}")

            if not api_response['success']:
                print(f"API call failed: {api_response.get('error', 'Unknown error')}")
                return api_response

            # Parse LLM response
            parsed_analysis = self.parse_llm_response(api_response['analysis'])

            # Combine results
            final_result = {
                'success': True,
                'file_id': file_id,
                'dataset_shape': df.shape,
                'analysis_datetime': datetime.now().isoformat(),
                'column_descriptions': parsed_analysis['column_descriptions'],
                'plot_codes': parsed_analysis['plot_codes'],
                'insights_summary': parsed_analysis['insights_summary'],
                'raw_llm_response': parsed_analysis['raw_response'],
                'tokens_used': api_response['tokens_used'],
                'model_used': api_response['model']
            }

            print("LLM analysis completed successfully!")
            return final_result

        except Exception as e:
            print(f"Error in LLM analysis workflow: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e),
                'file_id': file_id
            }