import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D
import requests

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
    latitudes = np.random.uniform(-90, 90, count)
    longitudes = np.random.uniform(-180, 180, count)
    altitudes = np.random.uniform(altitude_range - 50, altitude_range + 50, count)
    return latitudes, longitudes, altitudes


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


# Convert lat, lon, alt to Cartesian coordinates
def lat_lon_alt_to_cartesian(lat, lon, alt):
    lat, lon = np.radians(lat), np.radians(lon)
    r = EARTH_RADIUS + alt
    x = r * np.cos(lat) * np.cos(lon)
    y = r * np.cos(lat) * np.sin(lon)
    z = r * np.sin(lat)
    return x, y, z


# Calculate launch trajectory
def calculate_trajectory(simulation_time):
    trajectory = []
    for t in range(simulation_time):
        if t < simulation_time / 3:
            altitude = (t / (simulation_time / 3)) * TARGET_ORBIT_ALTITUDE / 2
        elif t < 2 * simulation_time / 3:
            u = t - simulation_time / 3
            v = simulation_time / 3
            altitude = TARGET_ORBIT_ALTITUDE / 2 + (u / v) * TARGET_ORBIT_ALTITUDE / 2
        else:
            u = t - 2 * simulation_time / 3
            v = simulation_time / 3
            altitude = TARGET_ORBIT_ALTITUDE + (u / v) * TARGET_ORBIT_ALTITUDE / 2
        trajectory.append(altitude)
    return trajectory


trajectory_altitudes = calculate_trajectory(SIMULATION_DURATION)
trajectory_latitudes = np.linspace(LAUNCH_LAT, LAUNCH_LAT, SIMULATION_DURATION)
trajectory_longitudes = np.linspace(LAUNCH_LON, LAUNCH_LON, SIMULATION_DURATION)

# Generate debris and satellite data
debris_latitudes, debris_longitudes, debris_altitudes = generate_object_data(DEBRIS_COUNT, TARGET_ORBIT_ALTITUDE)
satellite_latitudes, satellite_longitudes, satellite_altitudes = generate_object_data(SATELLITE_COUNT,
                                                                                      TARGET_ORBIT_ALTITUDE + 100)

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
    wind_adjustment = np.cos(np.radians(wind_deg)) * wind_speed * frame / 1000

    # Get launch vehicle position
    lat, lon, alt = trajectory_latitudes[frame], trajectory_longitudes[frame], trajectory_altitudes[
        frame] + wind_adjustment
    x, y, z = lat_lon_alt_to_cartesian(lat, lon, alt)

    # Update lists
    positions.append((x, y, z))
    velocities.append(current_velocity)
    fuel_weights.append(current_fuel_weight)
    weights.append(current_weight)

    # Update current conditions (simplified linear fuel burn and velocity increase)
    current_fuel_weight -= 0.5  # kg per second
    current_weight -= 0.5  # kg per second
    current_velocity += 0.01  # km/s per second

    # Convert debris and satellite positions to Cartesian coordinates
    debris_x, debris_y, debris_z = lat_lon_alt_to_cartesian(debris_latitudes, debris_longitudes, debris_altitudes)
    satellite_x, satellite_y, satellite_z = lat_lon_alt_to_cartesian(satellite_latitudes, satellite_longitudes,
                                                                     satellite_altitudes)

    # Plot trajectory
    positions_x, positions_y, positions_z = zip(*positions)
    ax.plot3D(positions_x, positions_y, positions_z, 'g--', label='Trajectory')
    ax.scatter3D(x, y, z, color='green', label='Launch Vehicle')

    # Plot debris and satellites
    ax.scatter3D(debris_x, debris_y, debris_z, color='red', s=1, label='Debris')
    ax.scatter3D(satellite_x, satellite_y, satellite_z, color='orange', s=2, label='Satellites')

    # Set plot limits and labels
    ax.set_xlim(-EARTH_RADIUS * 1.5, EARTH_RADIUS * 1.5)
    ax.set_ylim(-EARTH_RADIUS * 1.5, EARTH_RADIUS * 1.5)
    ax.set_zlim(0, EARTH_RADIUS * 2)
    ax.set_xlabel('X (km)')
    ax.set_ylabel('Y (km)')
    ax.set_zlabel('Z (km)')
    ax.set_title(f'Launch Simulation: T+{frame * TIME_INTERVAL}s')

    # Display vehicle data
    ax.text2D(0.05, 0.95, f'Velocity: {current_velocity:.2f} km/s\n'
                          f'Weight: {current_weight:.2f} kg\n'
                          f'Fuel Density: {FUEL_DENSITY} kg/L\n'
                          f'Fuel Weight: {current_fuel_weight:.2f} kg\n'
                          f'Fuel Left: {current_fuel_weight:.2f} kg\n'
                          f'Time: {frame * TIME_INTERVAL}s',
              transform=ax.transAxes, fontsize=10)

    # Display weather data
    ax.text2D(0.05, 0.45, f'Temperature: {weather_data["temperature"]:.2f} °C\n'
                          f'Humidity: {weather_data["humidity"]} %\n'
                          f'Pressure: {weather_data["pressure"]} hPa\n'
                          f'Wind Speed: {weather_data["wind_speed"]} m/s\n'
                          f'Wind Direction: {weather_data["wind_deg"]}°',
              transform=ax.transAxes, fontsize=10)

    ax.legend()


# Create animation
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ani = FuncAnimation(fig, update, frames=SIMULATION_DURATION, interval=TIME_INTERVAL * 1000 / 60, repeat=False)
plt.show()
