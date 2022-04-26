import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px
st.header("DASHBOARD FOR ACCIDENT VISUALIZATION IN MAURITIUS")
DATA_URL = ("D:/Accident_data/cases.csv")

@st.cache(persist=True)
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows, parse_dates=[['Month', 'Year', 'Time']])
    data.rename(columns={'Month_Year_Time': 'date/time'}, inplace=True)
    return data

data =load_data(5000)
original_data = data
st.header("Locations of injury road accidents")
injured_people = st.slider("Slide to show the number of persons injured in road accidents", 0, 30)
st.map(data.query("Number_of_Casualties >= @injured_people")[["latitude", "longitude"]].dropna(how="any"))


st.header("How many collisions occurred during a given time of day?")
hour = st.slider("Hour to look at", 0, 23)
data = data[data['date/time'].dt.hour == hour]

st.markdown("Vehicle collisions between %i:00 and %i:00" % (hour, (hour + 1) % 24))

midpoint = (np.average(data["latitude"]), np.average(data["longitude"]))
st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 11,
        "pitch": 50,
    },
    layers=[
        pdk.Layer(
        "HexagonLayer",
        data=data[['date/time', 'latitude', 'longitude']],
        get_position=["longitude", "latitude"],
        auto_highlight=True,
        radius=500,
        extruded=True,
        pickable=True,
        elevation_scale=10,
        elevation_range=[0, 1000],
        ),
    ],
))

if st.checkbox("Show Raw Data", False):
    st.subheader('Raw Data')
    st.write(data)

st.subheader("Breakdown by minute between %i:00 and %i:00" % (hour, (hour + 1) % 24))
filtered = data[
    (data['date/time'].dt.hour >= hour) & (data['date/time'].dt.hour < (hour + 1))
]
hist = np.histogram(filtered['date/time'].dt.minute, bins=60, range=(0, 60))[0]
chart_data = pd.DataFrame({"minute": range(60), "crashes": hist})

fig = px.bar(chart_data, x='minute', y='crashes', hover_data=['minute', 'crashes'], height=400)
st.write(fig)

st.header("Locations by accident severity")
injured_people1 = st.selectbox('Select the desired Accident Severity', ['Fatal', 'Serious', 'Slight'])
st.map(original_data.query("Accident_Severity == @injured_people1")[["latitude", "longitude"]].dropna(how="any"))
