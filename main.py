import streamlit as st
import os
import pandas as pd
import matplotlib.pyplot as plt
from analysis import analyse_connections, analyse_messages, analyse_invitations, count_messages, add_connection_direction
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_google_vertexai import VertexAI
import json
import tempfile

# Initialize Google Cloud credentials
def create_temp_creds_file(credentials_json):
    # Create a temporary file to store the credentials
    _, path = tempfile.mkstemp(suffix='.json')  # Creates a temp file and returns its path
    with open(path, 'w') as temp_file:
        json.dump(credentials_json, temp_file)  # Write the JSON data to the temp file
    
    return path

# Load credentials from Streamlit secrets
creds_json = json.loads(st.secrets["google_credentials"])

# Create a temporary credentials file and get the path
temp_creds_path = create_temp_creds_file(creds_json)

# Set the GOOGLE_APPLICATION_CREDENTIALS environment variable
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = temp_creds_path


llm = VertexAI(model_name="gemini-1.0-pro-vision-001", temperature=0.2)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

def find_data_start(file, key_column='First Name'):
    """
    Dynamically find the starting row of actual data in a CSV file.

    Parameters:
    file (file-like object): The CSV file to scan.
    key_column (str): The expected header name of the first column of the data.

    Returns:
    int: The index of the row to be used as the header (0-based).
    """
    # Attempt to read the file incrementally until the key column is found
    for skip_rows in range(10):  # Adjust range based on max expected preamble length
        file.seek(0)  # Reset file pointer to the start of the file for each attempt
        try:
            df = pd.read_csv(file, skiprows=skip_rows, nrows=1)
            if key_column in df.columns:
                return skip_rows
        except pd.errors.EmptyDataError:
            continue
    raise ValueError(f"Unable to find data start; '{key_column}' not found in the first 10 rows.")

@st.cache_data
def load_data(uploaded_files):
    data_frames = {}
    for file in uploaded_files:
        key = file.name.split('/')[-1].split('.')[0].lower()
        try:
            if key =="connections":
                header_row = find_data_start(file, 'First Name')
                file.seek(0)  # Reset file position after finding header
            else:
                header_row = 0
            df = pd.read_csv(file, skiprows=header_row)
        except Exception as e:
            st.error(f"Failed to read {key}: {e}")
            continue
        data_frames[key] = df
    return data_frames


def main():
    """
    Main function to run the Streamlit app for network analysis.
    
    This function sets up the Streamlit interface for uploading files, entering analysis questions, 
    and viewing different tabs with data visualizations based on the uploaded CSV data.
    """
    st.title('6degrees network analysis')

    st.subheader('Upload your linkedin data to get started!')
    # Allows user to upload multiple CSV files for analysis
    uploaded_files = st.file_uploader("Choose CSV files", accept_multiple_files=True, type='csv')
    if uploaded_files:
        data_frames = load_data(uploaded_files)
        
        if "connections" in data_frames:

            st.header("Let's unlock your professional network!")
            
            tab1, tab2, tab3 = st.tabs(["Connections", "Messages", "Invitations"])
            
            with tab1:
                graphs = analyse_connections(data_frames['connections'])
                for title, graph in graphs.items():
                    st.plotly_chart(graph, use_container_width=True)
            
            with tab2:
                st.write("Insights for Graph 2 based on analysis")
                
            
            with tab3:
                st.write("Insights for Graph 3 based on analysis")

            if "invitations" in data_frames:
                connections = add_connection_direction(data_frames['connections'], data_frames['invitations'])
            
            if "messages" in data_frames:
                messages_count = count_messages(data_frames['messages'])

            connections =  pd.merge(connections, messages_count, left_on='URL', right_on='URL', how='left')
            connections['Count'] = connections['Count'].fillna(0)

            objective = st.text_input("What do you want to know?", "E.g. Which connections could introduce me to banking industry?")
            
            if st.button("Analyze"):

                agent = create_pandas_dataframe_agent(llm, connections, verbose=True)
                
                output = agent.invoke(
                    {
                        "input": objective
                    }
                )
                st.write(output)      
                

if __name__ == "__main__":
    main()
