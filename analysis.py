import pandas as pd
import plotly.express as px

def count_messages(messages):
    """
    Takes messages CSV and returns a dataframe with the URLs of other users and the count of total messages exchanged with them. 
    """
    # Extract all sender URLs
    sender_urls = messages['SENDER PROFILE URL'].tolist()
    
    # Extract and split the recipient URLs into individual URLs    
    recipient_urls = messages['RECIPIENT PROFILE URLS'].fillna('').apply(lambda x: x.split(',') if isinstance(x, str) else [])

    # Flatten the list of lists while ensuring that each element is indeed a list
    flattened_urls = [url for sublist in recipient_urls for url in sublist if isinstance(sublist, list)]

    # Now continue with your analysis...
    # For example, count occurrences of each URL
    url_counts = pd.Series(flattened_urls).value_counts().reset_index()
    url_counts.columns = ['URL', 'Count']
    
    return url_counts


def add_connection_direction(connections, invitations):
    """
    Takes connections and invitations dataframes and add the connection direction to the connection df. 
    """
    # Select only relevant columns from invitations for merging
    inviter_data = invitations[['inviterProfileUrl', 'Direction']]
    invitee_data = invitations[['inviteeProfileUrl', 'Direction']]
    
    # Merge to find matches with inviterProfileUrl
    merged_inviter = pd.merge(connections, inviter_data, left_on='URL', right_on='inviterProfileUrl', how='left')
    
    # Merge to find matches with inviteeProfileUrl
    merged_invitee = pd.merge(connections, invitee_data, left_on='URL', right_on='inviteeProfileUrl', how='left')
    
    # Create the 'connection type' column based on 'Direction' from both merges
    connections['connection type'] = merged_inviter['Direction'].fillna(merged_invitee['Direction'])
    
    # Replace NaN values with an empty string
    connections['connection type'] = connections['connection type'].fillna('')
    
    # Optional: Drop columns from the merges if they are not needed
    connections.drop(columns=['inviterProfileUrl', 'inviteeProfileUrl'], errors='ignore', inplace=True)
    
    return connections

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

