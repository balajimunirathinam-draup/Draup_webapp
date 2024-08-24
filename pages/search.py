import pandas as pd
from duckduckgo_search import DDGS
import streamlit as st
import time

# Function to extract data from DuckDuckGo search results
def extract_data(result):
    return {
        'title': result.get('title', ''),
        'href': result.get('href', ''),
        'body': result.get('body', ''),
    }

# Function to perform search with rate limit handling
def perform_search(ddgs, query):
    try:
        results = [r for r in ddgs.text(query, max_results=1)]
        return results
    except Exception as e:
        st.error(f"Error during search for query '{query}': {str(e)}")
        return []

# Streamlit app
st.title("Secondary Search Tool")

# File uploader
uploaded_file = st.file_uploader("Upload a CSV file with search queries", type="csv")

if uploaded_file is not None:
    # Read the CSV file to get the column names
    df = pd.read_csv(uploaded_file)
    
    # Display the columns for user to select which one(s) to use for queries
    selected_columns = st.multiselect("Select the column(s) for search queries", df.columns.tolist())
    
    if selected_columns:
        # Show the selected columns in a DataFrame
        selected_df = df[selected_columns]
        st.write("Selected DataFrame:")
        st.dataframe(selected_df)
        
        # Add a button to start the processing
        if st.button("Start Process"):
            with st.spinner("Processing..."):
                # Initialize an empty DataFrame to store all results
                all_results_df = pd.DataFrame()
                
                # Initialize the progress bar
                progress_bar = st.progress(0)
                total_queries = len(selected_df)
                
                with DDGS() as ddgs:
                    for idx, row in selected_df.iterrows():
                        query = " ".join([str(value) for value in row.values if pd.notna(value)])
                        
                        # Retry mechanism with delay
                        success = False
                        retry_count = 0
                        while not success and retry_count < 3:
                            results = perform_search(ddgs, query)
                            
                            if results:
                                first_result = results[0]
                                extracted_data = extract_data(first_result)

                                # Create a DataFrame for the current query's results
                                query_results_df = pd.DataFrame([extracted_data])

                                # Concatenate the current query's results with all results
                                all_results_df = pd.concat([all_results_df, query_results_df], ignore_index=True)
                                success = True
                            else:
                                retry_count += 1
                                if retry_count < 3:
                                    st.warning(f"Ratelimit encountered. Retrying query '{query}' in 5 seconds...")
                                    time.sleep(5)
                                else:
                                    st.error(f"Failed to retrieve results for query '{query}' after 3 attempts.")
                        
                        # Update the progress bar
                        progress_percentage = (idx + 1) / total_queries
                        progress_bar.progress(progress_percentage)
                        
                        # Delay between each search to avoid hitting rate limits
                        time.sleep(2)
                
                if not all_results_df.empty:
                    # Allow users to select which columns to include in the output file
                    output_columns = st.multiselect(
                        "Select the columns to include in the output file",
                        options=all_results_df.columns.tolist(),
                        default=all_results_df.columns.tolist()
                    )
                    
                    if output_columns:
                        # Filter the DataFrame to include only the selected columns
                        final_results_df = all_results_df[output_columns]
                        
                        # Save the combined DataFrame to a CSV file
                        output_filename = 'output.csv'
                        final_results_df.to_csv(output_filename, index=False, encoding='utf-8')

                        # Provide a download link for the results
                        st.success(f"Data extracted and saved to {output_filename}")
                        st.download_button(
                            label="Download CSV",
                            data=final_results_df.to_csv(index=False, encoding='utf-8'),
                            file_name=output_filename,
                            mime='text/csv'
                        )
                    else:
                        st.warning("Please select at least one column to include in the output file.")
                else:
                    st.warning("No results were retrieved from the search queries.")
    else:
        st.warning("Please select at least one column for search queries.")
