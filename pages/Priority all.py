import pandas as pd
import json
import streamlit as st
import re
import io
from openpyxl import Workbook

def load_file(uploaded_file):
    """Load the uploaded file based on its extension."""
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xls', '.xlsx')):
            # Load all sheets and let the user select one if multiple sheets are present
            df_dict = pd.read_excel(uploaded_file, sheet_name=None)
            sheet_names = list(df_dict.keys())
            selected_sheet = st.selectbox('Select sheet', sheet_names)
            df = df_dict[selected_sheet]
        else:
            st.error("Unsupported file type.")
            return None
        return df
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None

def load_json_safe(x):
    """Safely load JSON data from a string."""
    try:
        return json.loads(x)
    except (json.JSONDecodeError, TypeError):
        return {}

def clean_description(description):
    """Clean unwanted characters from the description."""
    if isinstance(description, list):
        description = ' '.join(map(str, description))
    return re.sub(r'[.,]', '', description).strip()

def extract_priority_data(df, priority_column, selected_keys, options):
    """Extract priority data based on selected keys and format the results."""
    df[priority_column] = df[priority_column].apply(load_json_safe)

    # Check if 'Company' and 'Year' columns exist before sorting
    if 'Company' in df.columns and 'Year' in df.columns:
        df_sorted = df.sort_values(by=['Company', 'Year'], ascending=[True, False])
    else:
        st.warning("The required columns 'Company' and 'Year' are not present in the dataset.")
        df_sorted = df  # Proceed without sorting if columns are missing

    result = []
    seen_companies = set()

    # Progress bar
    with st.spinner('Processing data...'):
        progress_bar = st.progress(0)
        total_steps = len(df_sorted)

        for i, row in df_sorted.iterrows():
            company = row['Company']
            if company not in seen_companies:
                seen_companies.add(company)
                json_priorities = row[priority_column]
                for key in selected_keys:
                    if key in json_priorities:
                        for sub_item in json_priorities[key]:
                            formatted_data = {
                                'Company Name': company,
                                'Priority Type': options[key],
                                'Priority Initiative Name': sub_item.get('priority', ''),
                                'Priority Initiative Description': clean_description(sub_item.get('description', ''))
                            }
                            result.append(formatted_data)

            # Update progress bar
            progress_bar.progress((i + 1) / total_steps)
    
    return pd.DataFrame(result, columns=['Company Name', 'Priority Type', 'Priority Initiative Name', 'Priority Initiative Description'])

def convert_df_to_excel(df):
    """Convert DataFrame to an Excel file."""
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Data')
    buffer.seek(0)
    return buffer

def convert_df_to_json(df):
    """Convert DataFrame to a JSON file."""
    buffer = io.BytesIO()
    json_data = df.to_json(orient='records')
    buffer.write(json_data.encode('utf-8'))
    buffer.seek(0)
    return buffer

def convert_df_to_csv(df):
    """Convert DataFrame to a CSV file."""
    return df.to_csv(index=False).encode('utf-8')

def main():
    """Main function to run the Streamlit app."""
    st.set_page_config(
        page_title="Priority Extract Tool",
        page_icon="favicon-96.png",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'About': "This app extracts and displays Priority Extract Tool from uploaded datasets."
        }
    )

    st.title("Priority Extract Tool")

    uploaded_file = st.file_uploader("Choose a file", type=['csv', 'xls', 'xlsx'])

    if uploaded_file is not None:
        df = load_file(uploaded_file)
        if df is not None:
            st.success("File successfully uploaded.")
            st.write("Preview of the uploaded DataFrame:")
            st.write(df.head(25))

            # Allow user to select the column containing the priorities
            priority_column = st.selectbox("Select the column containing formatted priorities:", df.columns)

            options = {
                'business': 'Business Priorities',
                'R&D': 'R&D Priorities',
                'sustainability': 'Sustainability Priorities',
                'talent': 'Talent Priorities',
                'technology': 'Technology Priorities'
            }
            selected_keys = st.multiselect('Select the keys to extract data:', options.keys())

            if selected_keys:
                selected_df = extract_priority_data(df, priority_column, selected_keys, options)
                
                if not selected_df.empty:
                    st.write("Preview of the extracted data:")
                    st.write(selected_df)

                    # CSV download
                    csv_data = convert_df_to_csv(selected_df)
                    st.download_button(
                        label="Download data as CSV",
                        data=csv_data,
                        file_name='extracted_priority_data.csv',
                        mime='text/csv',
                        use_container_width=True
                    )

                    # Excel download
                    excel_buffer = convert_df_to_excel(selected_df)
                    st.download_button(
                        label="Download data as Excel",
                        data=excel_buffer,
                        file_name='extracted_priority_data.xlsx',
                        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                        use_container_width=True
                    )

                    # JSON download
                    json_buffer = convert_df_to_json(selected_df)
                    st.download_button(
                        label="Download data as JSON",
                        data=json_buffer,
                        file_name='extracted_priority_data.json',
                        mime='application/json',
                        use_container_width=True
                    )

        else:
            st.error("Failed to load the file. Please try again.")

    # Expander for tool information
    with st.expander("Learn More About the Priority Extract Tool"):
        st.write(
            """
            **Priority Extract Tool** is designed to help users analyze and extract prioritized data from uploaded datasets. It supports various file formats (CSV, Excel), processes the data based on user-selected criteria, and formats the extracted information for easy download. Key features include:

            - **File Upload**: Users can upload CSV or Excel files.
            - **Data Preview**: View a snapshot of the uploaded data.
            - **Priority Extraction**: Select and extract priorities based on specified keys (e.g., Business, R&D, Sustainability).
            - **Data Cleaning**: Remove unwanted characters from descriptions.
            - **Download Options**: Export the processed data in CSV, Excel, or JSON formats.
            - **User Interface**: Interactive elements for file upload, data selection, and download.

            This tool streamlines data handling, enabling users to quickly obtain and utilize relevant priority information from their datasets.
            """
        )

if __name__ == "__main__":
    main()

# Footer bar
footer = """
<style>
.footer {position: fixed; left: 0; bottom: 0; width: 100%; background-color: #65cff6; color: black; text-align: center; padding: 10px;}
</style>
<div class="footer"><p>Copyright © 2024 Draup. All Rights Reserved.</p></div>
"""
st.markdown(footer, unsafe_allow_html=True)
