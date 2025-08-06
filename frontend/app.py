import streamlit as st
import pandas as pd
import sys
import os
import tempfile
from datetime import datetime

# Add backend to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.src.file_handler import FileHandler

# Page config
st.set_page_config(
    page_title="Analytics Autopilot",
    page_icon="📊",
    layout="wide"
)

def initialize_components():
    """Initialize file handler"""
    if 'file_handler' not in st.session_state:
        st.session_state.file_handler = FileHandler()

def generate_pdf_report(analysis_results):
    """
    Generate PDF report from analysis results
    
    Args:
        analysis_results (dict): Complete analysis results
    
    Returns:
        dict: PDF generation result with file path
    """
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        
        # Create PDF filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = f"analytics_report_{timestamp}.pdf"
        
        # Create PDF document
        doc = SimpleDocTemplate(pdf_filename, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        story.append(Paragraph("Analytics Autopilot - Data Analysis Report", title_style))
        story.append(Spacer(1, 20))
        
        # Report Information
        upload_info = analysis_results['upload_info']
        processing_info = analysis_results['processing_info']
        llm_analysis = analysis_results['llm_analysis']
        
        # File Information Section
        story.append(Paragraph("File Information", styles['Heading2']))
        story.append(Paragraph(f"<b>Original Filename:</b> {upload_info['stored_filename']}", styles['Normal']))
        story.append(Paragraph(f"<b>Original Shape:</b> ({upload_info['original_rows']}, {upload_info['original_columns']}) rows, columns", styles['Normal']))
        story.append(Paragraph(f"<b>Processed Shape:</b> ({processing_info['processed_rows']}, {processing_info['processed_columns']}) rows, columns", styles['Normal']))
        story.append(Paragraph(f"<b>Analysis Date:</b> {analysis_results['analysis_datetime']}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Processing Statistics
        story.append(Paragraph("Processing Statistics", styles['Heading2']))
        story.append(Paragraph(f"<b>Rows Removed:</b> {processing_info['rows_removed']}", styles['Normal']))
        story.append(Paragraph(f"<b>Columns Removed:</b> {processing_info['columns_removed']}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Column Descriptions
        if llm_analysis['column_descriptions']:
            story.append(Paragraph("Column Descriptions", styles['Heading2']))
            # Clean up the column descriptions for PDF
            col_desc = llm_analysis['column_descriptions'].replace('\n', '<br/>')
            story.append(Paragraph(col_desc, styles['Normal']))
            story.append(Spacer(1, 20))
        
        # Visualization Code
        if llm_analysis['plot_codes']:
            story.append(Paragraph("Recommended Visualizations", styles['Heading2']))
            for i, code in enumerate(llm_analysis['plot_codes'], 1):
                story.append(Paragraph(f"Visualization {i}:", styles['Heading3']))
                code_style = ParagraphStyle(
                    'CodeStyle',
                    parent=styles['Code'],
                    fontSize=8,
                    leftIndent=20,
                    fontName='Courier'
                )
                story.append(Preformatted(code, code_style))
                story.append(Spacer(1, 10))
        
        # Key Insights
        if llm_analysis['insights_summary']:
            story.append(Paragraph("Key Insights", styles['Heading2']))
            story.append(Paragraph(llm_analysis['insights_summary'], styles['Normal']))
            story.append(Spacer(1, 20))
        
        # Technical Details
        story.append(Paragraph("Technical Details", styles['Heading2']))
        story.append(Paragraph(f"<b>AI Model Used:</b> {llm_analysis.get('model_used', 'N/A')}", styles['Normal']))
        story.append(Paragraph(f"<b>Tokens Used:</b> {llm_analysis.get('tokens_used', 'N/A')}", styles['Normal']))
        
        # Build PDF
        doc.build(story)
        
        print(f"PDF report generated: {pdf_filename}")
        
        return {
            'success': True,
            'pdf_path': pdf_filename,
            'filename': pdf_filename
        }
        
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def display_processing_results(result):
    """Display processing results including LLM analysis"""
    if result['success']:
        st.success("Processing completed successfully!")
        
        upload_info = result['upload_info']
        processing_info = result['processing_info']
        
        # File Information
        st.subheader("File Information")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Original File:**")
            st.write(f"Filename: {upload_info['stored_filename']}")
            st.write(f"Shape: ({upload_info['original_rows']}, {upload_info['original_columns']})")
        
        with col2:
            st.write("**Processed File:**")
            st.write(f"Filename: {processing_info['processed_filename']}")
            st.write(f"Shape: ({processing_info['processed_rows']}, {processing_info['processed_columns']})")
        
        # Processing Statistics
        st.subheader("Processing Statistics")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Rows Removed", processing_info['rows_removed'])
        with col2:
            st.metric("Columns Removed", processing_info['columns_removed'])
        
        # LLM Analysis Results
        if 'llm_analysis' in processing_info and processing_info['llm_analysis']['success']:
            llm_data = processing_info['llm_analysis']
            
            st.subheader("AI Analysis Results")
            
            # Column Descriptions
            if llm_data['column_descriptions']:
                st.subheader("Column Descriptions")
                st.text(llm_data['column_descriptions'])
            
            # Visualization Code
            if llm_data['plot_codes']:
                st.subheader("Recommended Visualizations")
                for i, code in enumerate(llm_data['plot_codes'], 1):
                    with st.expander(f"Visualization {i} Code"):
                        st.code(code, language='python')
            
            # Insights Summary
            if llm_data['insights_summary']:
                st.subheader("Key Insights")
                st.write(llm_data['insights_summary'])
            
            # Store results in session state for PDF generation
            st.session_state.analysis_results = {
                'upload_info': upload_info,
                'processing_info': processing_info,
                'llm_analysis': llm_data,
                'analysis_datetime': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # PDF Download Button
            st.subheader("Download Report")
            if st.button("Download PDF Report", type="primary"):
                with st.spinner("Generating PDF report..."):
                    pdf_result = generate_pdf_report(st.session_state.analysis_results)
                    
                if pdf_result['success']:
                    with open(pdf_result['pdf_path'], "rb") as pdf_file:
                        st.download_button(
                            label="Click to Download Analysis Report",
                            data=pdf_file.read(),
                            file_name=f"analysis_report_{upload_info['stored_filename'].replace('.csv', '')}.pdf",
                            mime="application/pdf",
                            key="download_pdf"
                        )
                    
                    # Clean up PDF file after download
                    try:
                        os.remove(pdf_result['pdf_path'])
                    except:
                        pass
                        
                    st.success("PDF report ready for download!")
                else:
                    st.error(f"PDF generation failed: {pdf_result['error']}")
        
        else:
            st.warning("LLM analysis was not available for this file.")
            if 'llm_analysis' in processing_info:
                st.error(f"LLM Error: {processing_info['llm_analysis'].get('error', 'Unknown error')}")
    
    else:
        st.error(f"Processing failed: {result['error']}")

def main():
    st.title("Analytics Autopilot")
    st.markdown("Intelligent Data Processing Platform")
    
    # Initialize components
    initialize_components()
    
    # File upload section
    st.header("Upload Dataset")
    
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="Upload your CSV file for automated processing and AI analysis"
    )
    
    if uploaded_file is not None:
        # Display file info
        st.subheader("File Information")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write(f"**Filename:** {uploaded_file.name}")
        with col2:
            st.write(f"**Size:** {uploaded_file.size / 1024:.1f} KB")
        with col3:
            st.write(f"**Type:** {uploaded_file.type}")
        
        # Show data preview
        st.subheader("Data Preview")
        try:
            df_preview = pd.read_csv(uploaded_file)
            st.dataframe(df_preview.head(10), use_container_width=True)
            
            # Reset file pointer for processing
            uploaded_file.seek(0)
            
            # Process button
            if st.button("Process Data", type="primary", use_container_width=True):
                # Create temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
                    tmp_file.write(uploaded_file.getbuffer())
                    temp_file_path = tmp_file.name
                
                # Show processing status
                with st.spinner("Processing dataset and generating AI insights..."):
                    # Call the complete workflow
                    result = st.session_state.file_handler.complete_workflow(
                        temp_file_path, 
                        uploaded_file.name
                    )
                
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
                
                # Display results
                display_processing_results(result)
                
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
            st.info("Please make sure you uploaded a valid CSV file.")
    
    else:
        st.info("Please upload a CSV file to get started")

if __name__ == "__main__":
    main()