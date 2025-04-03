import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import matplotlib.pyplot as plt

# Function to create an interactive map
def create_map(station_data):
    # Check if 'Latitude' and 'Longitude' columns exist
    if 'LatitudeMeasure' in station_data.columns and 'LongitudeMeasure' in station_data.columns:
        # Create a map centered around the average latitude and longitude
        m = folium.Map(location=[station_data['LatitudeMeasure'].mean(), station_data['LongitudeMeasure'].mean()], zoom_start=10)
        
        # Add markers for each station
        for _, row in station_data.iterrows():
            folium.Marker(
                location=[row['LatitudeMeasure'], row['LongitudeMeasure']],
                popup=row['MonitoringLocationName']
            ).add_to(m)
        
        return m
    else:
        st.error("The station data must contain 'LatitudeMeasure' and 'LongitudeMeasure' columns.")
        return None

# Function to plot water quality data
def plot_water_quality(data, characteristic, start_date, end_date, min_value, max_value):
    # Convert ActivityStartDate to datetime format
    data['ActivityStartDate'] = pd.to_datetime(data['ActivityStartDate'])
    
    # Ensure start_date and end_date are in datetime format
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    
    # Filter data based on user input and exclude empty or NaN values
    filtered_data = data[(data['CharacteristicName'] == characteristic) &
                         (data['ActivityStartDate'] >= start_date) &
                         (data['ActivityStartDate'] <= end_date) &
                         (data['ResultMeasureValue'] >= min_value) &
                         (data['ResultMeasureValue'] <= max_value) &
                         (data['ResultMeasureValue'].notna())]
    
    # Get unique site identifiers
    sites = filtered_data['MonitoringLocationIdentifier'].unique()
    
    # Plot the results with different colors for each site
    plt.figure(figsize=(12, 6))
    
    for site in sites:
        site_data = filtered_data[filtered_data['MonitoringLocationIdentifier'] == site]
        plt.plot(site_data['ActivityStartDate'], site_data['ResultMeasureValue'], label=site)
    
    plt.xlabel('Date')
    plt.ylabel(f'{characteristic} Value')
    plt.title(f'{characteristic} Over Time')
    plt.legend()
    plt.grid(True)
    plt.show()

# Streamlit app
st.title('Water Quality Analysis')

# Upload station data
station_file = st.file_uploader('Upload Station Data CSV', type='csv')
if station_file:
    station_data = pd.read_csv(station_file)
    st.write('Station Data:')
    st.write(station_data)
    
    # Create and display map
    map = create_map(station_data)
    if map:
        folium_static(map)

# Upload water quality data
quality_file = st.file_uploader('Upload Water Quality Data CSV', type='csv')
if quality_file:
    quality_data = pd.read_csv(quality_file)
    
    # Convert ResultMeasureValue to numeric, forcing errors to NaN
    quality_data['ResultMeasureValue'] = pd.to_numeric(quality_data['ResultMeasureValue'], errors='coerce')
    
    # Convert ActivityStartDate to datetime format
    quality_data['ActivityStartDate'] = pd.to_datetime(quality_data['ActivityStartDate'])
    
    st.write('Water Quality Data:')
    st.write(quality_data)
    
    # User input for filtering data
    characteristic = st.selectbox('Select Characteristic', quality_data['CharacteristicName'].unique())
    start_date = st.date_input('Start Date', value=pd.to_datetime(quality_data['ActivityStartDate']).min())
    end_date = st.date_input('End Date', value=pd.to_datetime(quality_data['ActivityStartDate']).max())
    min_value = st.number_input('Minimum Value', value=quality_data['ResultMeasureValue'].min())
    max_value = st.number_input('Maximum Value', value=quality_data['ResultMeasureValue'].max())
    
    # Plot water quality data based on user input
    if st.button('Plot Data'):
        plot_water_quality(quality_data, characteristic, start_date, end_date, min_value, max_value)
