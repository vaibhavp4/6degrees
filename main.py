import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from analysis import analyse_connections, analyse_messages, analyse_invitations, count_messages, add_connection_direction
from langchain_experimental.agents import create_pandas_dataframe_agent
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load the .env file
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if api_key is None:
    raise ValueError("OPENAI_API_KEY is not set in the .env file.")
else:
    os.environ["OPENAI_API_KEY"] = api_key  # Set the API key in os.environ if not already set

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)


@st.cache_data
def load_data(uploaded_files):
    """
    Load and concatenate multiple CSV files into a dictionary of dataframes.

    Parameters:
    uploaded_files (iterable): An iterable of uploaded file objects (from Streamlit).

    Returns:
    dict: A dictionary where each key is the file name (without extension) and value is the dataframe.
    
    Each file is read into a dataframe, skipping bad lines. Errors during file reading are caught and displayed in the Streamlit interface.
    """
    data_frames = {}
    for file in uploaded_files:
        key = file.name.split('/')[-1].split('.')[0].lower()
        try:
            header_row = 2 if key == "connections" else 0
            df = pd.read_csv(file, delimiter=',', on_bad_lines='skip', header=header_row)
        except Exception as e:
            st.error(f"Failed to read {key}: {e}")  # Display error in Streamlit
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

            agent = create_pandas_dataframe_agent(llm, connections, agent_type="openai-tools", verbose=True)
            
            output = agent.invoke(
                {
                    "input": objective
                }
            )
            st.write(output)           
                

if __name__ == "__main__":
    main()
