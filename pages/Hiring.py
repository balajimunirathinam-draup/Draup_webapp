import pandas as pd
import streamlit as st
import io

st.title('Hiring Deliverable')

# File uploader
uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx", "xls"])

if uploaded_file is not None:
    # Determine the file type and load the file into a DataFrame
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # Replace unwanted patterns
    df = df.replace('"]', '', regex=True)
    df = df.replace('\["', '', regex=True)
    df = df.replace('\[]', '-', regex=True)

    # Drop duplicates
    df.drop_duplicates(inplace=True)

    # Create a new DataFrame with the specified columns and rename them
    df_frame = df[['mvp_company_name', 'translated_job_title', 'msa', 'publication_date', 'url', 'core_skills', 
                    'soft_skills', 'job_role_list', 'digital_products', 'business_function', 'functional_workload', 
                    'education', 'synon_location']]

    df_frame = df_frame.rename(columns={
        'mvp_company_name': 'Company Name',
        'translated_job_title': 'Job Title',
        'msa': 'Location',
        'publication_date': 'Posted Date',
        'url': 'URL',
        'core_skills': 'Core Skills',
        'soft_skills': 'Soft Skills',
        'job_role_list': 'Job Role',
        'digital_products': 'Digital Products',
        'business_function': 'Business Function',
        'functional_workload': 'Functional Workload',
        'education': 'Education',
        'synon_location': 'Synon Location'
    })

    # Display data info
    st.write('## Data Info')
    buffer = io.StringIO()
    df_frame.info(buf=buffer)
    s = buffer.getvalue()
    st.text(s)

    # Display DataFrame
    st.write('## Job Data')
    st.dataframe(df_frame)

    # Allow the user to download the cleaned data
    st.write('## Download Cleaned Data')
    csv = df_frame.to_csv(index=False)
    st.download_button(
        label='Download CSV',
        data=csv,
        file_name='cleaned_data.csv',
        mime='text/csv'
    )
else:
    st.write("Please upload a CSV or Excel file.")
