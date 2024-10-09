# -*- coding: utf-8 -*-
import streamlit as st
import requests
import json
import numpy as np  # Assuming historical data is in numpy format

from config import COUNTRY_CODES, WEATHER_API_KEY
from rag import generate_answer

# Load your vectorized historical data (replace with actual file path and method)
# Assuming it's a numpy array saved as 'vectorized_data.npy'
historical_data = np.load('vectorized_data.npy')

CONTEXT_TEMPLATE = """
Weather condition of the city {city} is {weather_condition}.
Temperature is {temp_f}°F. Temperature feels like {temp_feel_f}°F. 
Minimum temperature is {temp_min_f}°F while maximum temperature is {temp_max_f}°F.
Humidity is {humidity}%.
Pressure is {pressure} hPa.
Visibility is {visibility} meters.
Wind speed is {wind_speed} m/s and direction is {wind_deg} degrees.

Historical data indicates a {historical_risk}% risk of wildfire in similar conditions.
Based on the combined historical and current weather data, is there a wildfire risk in this area?
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
        weather_dict = {}

        if weather_data:
            weather_dict["weather_condition"] = weather_data[0]["main"]
        else:
            weather_dict["weather_condition"] = "Not available"

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

def get_historical_risk(vectorized_data, weather_data):
    # Function to calculate historical wildfire risk based on vectorized historical data and live weather data
    # This is a placeholder; replace with your actual logic or model
    # Example: Use weather data to match historical patterns
    temp_factor = weather_data['temp_f'] / np.max(vectorized_data[:, 0])  # Normalize against historical max temp
    wind_factor = weather_data['wind_speed'] / np.max(vectorized_data[:, 1])  # Normalize against historical wind speed
    historical_risk = (temp_factor + wind_factor) * 50  # A simple risk calculation, you can refine it

    return historical_risk

# Streamlit interface
st.title("Smokey-Wildfire Predictor")

st.markdown("""
Welcome to the Smokey-Wildfire Predictor app! 🌍
Enter your location details to check the current weather conditions and assess the potential risk of wildfires.
Stay informed and stay safe!
""")

# Get user input
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
        
        # Calculate historical wildfire risk using vectorized historical data
        historical_risk = get_historical_risk(historical_data, dict_weather_data)
        dict_weather_data["historical_risk"] = round(historical_risk, 2)

        # Display the current weather data and historical risk
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
            st.write(f"Historical Wildfire Risk: {dict_weather_data['historical_risk']}%")

        # Create the query using both live and historical data
        query = CONTEXT_TEMPLATE.format(**dict_weather_data)

        # Get prediction
        with st.spinner('Getting Predictions...'):
            answer = generate_answer(query, country)
            st.toast("Prediction Completed!", icon="✅")

        st.subheader("Prediction")
        st.write(answer)
