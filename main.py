import streamlit as st
import os
import pandas as pd
import matplotlib.pyplot as plt
from analysis import analyse_connections, count_messages, add_connection_direction, goal_to_analysis
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_google_vertexai import VertexAI
import json
import tempfile
import time
import plotly.graph_objects as go


if 'clicked' not in st.session_state:
    st.session_state.clicked = False

def click_button():
    st.session_state.clicked = True

    
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
    st.title('6degrees Network Analysis')

    st.subheader('Upload your LinkedIn data to get started!')
    # Allows user to upload multiple CSV files for analysis
    uploaded_files = st.file_uploader("Upload CSV files downloaded from LinkedIn (your data is not saved)", accept_multiple_files=True, type='csv')
    
    if uploaded_files:
        if 'data_frames' not in st.session_state:
            with st.spinner('Loading data...'):
                st.session_state.data_frames = load_data(uploaded_files)
                time.sleep(1)  # Simulate time delay
            st.success('Data successfully loaded!')

    if 'data_frames' in st.session_state:
            st.header("Define Your Objective")
            goal = st.radio("What is your goal?", 
                                    ["Finding new clients", 
                                     "Recruit new talent", 
                                     "Find investors", 
                                     "Find a new job", 
                                     "Grow your community", 
                                     "Strengthen Partnerships", 
                                    "Build Distribution channels"], 
                                    captions = [
                                                "Expand Your Business Horizons",
                                                "Boost Your Team's Capabilities",
                                                "Connect, Engage, Succeed",
                                                "Refine and Perfect Offerings",
                                                "Fuel Your Future Ventures",
                                                "Ensure Investment Security",
                                                "Embark on New Career Paths",
                                                "Build a Thriving Network",
                                                "Forge Stronger Alliances",
                                                "Widen Your Market Reach"
                                            ],
                                    index=0,
                                    help="Select your goal to tailor the analysis.")
            
            details = st.text_input("Details about your goal - specify industry or role", "E.g. <Fintech> or <Product leader>")
            
            st.button('Analyse', on_click=click_button)

            if st.session_state.clicked:

                st.info(f"Goal selected: {goal}, details: {details}")
                
                st.header("Network Insights")
                tab1, tab2, tab3 = st.tabs(["Overview", "Insights", "Ask a question"])
                
                with tab1:
                    st.subheader("Connections Overview")
                    with st.spinner('Analyzing connections...'):
                        graphs = analyse_connections(st.session_state.data_frames['connections'])
                    for title, graph in graphs.items():
                        st.plotly_chart(graph, use_container_width=True)

                with tab2:
                    st.subheader("Insights Based On Your Goal")
                    agent = create_pandas_dataframe_agent(llm, st.session_state.data_frames['connections'], verbose=True)
                    tasks = goal_to_analysis(goal)
                    for task in tasks:
                        st.subheader(task)
                        user_query_graph = f'This is my goal: {goal} for industry/role: {details}. Write code for plotly graph to analyse {task}'
                        user_query = f'This is my goal: {goal} for industry/role: {details}. Your goal is to find {task}'
                        
                        with st.spinner("Running agent..."):
                            time.sleep(10)

                        analysis =  agent.invoke({"input": user_query})
                        st.write(analysis)
                        
                        with st.spinner("Running agent..."):
                            time.sleep(10)

                        plotly_code = agent.invoke({"input": user_query_graph})
                        local_vars = {}

                        # Execute the string code
                        exec(plotly_code, {'go': go}, local_vars)  # Provide 'go' in the global variables for safety

                        # Extract the figure from the local_vars
                        fig = local_vars['fig']

                        # Use the figure in Streamlit
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)
                    

                with tab3:
                    st.subheader("Chat With Your Network Data")
                    objective = st.text_input("What do you want to know?", "E.g. Which connections could introduce me to fintech clients?")
                    if st.button("Submit query"):
                        with st.spinner('Analyzing your query...'):
                            agent = create_pandas_dataframe_agent(llm, st.session_state.data_frames['connections'], verbose=True)
                            output = agent.invoke({"input": objective})
                        st.success("Analysis complete!")
                        st.write(output)            
                

if __name__ == "__main__":
    main()
