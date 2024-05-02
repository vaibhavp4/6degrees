import streamlit as st
import io
import pandas as pd
import matplotlib.pyplot as plt
from analysis import analyse_connections, analyse_messages, analyse_invitations, count_messages, add_connection_direction
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_community.llms import VertexAI
import base64
import vertexai
from vertexai.generative_models import GenerativeModel, Part, FinishReason
import vertexai.preview.generative_models as generative_models

llm = VertexAI(model_name="gemini-1.5-pro-preview-0409", temperature=0.2)

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

                

                def generate():
                    vertexai.init(project="snappy-topic-422116-h1", location="europe-west2")
                    model = GenerativeModel("gemini-1.5-pro-preview-0409")
                    responses = model.generate_content(
                        [text1],
                        generation_config=generation_config,
                        safety_settings=safety_settings,
                        stream=True,
                    )

                    for response in responses:
                        st.write(response.text, end="")

                text1 = """We have access to LinkedIn connections of a user. Our goal is to help the user get meaningful insights based on their request.

                Here is their request:current role: Foundercurrent objective: To get new clientsIdeal customer profile: Ed-tech companies

                Suggest 3 questions or insights areas that we can explore from their LinkedIn data to help them achieve their objective

                Here are the rules:- The questions should be precise and non-overlapping- The questions should be answerable by analysing only the CSV containing the following columns: First Name, Last Name, URL, Email Address, Company, Position, Connected On, Messages count, Team, Industry"""

                generation_config = {
                    "max_output_tokens": 8192,
                    "temperature": 0.7,
                    "top_p": 0.95,
                }

                safety_settings = {
                    generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                }

                generate()


                
                '''
                agent = create_pandas_dataframe_agent(llm, connections, agent_type="openai-tools", verbose=True)
                
                output = agent.invoke(
                    {
                        "input": objective
                    }
                )
                st.write(output) 
                '''          
                

if __name__ == "__main__":
    main()
