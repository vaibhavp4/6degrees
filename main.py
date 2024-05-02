import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from analysis import analyse_connections, analyse_messages, analyse_invitations, count_messages, add_connection_direction

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

    # Allows user to upload multiple CSV files for analysis
    uploaded_files = st.file_uploader("Choose CSV files", accept_multiple_files=True, type='csv')
    if uploaded_files:
        data_frames = load_data(uploaded_files)
        
        st.header("Let's unlock your professional network!")


    # Initialize the session state variables if not already present
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "current_step" not in st.session_state:
        st.session_state.current_step = 1  # Start at the first question

    # Function to handle adding chat messages to the history and displaying them
    def add_and_display_message(role, content):
        st.session_state.messages.append({"role": role, "content": content})
        for message in st.session_state.messages:
            with st.chat_message(message['role']):
                st.markdown(message['content'])

    # Display previous messages
    for message in st.session_state.messages:
        with st.chat_message(message['role']):
            st.markdown(message['content'])

    # Manage the conversation steps
    if st.session_state.current_step == 1:
        objective = st.chat_input("What's your objective?")
        if objective:
            add_and_display_message("user", objective)
            add_and_display_message("assistant", "Thanks! Let's learn more about it.")
            st.session_state.current_step += 1

    elif st.session_state.current_step == 2:
        icp = st.chat_input("Describe your ICP/target market.")
        if icp:
            add_and_display_message("user", icp)
            add_and_display_message("assistant", "Great! Let's refine it further.")
            st.session_state.current_step += 1

    elif st.session_state.current_step == 3:
        industry = st.chat_input("Which industries are you interested in?")
        if industry:
            add_and_display_message("user", industry)
            add_and_display_message("assistant", "Perfect! Click analyse to unlock the best opportunities.")
            st.session_state.current_step += 1  # Adjust this if there are more steps

        
        if st.button("Analyze"):
            # Placeholder for future function to tailor analysis based on user input
            # TODO: 
            # Implement a function to convert the onboarding responses context and analysis goals for tabs
            

            if "invitations" in data_frames:
                connections = add_connection_direction(data_frames['connections'], data_frames['invitations'])
            
            if "messages" in data_frames:
                messages_count = count_messages(data_frames['messages'])
                st.table(messages_count.head(3))

            connections =  pd.merge(connections, messages_count, left_on='URL', right_on='URL', how='left')
            connections['Count'] = connections['Count'].fillna(0)

            st.table(connections.sort_values(by='Count', ascending=False).head(3))
            
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
