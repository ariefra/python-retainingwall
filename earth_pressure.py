
import math

def calculate_ka(phi_deg, beta_deg=0):
    """Calculates Rankine's active earth pressure coefficient for horizontal or sloped backfill."""
    phi_rad = math.radians(phi_deg)
    beta_rad = math.radians(beta_deg)
    if beta_deg == 0:
        return math.tan(math.pi/4 - phi_rad/2)**2
    else:
        # Rankine's active earth pressure coefficient for sloped backfill
        # K_a = cos(beta) * ((cos(beta) - sqrt(cos(beta)^2 - cos(phi)^2)) / (cos(beta) + sqrt(cos(beta)^2 - cos(phi)^2)))
        numerator = math.cos(beta_rad) - math.sqrt(math.cos(beta_rad)**2 - math.cos(phi_rad)**2)
        denominator = math.cos(beta_rad) + math.sqrt(math.cos(beta_rad)**2 - math.cos(phi_rad)**2)
        return math.cos(beta_rad) * (numerator / denominator)

def calculate_kp(phi_deg):
    """Calculates Rankine's passive earth pressure coefficient."""
    phi_rad = math.radians(phi_deg)
    return math.tan(math.pi/4 + phi_rad/2)**2

def calculate_earth_pressure(soil_props, height, groundwater_depth=None, is_active=True, surcharge_load=0.0, active_side_slope_height=0.0):
    """Calculates earth pressure at a given depth, including surcharge effect and slope effect."""
    gamma = soil_props["unit_weight_kn_m3"]
    phi = soil_props["friction_angle_deg"]
    c = soil_props["cohesion_kpa"]

    beta_deg = 0 # Angle of backfill with horizontal
    if is_active and active_side_slope_height > 0:
        # Assuming a 1V:2H slope for now, so beta = atan(1/2) = 26.565 degrees
        beta_deg = 26.565 # This should ideally be derived from geometry

    if is_active:
        K = calculate_ka(phi, beta_deg)
    else:
        K = calculate_kp(phi)

    pressure = gamma * height * K + surcharge_load * K # Add surcharge effect

    # Simplified groundwater effect (assuming submerged unit weight for soil below GWL)
    if groundwater_depth is not None and height > groundwater_depth:
        gamma_submerged = gamma - 9.81 # Assuming unit weight of water is 9.81 kN/m^3
        pressure_above_gw = gamma * groundwater_depth * K
        pressure_below_gw = gamma_submerged * (height - groundwater_depth) * K + 9.81 * (height - groundwater_depth) # Add hydrostatic pressure
        pressure = pressure_above_gw + pressure_below_gw

    return pressure

def calculate_point_load_effect(point_load, distance_from_wall, H_total, phi_deg):
    """Calculates the horizontal pressure due to a point load (simplified).
    This is a very simplified approach, assuming a triangular distribution from the point of application.
    More rigorous methods (e.g., Boussinesq) exist for accurate analysis.
    """
    # For simplicity, assume the point load creates a triangular pressure distribution
    # that starts at the depth of application and extends to the base of the wall.
    # The maximum pressure is at the point of application and decreases linearly to zero at the base.
    # This is a highly simplified model and should be used with caution.

    # Assuming the point load acts at the ground surface for simplicity in this initial implementation.
    # The horizontal pressure at any depth z due to a point load Q at distance x from the wall
    # can be approximated by a simplified formula (e.g., based on a 2:1 stress distribution).
    # For this simplified model, let's assume the point load creates an equivalent horizontal force
    # that is distributed over the height of the wall below the point of application.

    # This is a placeholder. A more accurate model would involve integrating Boussinesq's equation
    # or using pressure distribution diagrams for point loads.

    # For now, let's assume the point load contributes to an equivalent horizontal force
    # that acts at 2/3 of the height from the base, similar to a triangular pressure.
    # This is a very rough approximation.

    # A very simplified approach: treat point load as an equivalent horizontal force
    # acting at the height of the wall, and apply it as a concentrated force.
    # This is not a pressure, but a force.
    # For now, return 0.0 and add a note in the report that point load is not fully implemented.
    return 0.0
