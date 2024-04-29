import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Function to load and concatenate multiple CSV files
@st.cache_data
def load_data(uploaded_files):
    data_frames = {}
    for file in uploaded_files:
        key = file.name.split('/')[-1].split('.')[0].lower()
        try:
            # Efficiently read CSV with proper error handling and feedback
            df = pd.read_csv(file, delimiter=',', on_bad_lines='skip')
        except Exception as e:
            st.error(f"Failed to read {key}: {e}")  # Streamlit error display
            continue
        data_frames[key] = df
    return data_frames

# Function to perform analysis (modify this based on the actual analysis needed)
def analyze_data(data):
    # Example analysis: Get summary statistics
    return data.describe()

# Streamlit app
def main():
    st.title('6degrees network analysis')

    # File uploader allows user to upload multiple CSV files
    uploaded_files = st.file_uploader("Choose CSV files", accept_multiple_files=True, type='csv')
    if uploaded_files: 
        data = load_data(uploaded_files)
        
        # Questions section
        st.header("Questions for Analysis")
        question1 = st.text_input("What is your current goal?")
        question2 = st.text_input("Please describe your ICP/target market?")
        question3 = st.text_input("Which industries are you interested in?")
        
        if st.button("Analyze"):
            # Data analysis based on questions
            analysis_result = analyze_data(data)
            
            # Creating tabs for different insights and graphs
            tab1, tab2, tab3 = st.tabs(["Big tech", "Founders", "Investors"])
            
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
