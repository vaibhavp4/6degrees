import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Function to load and concatenate multiple CSV files
def load_data(uploaded_files):
    data_frames = []
    for file in uploaded_files:
        df = pd.read_csv(file)
        data_frames.append(df)
    combined_data = pd.concat(data_frames, ignore_index=True)
    return combined_data

# Function to perform analysis (modify this based on the actual analysis needed)
def analyze_data(data):
    # Example analysis: Get summary statistics
    return data.describe()

# Streamlit app
def main():
    st.title('CSV File Analysis App')

    # File uploader allows user to upload multiple CSV files
    uploaded_files = st.file_uploader("Choose CSV files", accept_multiple_files=True, type='csv')
    if uploaded_files:
        data = load_data(uploaded_files)
        
        # Questions section
        st.header("Questions for Analysis")
        question1 = st.text_input("What is your first question?")
        question2 = st.text_input("What is your second question?")
        
        if st.button("Analyze"):
            # Data analysis based on questions
            analysis_result = analyze_data(data)
            
            # Creating tabs for different insights and graphs
            tab1, tab2, tab3 = st.tabs(["Graph 1", "Graph 2", "Graph 3"])
            
            with tab1:
                st.write("Insights for Graph 1 based on analysis")
                fig, ax = plt.subplots()
                ax.hist(data[data.columns[0]]) # Example graph
                st.pyplot(fig)
            
            with tab2:
                st.write("Insights for Graph 2 based on analysis")
                fig, ax = plt.subplots()
                ax.plot(data[data.columns[1]]) # Example graph
                st.pyplot(fig)
            
            with tab3:
                st.write("Insights for Graph 3 based on analysis")
                fig, ax = plt.subplots()
                ax.bar(data[data.columns[2]].unique(), data[data.columns[2]].value_counts()) # Example graph
                st.pyplot(fig)

if __name__ == "__main__":
    main()
