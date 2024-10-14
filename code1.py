import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Define constants
EARTH_RADIUS = 6371  # in km
SATELLITE_ALTITUDE = 500  # in km above Earth surface
TIME_INTERVAL = 60  # 1 minute in seconds
SIMULATION_STEPS = 360
DEBRIS_COUNT = 10


# Generate random debris data
def generate_debris_data(count):
    angles = np.linspace(0, 2 * np.pi, count, endpoint=False)
    radius = EARTH_RADIUS + SATELLITE_ALTITUDE + np.random.uniform(-50, 50, count)
    velocities = [(np.random.uniform(-1, 1), np.random.uniform(-1, 1)) for _ in range(count)]
    return radius, angles, velocities


# Predict debris positions
def predict_positions(radii, angles, velocities, time_step):
    new_angles = angles + np.array([v[0] for v in velocities]) * time_step
    positions = [(r * np.cos(angle), r * np.sin(angle)) for r, angle in zip(radii, new_angles)]
    return positions, new_angles


# Calculate collision risk (simple distance-based approach)
def calculate_collision_risk(satellite_pos, debris_positions, threshold=100):
    risks = []
    for debris in debris_positions:
        distance = np.sqrt((satellite_pos[0] - debris[0]) ** 2 + (satellite_pos[1] - debris[1]) ** 2)
        if distance < threshold:
            risks.append((debris, distance))
    return risks


# Plan avoidance maneuver (simple repositioning)
def plan_avoidance_maneuver(satellite_pos, risk_debris):
    if risk_debris:
        new_position = (satellite_pos[0] + 50, satellite_pos[1] + 50)  # simplistic avoidance maneuver
        return new_position
    return satellite_pos


# Initialize data
satellite_radius = EARTH_RADIUS + SATELLITE_ALTITUDE
satellite_angle = 0
satellite_angular_velocity = 2 * np.pi / (24 * 3600)  # One revolution per 24 hours

debris_radii, debris_angles, debris_velocities = generate_debris_data(DEBRIS_COUNT)
satellite_positions = []
debris_positions_over_time = []

# Simulate positions over time
for step in range(SIMULATION_STEPS):
    satellite_position = (satellite_radius * np.cos(satellite_angle), satellite_radius * np.sin(satellite_angle))
    debris_positions, debris_angles = predict_positions(debris_radii, debris_angles, debris_velocities, TIME_INTERVAL)

    satellite_positions.append(satellite_position)
    debris_positions_over_time.append(debris_positions)

    satellite_angle += satellite_angular_velocity * TIME_INTERVAL


# Animation function
def animate(frame):
    ax.clear()

    # Plot Earth
    earth = plt.Circle((0, 0), EARTH_RADIUS, color='blue', alpha=0.3)
    ax.add_artist(earth)

    # Plot satellite position
    sat_pos = satellite_positions[frame]
    ax.plot(*sat_pos, 'go', label='Satellite Position')

    # Plot debris positions
    debris_pos = debris_positions_over_time[frame]
    debris_x, debris_y = zip(*debris_pos)
    ax.plot(debris_x, debris_y, 'rx', label='Debris Position')

    # Mark the axis
    ax.plot([0, sat_pos[0]], [0, sat_pos[1]], 'g--', label='Satellite Axis')
    for debris in debris_pos:
        ax.plot([0, debris[0]], [0, debris[1]], 'r--')

    # Add labels
    ax.text(sat_pos[0], sat_pos[1], 'Satellite', color='green')
    for i, (dx, dy) in enumerate(debris_pos):
        ax.text(dx, dy, f'Debris {i + 1}', color='red')

    # Plot configuration
    ax.set_xlim(-2 * EARTH_RADIUS, 2 * EARTH_RADIUS)
    ax.set_ylim(-2 * EARTH_RADIUS, 2 * EARTH_RADIUS)
    ax.set_aspect('equal')
    plt.legend(loc='upper right')
    plt.xlabel('X Position (km)')
    plt.ylabel('Y Position (km)')
    plt.title('Satellite and Debris Circular Orbits Animation')
    plt.grid(True)


# Set up the figure and axis
fig, ax = plt.subplots()

# Create the animation
ani = animation.FuncAnimation(fig, animate, frames=SIMULATION_STEPS, interval=100, repeat=False)

# Show the animation
plt.show()
