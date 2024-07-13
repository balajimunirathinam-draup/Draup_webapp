import pandas as pd
import json
import streamlit as st

def load_file(uploaded_file):
    """Load the uploaded file based on its extension."""
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith('.xls') or uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
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

def main():
    """Main function to run the Streamlit app."""
    st.title("Priority Deliverable")
    
    # Sidebar for uploading file
    uploaded_file = st.file_uploader("Choose a file", type=['csv', 'xls', 'xlsx'])
    
    if uploaded_file is not None:
        df = load_file(uploaded_file)
        if df is not None:
            st.success("File successfully uploaded.")
            st.write("Preview of the uploaded DataFrame:")
            st.write(df.head(25))

            # Options for selecting keys with their corresponding names
            options = {
                'business': 'Business Priorities',
                'R&D': 'R&D Priorities',
                'sustainability': 'Sustainability Priorities',
                'talent': 'Talent Priorities',
                'technology': 'Technology Priorities'
            }
            selected_keys = st.multiselect('Select the keys to extract data:', options.keys())

            # Apply the load_json_safe function to the 'Formatted Priorities' column of the DataFrame
            df['Formatted Priorities'] = df['Formatted Priorities'].apply(load_json_safe)

            # Sort the DataFrame by 'Company' and 'Year' columns in descending order to consider the most recent year first
            df_sorted = df.sort_values(by=['Company', 'Year'], ascending=[True, False])

            # Initialize an empty list to store the extracted data
            result = []

            # Track seen companies to avoid duplicates
            seen_companies = set()

            # Loop through each row in the sorted DataFrame
            for index, item in df_sorted.iterrows():
                company = item['Company']
                if company not in seen_companies:
                    seen_companies.add(company)
                    json_priorities = item['Formatted Priorities']
                    # Check if any of the selected keys are present in the item
                    for key in selected_keys:
                        if key in json_priorities:
                            # If the selected key is present, loop through each sub-item under the selected key
                            for sub_item in json_priorities[key]:
                                # Add the 'Company' and 'Selected Key' information from the corresponding row in the DataFrame to each sub-item
                                formatted_data = {
                                    'Company Name': company,
                                    'Priority Type': options[key],
                                    'Priority Initiative Name': sub_item.get('priority', ''),
                                    'Priority Initiative Description': sub_item.get('description', '')
                                }
                                # Append the modified sub-item to the result list
                                result.append(formatted_data)

            # Create a DataFrame from the extracted data
            selected_df = pd.DataFrame(result, columns=['Company Name', 'Priority Type', 'Priority Initiative Name', 'Priority Initiative Description'])

            # Display the extracted data in a DataFrame
            st.write(selected_df)

        else:
            st.error("Failed to load the file. Please try again.")

if __name__ == "__main__":
    main()
