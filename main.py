import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from analysis import analyse_connections, analyse_messages, analyse_invitations

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
            df = pd.read_csv(file, delimiter=',', on_bad_lines='skip', header=2)
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

    # Allows user to upload multiple CSV files for analysis
    uploaded_files = st.file_uploader("Choose CSV files", accept_multiple_files=True, type='csv')
    if uploaded_files:
        data_frames = load_data(uploaded_files)
        
        st.header("Questions for Analysis")
        # Collect input from users to guide data analysis
        question1 = st.text_input("What is your current goal?")
        question2 = st.text_input("Please describe your ICP/target market?")
        question3 = st.text_input("Which industries are you interested in?")
        
        if st.button("Analyze"):
            # Placeholder for future function to tailor analysis based on user input
            # TODO: 
            # Implement a function to convert the onboarding responses context and analysis goals for tabs
            
            '''
            for key, df in data_frames.items():
                st.write(key)
                st.table(df.head())
            '''
            
            # Setting up tabs for different insights and visualizations
            tab1, tab2, tab3 = st.tabs(["Connections", "Messages", "Invitations"])
            
            with tab1:
                graphs = analyse_connections(data_frames['connections'])
                for title, graph in graphs.items():
                    st.plotly_chart(graph, use_container_width=True)
            
            with tab2:
                st.write("Insights for Graph 2 based on analysis")
                
            
            with tab3:
                st.write("Insights for Graph 3 based on analysis")
                

if __name__ == "__main__":
    main()
