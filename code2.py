import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Define constants
EARTH_RADIUS = 6371  # in km
SATELLITE_ALTITUDE = 500  # in km above Earth surface
TIME_INTERVAL = 60  # 1 minute in seconds
SIMULATION_DURATION = 600  # in seconds
DEBRIS_COUNT = 200  # Increased number of debris
COLLISION_THRESHOLD = 100  # in km

# Generate random debris data
def generate_debris_data(count):
    angles = np.linspace(0, 2 * np.pi, count, endpoint=False)
    radii = EARTH_RADIUS + SATELLITE_ALTITUDE + np.random.uniform(-50, 50, count)
    return radii, angles

# Generate random satellite data
def generate_satellite_data(count):
    angles = np.linspace(0, 2 * np.pi, count, endpoint=False)
    radii = EARTH_RADIUS + SATELLITE_ALTITUDE + np.random.uniform(50, 150, count)
    return radii, angles

# Calculate distance between two points
def calculate_distance(pos1, pos2):
    return np.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

# Check for collisions between two types of objects (satellite-satellite, satellite-debris)
def detect_collisions(satellite_positions, debris_positions):
    collisions = []
    for i, sat_pos in enumerate(satellite_positions):
        for j, deb_pos in enumerate(debris_positions):
            distance = calculate_distance(sat_pos, deb_pos)
            if distance < COLLISION_THRESHOLD:
                collisions.append(('satellite', i, 'debris', j))
        for k, other_sat_pos in enumerate(satellite_positions):
            if i != k:
                distance = calculate_distance(sat_pos, other_sat_pos)
                if distance < COLLISION_THRESHOLD:
                    collisions.append(('satellite', i, 'satellite', k))
    return collisions

# Refactor satellite positions to avoid collisions
def refactor_satellites(satellite_positions, collisions):
    for obj1_type, obj1_idx, obj2_type, obj2_idx in collisions:
        if obj1_type == 'satellite':
            satellite_positions[obj1_idx] = None  # Mark the satellite for refactoring
        if obj2_type == 'satellite':
            satellite_positions[obj2_idx] = None  # Mark the satellite for refactoring
    # Refactor satellite positions
    for i, sat_pos in enumerate(satellite_positions):
        if sat_pos is None:
            # Implement your refactoring logic here
            # For now, just reset the position to a random point
            satellite_positions[i] = np.random.uniform(-180, 180), np.random.uniform(-90, 90)

# Initialize data
debris_radii, debris_angles = generate_debris_data(DEBRIS_COUNT)
satellite_radii, satellite_angles = generate_satellite_data(DEBRIS_COUNT)

# Function to update plot
def update(frame):
    # Update debris positions
    debris_positions = [(r * np.cos(angle + frame / 100), r * np.sin(angle + frame / 100)) for r, angle in zip(debris_radii, debris_angles)]
    # Update satellite positions
    satellite_positions = [(r * np.cos(angle + frame / 100), r * np.sin(angle + frame / 100)) for r, angle in zip(satellite_radii, satellite_angles)]
    # Detect collisions
    collisions = detect_collisions(satellite_positions, debris_positions)
    # Print collisions
    print(f"Frame: {frame}, Collisions: {collisions}")
    # Refactor satellites
    refactor_satellites(satellite_positions, collisions)
    # Clear previous plot
    ax.clear()
    # Plot Earth
    earth = plt.Circle((0, 0), EARTH_RADIUS, color='blue')
    ax.add_artist(earth)
    # Plot debris
    debris_x, debris_y = zip(*debris_positions)
    ax.scatter(debris_x, debris_y, color='red', label='Debris')
    # Plot satellites
    for i, (x, y) in enumerate(satellite_positions):
        ax.scatter(x, y, color='green', label=f'Satellite {i+1}')
    # Plot collisions
    for obj1_type, obj1_idx, obj2_type, obj2_idx in collisions:
        if obj1_type == 'satellite':
            x, y = satellite_positions[obj1_idx]
            ax.text(x, y, f'Collision between Satellite {obj1_idx+1} and {obj2_type} {obj2_idx+1}', fontsize=8, color='red')
        elif obj2_type == 'satellite':
            x, y = satellite_positions[obj2_idx]
            ax.text(x, y, f'Collision between {obj1_type} {obj1_idx+1} and Satellite {obj2_idx+1}', fontsize=8, color='red')
        else:
            ax.text(x, y, f'Collision between Satellite {obj1_idx+1} and Debris {obj2_idx+1}', fontsize=8, color='red')
    ax.set_xlim(-2 * EARTH_RADIUS, 2 * EARTH_RADIUS)
    ax.set_ylim(-2 * EARTH_RADIUS, 2 * EARTH_RADIUS)
    ax.set_aspect('equal')
    ax.set_title(f"Frame: {frame}")

# Create animation
fig, ax = plt.subplots()
ani = FuncAnimation(fig, update, frames=np.arange(0, SIMULATION_DURATION, TIME_INTERVAL), interval=50, repeat=False)
plt.show()
