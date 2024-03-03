import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

# configure settings for the webpage
st.set_page_config(page_title="Bike Sharing Dashboard", page_icon=":bar_chart:", layout="wide")

# mainpage
st.title(":bar_chart: Bike Sharing Order Summary")
st.markdown("##")

# read the dataset
df = pd.read_csv('dataset.csv')

# function to set up all dataframes
def create_workingday_df(df):
    # filtering condition of working day and non holiday
    workingday = df[(df['workingday'] == 1) & (df['holiday'] == 0)]

    # group by hour and sum the total orders
    workingday_df = workingday.groupby('hour')[['registered', 'casual']].sum().reset_index()

    return workingday_df

def create_non_workingday_df(df):
    # filtering condition of non working day and holiday
    non_workingday = df[(df['workingday'] == 0) & (df['holiday'] == 1)]

    # group by hour and sum the total orders
    non_workingday_df = non_workingday.groupby('hour')[['registered', 'casual']].sum().reset_index()

    return non_workingday_df

def create_weather_df(df):
    weather_df = df.groupby(by="weather").agg({
        'total_rent': 'sum',
        'casual': 'sum',
        'registered': 'sum'
    }).reset_index()
    
    return weather_df

def create_weather_corr_df(df):
    corr_df = df[['temp','humidity','windspeed','casual','registered','total_rent']]
    corr_matrix = corr_df.corr(numeric_only=True, method='spearman')
    corr_matrix = corr_matrix.round(2)

    return corr_matrix

def create_season_df(df):
    season_df = df.groupby(by="season").agg({
        'total_rent': 'sum',
        'casual': 'sum',
        'registered': 'sum'
    }).reset_index()
    
    return season_df

def create_seasons_year_df(df):
    seasons_year_df = df.groupby(by=[df["datetime"].dt.year,df["season"]]).agg({"total_rent": "sum"
    }).reset_index()

    return seasons_year_df

# setting the datetime
datetime_columns = ["datetime"]

df.sort_values(by="datetime", inplace=True)
df.reset_index(inplace=True)

for column in datetime_columns:
    df[column] = pd.to_datetime(df[column])

min_date = df["datetime"].min()
max_date = df["datetime"].max()

# setting the sidebar
with st.sidebar:
    # add logo
    st.image("img/logo.png")
    
    # filtering start_date & end_date from input date
    start_date, end_date = st.date_input(
        label='Filter Date',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

    filtered_df = df[(df["datetime"] >= str(start_date)) & (df["datetime"] <= str(end_date))]

    # call the dataframe function
    workingday_df       = create_workingday_df(filtered_df)
    non_workingday_df   = create_non_workingday_df(filtered_df)
    weather_df          = create_weather_df(filtered_df)
    corr_matrix         = create_weather_corr_df(filtered_df)
    season_df           = create_season_df(filtered_df)
    seasons_year_df     = create_seasons_year_df(filtered_df)

# plotting the line chart of working days
fig = px.line(
    workingday_df, 
    x='hour', 
    y=['registered', 'casual'], 
    labels={'value': 'Total Orders'}, 
    title='Total Orders by Hour of the Day (Working Day)',
    line_dash_sequence=['solid', 'dot'],  
    markers=True,  
    height=600,  
    width=800   
    )
fig.update_layout(xaxis_title='Hour of the Day', yaxis_title='Total Orders')
st.plotly_chart(fig)

st.info("The bike rental pattern on working days shows two highest peaks, indicating that customers tend to rent bikes twice a day, when commuting to work between 7 to 9 o'clock and returning home between 17 to 19 o'clock", icon="💡")

# plotting the line chart of non-working days
fig = px.line(
    non_workingday_df, 
    x='hour', 
    y=['registered', 'casual'], 
    labels={'value': 'Total Orders'}, 
    title='Total Orders by Hour of the Day (Non-Working Day)',
    line_dash_sequence=['solid', 'dot'], 
    markers=True,  
    height=600,  
    width=800   
    )
fig.update_layout(xaxis_title='Hour of the Day', yaxis_title='Total Orders')
st.plotly_chart(fig)

st.info("The bike rental pattern on non-working days is varies, with the average indicating a single peak at a specific hour. On average, the increase occurs within the time range from 12 to 17 o'clock.", icon="💡")

# plotting the bar chart of weathers condition
fig = px.bar(
    weather_df,
    x='weather',
    y=['casual', 'registered', 'total_rent'],
    labels={'weather': 'Weather', 'value': 'Total Orders'},
    title='Total Orders by Weather and User Status',
    color_discrete_map={'casual': 'darkblue', 'registered': 'blue', 'total_rent': 'darkorange'},
    barmode='group',
    height=600,  
    width=800,
)
st.plotly_chart(fig)

st.text(
    "Weather Categories:\n"
    "1: Clear, Few clouds, Partly cloudy, Partly cloudy\n"
    "2: Mist + Cloudy, Mist + Broken clouds, Mist + Few clouds, Mist\n"
    "3: Light Snow, Light Rain + Thunderstorm + Scattered clouds, Light Rain + Scattered clouds\n"
    "4: Heavy Rain + Ice Pallets + Thunderstorm + Mist, Snow + Fog"
)

# plotting the heatmap of variable weathers condition
fig = px.imshow(
    corr_matrix,
    labels=dict(x='Variables', y='Variables', color='Correlation'),
    x=corr_matrix.columns,
    y=corr_matrix.columns,
    color_continuous_scale='Blues',  
    title='Weather Variables Correlation Heatmap',
    color_continuous_midpoint=0,
    text_auto=True,
    height=600,  
    width=800,
)
st.plotly_chart(fig)

st.info("The temperature has a positive correlation with total_rent. For casual users, it is positively correlated with a value of 0.57 and registered with a value of 0.37. Therefore, it can be concluded that the higher the temperature, the more total_rent tends to increase.", icon="💡")

# plotting the bar chart of season category
fig = px.bar(
    season_df,
    x='season',
    y=['casual', 'registered', 'total_rent'],
    labels={'season': 'Season', 'value': 'Total Orders'},
    title='Total Orders by Season and User Status',
    color_discrete_map={'casual': 'darkblue', 'registered': 'blue', 'total_rent': 'darkorange'},
    barmode='group',
    height=600,  
    width=800,
)
st.plotly_chart(fig)

st.info("The Fall season is the category with the highest average number of bicycle rentals followed by the Summer, Winter, and finally the Springer season.", icon="💡")

# plotting the bar chart of year in season
fig = px.bar(
    seasons_year_df,
    x='season',
    y='total_rent',
    color='datetime',
    color_discrete_map={'2,011': 'blue', '2,012': 'darkblue'},
    labels={'total_rent': 'Total Rent'},
    title='Total Rent by Season and Year',
)
fig.update_layout(xaxis_title='Season', yaxis_title='Total Rent')
st.plotly_chart(fig)

st.info("There was an increase in bike rentals across all four seasons from the year 2011 to 2012.", icon="💡")
