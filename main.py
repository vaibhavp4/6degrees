import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from analysis import analyse_connections, analyse_messages, analyse_invitations, count_messages, add_connection_direction
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain.llms import VertexAI

if "gemini_model" not in st.session_state:
    st.session_state["gemini_model"] = "gemini-ultra-pro"

llm = VertexAI(model_name="text-bison@001", temperature=0)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

@st.cache_data
def load_data(uploaded_files):
    """
    Load and concatenate multiple CSV files into a dictionary of dataframes.

    Parameters:
    uploaded_files (iterable): An iterable of uploaded file objects (from Streamlit).

    Returns:
    dict: A dictionary where each key is the file name (without extension) and value is the dataframe.
    """
    data_frames = {}
    for file in uploaded_files:
        key = file.name.split('/')[-1].split('.')[0].lower()
        try:
            # Attempt to identify the header row
            if key =="connections":
                header_row = find_header_row(file, expected_column_name='First Name')
            else:
                header_row = 0
            file.seek(0)  # Reset file read position after checking rows
            df = pd.read_csv(file, delimiter=',', on_bad_lines='skip', header=header_row)
        except Exception as e:
            st.error(f"Failed to read {key}: {e}")  # Display error in Streamlit
            continue
        data_frames[key] = df
    return data_frames

def find_header_row(file, expected_column_name='First Name'):
    """
    Attempts to determine the header row index by looking for a specific column name.
    
    Parameters:
    file (file-like object): The file to scan for the header.
    expected_column_name (str): The name of the first expected column header.

    Returns:
    int: The index of the row to be used as the header.
    """
    import csv
    reader = csv.reader(file)
    for index, row in enumerate(reader):
        if expected_column_name in row:
            return index
    raise ValueError(f"Header with column name '{expected_column_name}' not found.")


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

                agent = create_pandas_dataframe_agent(llm, connections, agent_type="openai-tools", verbose=True)
                
                output = agent.invoke(
                    {
                        "input": objective
                    }
                )
                st.write(output)           
                

if __name__ == "__main__":
    main()
