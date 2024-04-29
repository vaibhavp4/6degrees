import pandas as pd
import plotly.express as px

def analyse_connections(df):
    """
    Analyzes a LinkedIn connections DataFrame to produce visualizations of:
    1. Connections per year
    2. Top 25 companies by connections
    3. Top 25 positions by connections
    
    Parameters:
        df (pd.DataFrame): The DataFrame containing LinkedIn connection data with columns
                           'Connected On', 'Company', and 'Position'.
                           
    Returns:
        dict: A dictionary of Plotly graph objects where keys are descriptive names of the graphs.
    """
    graphs = {}
    try:
        # Convert 'Connected On' to datetime and extract year
        df['Connected On'] = pd.to_datetime(df['Connected On'], format='%d %b %Y')
        df['year'] = df['Connected On'].dt.year
        
        # Group by year and count connections
        connection_counts = df.groupby('year').size().reset_index(name='count')
        # Plotly bar graph for connections per year
        connections = px.bar(connection_counts, x='year', y='count',
                             title='LinkedIn Connections per Year',
                             color='year', color_continuous_scale='viridis',
                             template='plotly_dark', barmode='group', opacity=0.8)
        graphs['Yearly Connections'] = connections
        
        # Analyze top 25 companies by connection count
        if 'Company' in df.columns:
            company_counts = df.groupby('Company').size().reset_index(name='count')
            top_25_companies = company_counts.sort_values(by='count', ascending=False).head(25)
            companies = px.box(top_25_companies, x='Company', y='count',
                               title='Top 25 Companies by LinkedIn Connections',
                               color='Company', template='plotly_dark')
            graphs['Top 25 Companies'] = companies
        else:
            print("The 'Company' column is missing in the DataFrame.")
        
        # Analyze top 25 positions by connection count
        if 'Position' in df.columns:
            position_counts = df.groupby('Position').size().reset_index(name='count')
            top_25_positions = position_counts.sort_values(by='count', ascending=False).head(25)
            position = px.scatter(top_25_positions, x='Position', y='count',
                                  title='Top 25 Positions by LinkedIn Connections',
                                  color='Position', template='plotly_dark')
            position.update_layout(xaxis_tickangle=45)
            graphs['Top 25 Positions'] = position
        else:
            print("The 'Position' column is missing in the DataFrame.")
        
    except KeyError as e:
        print(f"Error: Missing key in DataFrame - {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return graphs


def analyse_messages(df):
    # TODO: implement function to analyse messages
    pass

def analyse_invitations(df):
    # TODO: implement function to analyse invitations
    pass

