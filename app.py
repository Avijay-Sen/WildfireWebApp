# -*- coding: utf-8 -*-
"""app.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1F_HL9IXSQ01edjQJnHgzGpkDFPVDOwY6
"""

import streamlit as st
import requests
import json

from config import COUNTRY_CODES, WEATHER_API_KEY
from rag import generate_answer

CONTEXT_TEMPLATE = """
Weather condition of the city {city} is {weather_condition}.
Tempertaure is {temp}. Temperature feels link {temp_feel}. Minimum temperature is {temp_min} while maximum temperature is {temp_max}. All the temperatures are in Kelvin.
Humidity is {humidity}%.
Pressure is {pressure} hPa.
Visibility in meters {visibility}.
Wind speed is {wind_speed} in meter/sec and direction is {wind_deg} in degrees.
Based on this weather data, is there a wildfire risk in this area?
"""

# Convert temperature from Kelvin to Fahrenheit
def kelvin_to_fahrenheit(kelvin):
    return (kelvin - 273.15) * 9/5 + 32

def create_url(country_code: str, state: str, city: str) -> str:
    return f'http://api.openweathermap.org/data/2.5/weather?q={city},{state},{country_code}&APPID={WEATHER_API_KEY}'


def get_weather_data(url: str):
    r = requests.get(url)
    response = getattr(r,'_content').decode("utf-8")
    response = json.loads(response)
    weather_data = response.get("weather", None)
    try:
        main_data = response["main"]
        wind_data = response["wind"]
        cloud_data = response["clouds"]
        # Create a dictionary of data
        weather_dict = {}
        if weather_data:
            weather_dict["weather_condition"] = weather_data[0]["main"]
        else:
            weather_dict["weather_condition"] = "Not available"

        # Convert temperatures to Fahrenheit
        weather_dict["temp"] = main_data["temp"]
        weather_dict["temp_f"] = kelvin_to_fahrenheit(main_data["temp"])
        weather_dict["temp_feel"] = main_data["feels_like"]
        weather_dict["temp_feel_f"] = kelvin_to_fahrenheit(main_data["feels_like"])
        weather_dict["temp_min"] = main_data["temp_min"]
        weather_dict["temp_min_f"] = kelvin_to_fahrenheit(main_data["temp_min"])
        weather_dict["temp_max"] = main_data["temp_max"]
        weather_dict["temp_max_f"] = kelvin_to_fahrenheit(main_data["temp_max"])
        weather_dict["pressure"] = main_data["pressure"]
        weather_dict["humidity"] = main_data["humidity"]
        weather_dict["visibility"] = response.get("visibility", "Not available")
        weather_dict["wind_speed"] = wind_data["speed"]
        weather_dict["wind_deg"] = wind_data["deg"]
    except Exception as error:
        weather_dict = None

    return weather_dict
#def get_weather_data(url: str):
  #  r = requests.get(url)
   # response = getattr(r,'_content').decode("utf-8")
    #response = json.loads(response)
    #weather_data = response.get("weather", None)
 #   try:
  #      main_data = response["main"]
   #     wind_data = response["wind"]
    #    cloud_data = response["clouds"]
        # create a dictionary of data
     #   weather_dict = {}
      #  if weather_data:
#            weather_dict["weather_condition"] = weather_data[0]["main"]
 #       else:
  #        weather_dict["weather_condition"] = "not available"
   #     weather_dict["temp"] = response["main"]["temp"]
  #      weather_dict["temp_feel"] = response["main"]["feels_like"]
   #     weather_dict["temp_min"] = response["main"]["temp_min"]
    #    weather_dict["temp_max"] = response["main"]["temp_max"]
     #   weather_dict["pressure"] = response["main"]["pressure"]
      #  weather_dict["humidity"] = response["main"]["humidity"]
       # weather_dict["sea_level"] = response["main"]["sea_level"]
       # weather_dict["ground_level"] = response["main"]["grnd_level"]
       # weather_dict["visibility"] = response["visibility"]
       # weather_dict["wind_speed"] = response["wind"]["speed"]
       # weather_dict["wind_deg"] = response["wind"]["deg"]
  #  except Exception as error:
   #     weather_dict = None
    #    main_data = None
     #   wind_data = None
      #  cloud_data = None

   # return main_data, wind_data, cloud_data, weather_data, weather_dict

# set a title
st.title("Smokey-Wildfire Predictor")

st.markdown("""
Welcome to the Smokey-Wildfire Predictor app! 🌍
Enter your location details to check the current weather conditions and assess the potential risk of wildfires.
Stay informed and stay safe!
""")

st.markdown(
    """
    <style>
        .reportview-container {
            background: #ff6f47;
        }
        .sidebar .sidebar-content {
            background: #c28961;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Set the image (correct URL)
IMAGE_ADDRESS = "https://raw.githubusercontent.com/Avijay-Sen/WildfireWebApp/main/SmokeyAppIcon.png"
st.image(IMAGE_ADDRESS, use_column_width=True)

# User needs to select a country, state, and city
st.subheader("Enter your location")

country = st.selectbox("Select your Country", list(COUNTRY_CODES.keys()), index=0)

state = st.text_input("State", value="")
city_name = st.text_input("City Name", value="")

if country and state and city_name:
    weather_url = create_url(COUNTRY_CODES[country], state, city_name)
    dict_weather_data = get_weather_data(weather_url)

    if not dict_weather_data:
        st.error("Could not fetch weather data. Please check the city and state names.", icon="🛑")
    else:
        dict_weather_data["city"] = city_name
        dict_weather_data["state"] = state


# Assuming you have already called get_weather_data and stored the result
dict_weather_data = get_weather_data(weather_url)

if dict_weather_data:
    # Display data in the sidebar
    st.sidebar.header("Weather Overview")
    st.sidebar.write(f"Condition: **{dict_weather_data['weather_condition']}**")
    st.sidebar.write(f"Temperature: **{dict_weather_data['temp']:.2f}°F**")
    st.sidebar.write(f"Feels Like: **{dict_weather_data['temp_feel']:.2f}°F**")
    st.sidebar.write(f"Min: **{dict_weather_data['temp_min']:.2f}°F**")
    st.sidebar.write(f"Max: **{dict_weather_data['temp_max']:.2f}°F**")
    st.sidebar.write(f"Humidity: **{dict_weather_data['humidity']}%**")
    st.sidebar.write(f"Pressure: **{dict_weather_data['pressure']} hPa**")
    st.sidebar.write(f"Visibility: **{dict_weather_data['visibility']} meters**")
    st.sidebar.write(f"Wind Speed: **{dict_weather_data['wind_speed']} m/s**")

#if country:
    # set the text input
    #city_name = st.text_input("City Name", value = None)
    #if city_name:
        #weather_url = create_url(COUNTRY_CODES[country], city_name)
        # get weather data
        #main_data, wind_data, cloud_data, weather_data, dict_weather_data = get_weather_data(weather_url)
        #if not dict_weather_data:
           # st.error("Check the City Name: Cannot fetch weather data", icon = "🛑")
           # st.stop()
       # st.write(dict_weather_data)
       # dict_weather_data["city"] = city_name
       # with st.sidebar:
           # if weather_data:
               # st.subheader("Weather Condition")
               # st.write(weather_data[0])
           # st.subheader("Temperature Statistics")
           # st.write(main_data)
           # st.subheader("Wind and Cloud Data")
          #  st.write(wind_data)
          #  st.write(cloud_data)

        # Use columns for a cleaner display
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Current Weather")
            st.write(f"Condition: {dict_weather_data['weather_condition']}")
            st.write(f"Temperature: {dict_weather_data['temp_f']:.2f}°F")
            st.write(f"Feels Like: {dict_weather_data['temp_feel_f']:.2f}°F")
            st.write(f"Min: {dict_weather_data['temp_min_f']:.2f}°F, Max: {dict_weather_data['temp_max_f']:.2f}°F")
        
        with col2:
            st.subheader("Other Weather Details")
            st.write(f"Humidity: {dict_weather_data['humidity']}%")
            st.write(f"Pressure: {dict_weather_data['pressure']} hPa")
            st.write(f"Visibility: {dict_weather_data['visibility']} meters")
            st.write(f"Wind: {dict_weather_data['wind_speed']} m/s, {dict_weather_data['wind_deg']}°")
            
            # create the query
        query = CONTEXT_TEMPLATE.format(**dict_weather_data)
        # get the answer
        with st.spinner('Getting Predictions'):
            answer = generate_answer(query, country)
            st.toast("Prediction Completed!", icon = "✅")
        st.subheader("Predictions")
        st.write(answer)
