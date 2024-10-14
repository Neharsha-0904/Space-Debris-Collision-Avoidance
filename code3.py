import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import requests
from datetime import datetime

# Constants
EARTH_RADIUS = 6371  # km
LAUNCH_LAT = 28.5721  # Latitude for Kennedy Space Center
LAUNCH_LON = -80.6480  # Longitude for Kennedy Space Center
TARGET_ORBIT_ALTITUDE = 500  # km
TIME_INTERVAL = 1  # seconds
SIMULATION_DURATION = 600  # seconds
INITIAL_VELOCITY = 0  # km/s
INITIAL_WEIGHT = 500000  # kg
FUEL_DENSITY = 0.8  # kg/L
INITIAL_FUEL_WEIGHT = 300000  # kg
DEBRIS_COUNT = 200  # Number of debris
SATELLITE_COUNT = 50  # Number of existing satellites
COLLISION_THRESHOLD = 100  # in km

# API key for OpenWeather (replace with your own API key)
API_KEY = 'your_openweather_api_key'


# Generate random debris and satellite data
def generate_object_data(count, altitude_range):
    angles = np.linspace(0, 2 * np.pi, count, endpoint=False)
    radii = EARTH_RADIUS + altitude_range + np.random.uniform(-50, 50, count)
    return radii, angles


# Get weather data
def get_weather_data(lat, lon):
    url = f'http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}'
    response = requests.get(url)
    data = response.json()
    if 'main' in data and 'wind' in data:
        return {
            "temperature": data["main"]["temp"] - 273.15,  # Kelvin to Celsius
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "wind_speed": data["wind"]["speed"],  # in m/s
            "wind_deg": data["wind"]["deg"]
        }
    else:
        # Default values if API data is not available
        return {
            "temperature": 20.0,  # Celsius
            "humidity": 50,  # Percentage
            "pressure": 1013,  # hPa
            "wind_speed": 5,  # m/s
            "wind_deg": 0  # Degrees
        }


# Calculate launch trajectory
def calculate_trajectory(simulation_time):
    trajectory = []
    for t in range(simulation_time):
        if t < simulation_time / 3:
            altitude = EARTH_RADIUS + (t / (simulation_time / 3)) * TARGET_ORBIT_ALTITUDE / 2
            x = 0
            y = altitude
        elif t < 2 * simulation_time / 3:
            u = t - simulation_time / 3
            v = simulation_time / 3
            altitude = EARTH_RADIUS + TARGET_ORBIT_ALTITUDE / 2 + (u / v) * TARGET_ORBIT_ALTITUDE / 2
            x = (u / v) * TARGET_ORBIT_ALTITUDE / 2
            y = altitude
        else:
            u = t - 2 * simulation_time / 3
            v = simulation_time / 3
            x = (u / v) * TARGET_ORBIT_ALTITUDE / 2 + TARGET_ORBIT_ALTITUDE / 2
            y = EARTH_RADIUS + TARGET_ORBIT_ALTITUDE
        trajectory.append((x, y))
    return trajectory


trajectory = calculate_trajectory(SIMULATION_DURATION)

# Generate debris and satellite data
debris_radii, debris_angles = generate_object_data(DEBRIS_COUNT, TARGET_ORBIT_ALTITUDE)
satellite_radii, satellite_angles = generate_object_data(SATELLITE_COUNT, TARGET_ORBIT_ALTITUDE + 100)

# Initialize data lists
positions = []
velocities = []
fuel_weights = []
weights = []

# Initial conditions
current_velocity = INITIAL_VELOCITY
current_weight = INITIAL_WEIGHT
current_fuel_weight = INITIAL_FUEL_WEIGHT


# Function to update plot
def update(frame):
    global current_velocity, current_weight, current_fuel_weight

    ax.clear()

    # Get current weather data
    weather_data = get_weather_data(LAUNCH_LAT, LAUNCH_LON)
    wind_speed = weather_data['wind_speed']
    wind_deg = weather_data['wind_deg']

    # Adjust launch trajectory for wind
    wind_adjustment_x = np.cos(np.radians(wind_deg)) * wind_speed * frame / 1000
    wind_adjustment_y = np.sin(np.radians(wind_deg)) * wind_speed * frame / 1000

    # Get launch vehicle position
    x, y = trajectory[frame]
    x += wind_adjustment_x
    y += wind_adjustment_y

    # Update lists
    positions.append((x, y))
    velocities.append(current_velocity)
    fuel_weights.append(current_fuel_weight)
    weights.append(current_weight)

    # Update current conditions (simplified linear fuel burn and velocity increase)
    current_fuel_weight -= 0.5  # kg per second
    current_weight -= 0.5  # kg per second
    current_velocity += 0.01  # km/s per second

    # Plot Earth
    earth = plt.Circle((0, 0), EARTH_RADIUS, color='blue', alpha=0.3)
    ax.add_artist(earth)

    # Plot launch vehicle with trajectory
    positions_x, positions_y = zip(*positions)
    ax.plot(positions_x, positions_y, 'g--', label='Trajectory')
    ax.plot(x, y, 'go', label='Launch Vehicle')

    # Plot debris and satellites
    debris_x = debris_radii * np.cos(debris_angles + frame / 100)
    debris_y = debris_radii * np.sin(debris_angles + frame / 100)
    satellite_x = satellite_radii * np.cos(satellite_angles + frame / 100)
    satellite_y = satellite_radii * np.sin(satellite_angles + frame / 100)
    ax.scatter(debris_x, debris_y, color='red', s=1, label='Debris')
    ax.scatter(satellite_x, satellite_y, color='orange', s=2, label='Satellites')

    # Set plot limits and labels
    ax.set_xlim(-EARTH_RADIUS * 2, EARTH_RADIUS * 2)
    ax.set_ylim(0, EARTH_RADIUS * 3)
    ax.set_aspect('equal')
    ax.set_xlabel('X (km)')
    ax.set_ylabel('Y (km)')
    ax.set_title(f'Launch Simulation: T+{frame * TIME_INTERVAL}s')

    # Display vehicle data
    ax.text(-EARTH_RADIUS * 1.8, EARTH_RADIUS * 2.7,
            f'Velocity: {current_velocity:.2f} km/s\n'
            f'Weight: {current_weight:.2f} kg\n'
            f'Fuel Density: {FUEL_DENSITY} kg/L\n'
            f'Fuel Weight: {current_fuel_weight:.2f} kg\n'
            f'Fuel Left: {current_fuel_weight:.2f} kg\n'
            f'Time: {frame * TIME_INTERVAL}s',
            fontsize=10)

    # Display weather data
    ax.text(-EARTH_RADIUS * 1.8, EARTH_RADIUS * 2.2,
            f'Temperature: {weather_data["temperature"]:.2f} °C\n'
            f'Humidity: {weather_data["humidity"]} %\n'
            f'Pressure: {weather_data["pressure"]} hPa\n'
            f'Wind Speed: {weather_data["wind_speed"]} m/s\n'
            f'Wind Direction: {weather_data["wind_deg"]}°',
            fontsize=5)

    ax.legend()


# Create animation
fig, ax = plt.subplots()
ani = FuncAnimation(fig, update, frames=SIMULATION_DURATION, interval=TIME_INTERVAL * 1000 / 60, repeat=False)
plt.show()
