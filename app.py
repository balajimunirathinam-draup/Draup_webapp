import pandas as pd
import json
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="BI_Prority_JSON-CSV",
    page_icon="favicon-96.png",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'About': "JSON is known as a light-weight data format type and is favored for its human readability and nesting features. It is often used in conjunction with APIs and data configuration. CSV: CSV is a data storage format that stands for Comma Separated Values with the extension . csv."
    }
)

# Title
st.title('BI_Prority_JSON-CSV')

# Define function to safely load JSON data
def load_json_safe(x):
    try:
        return json.loads(x)
    except (json.JSONDecodeError, TypeError):
        return {}

# Function to load data from a CSV file
def load_csv_data(file):
    if file is not None:
        df = pd.read_csv(file)
        return df
    return None

# Main function
def main():
    # Sidebar for uploading CSV file
    col1, col2 = st.columns([1, 3])
    with col1:
        st.sidebar.header("Upload CSV File")
        uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type=['csv'])

    # If a CSV file is uploaded, load it and display its content
    if uploaded_file is not None:
        df = load_csv_data(uploaded_file)
        if df is not None:
            with col2:
                st.success("File successfully uploaded.")
                st.write("Preview of the uploaded DataFrame:")
                st.write(df.head())

            # Prompt the user to input the key for selecting data
            selected_key = st.text_input('Enter the key to select data:')

            # Apply the load_json_safe function to the 'Formatted Priorities' column of the DataFrame
            json_data = df['Formatted Priorities'].apply(load_json_safe)

            # Initialize an empty list to store the extracted data
            result = []

            # Loop through each item in the json_data Series along with its index
            for index, item in enumerate(json_data):
                # Check if the selected key is present in the item
                if selected_key in item:
                    # If the selected key is present, loop through each sub-item under the selected key
                    for sub_item in item[selected_key]:
                        # Add the 'Company' information from the corresponding row in the DataFrame to each sub-item
                        sub_item['Company'] = df.iloc[index]['Company']
                        # Append the modified sub-item to the result list
                        result.append(sub_item)

            # Create a DataFrame from the extracted data
            selected_df = pd.DataFrame(result)

            # Display the extracted data in a DataFrame
            st.write(selected_df)

        else:
            with col2:
                st.error("Failed to load the CSV file. Please try again.")

if __name__ == "__main__":
    main()

# Footer bar
footer = """
<style>
.footer {position: fixed; left: 0; bottom: -17px; width: 100%; background-color: #65cff6; color: black; text-align: center; }
</style>
<div class="footer"><p>Copyright © 2024 Draup. All Rights Reserved.</p></div>
"""
st.markdown(footer, unsafe_allow_html=True)
