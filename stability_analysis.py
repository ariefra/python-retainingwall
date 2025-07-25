import math
from earth_pressure import calculate_earth_pressure

def perform_stability_analysis(params, geometry, active_soil, passive_soil, wall_material_props, slab_material_props):
    H_total = geometry["H_total"]
    h_wall_stem = geometry["h_wall_stem"]
    D_f = geometry["D_f"]
    B_toe = geometry["B_toe"]
    B_heel = geometry["B_heel"]
    t_top = geometry["t_top"]
    t_base = geometry["t_base"]
    B_base = geometry["B_base"]
    wall_base_offset_from_toe = geometry["wall_base_offset_from_toe"]
    groundwater_level_below_base = geometry["groundwater_level_below_base"]
    shear_key_depth = geometry["shear_key_depth"]
    shear_key_width = geometry["shear_key_width"]
    surcharge_load = geometry["surcharge_load"] # Surcharge load
    point_load = geometry["point_load"] # Point load
    point_load_distance_from_wall = geometry["point_load_distance_from_wall"] # Point load distance
    active_side_ground_elevation = geometry["active_side_ground_elevation"]
    passive_side_ground_elevation = geometry["passive_side_ground_elevation"]
    foundation_lower_than_passive_side = geometry["foundation_lower_than_passive_side"]

    # --- Weights of Wall Components (per unit length) ---
    # Stem Wall (trapezoidal section)
    area_stem = 0.5 * (t_top + t_base) * h_wall_stem
    weight_stem = area_stem * (wall_material_props["unit_weight_kn_m3"] if params["units"] == "metric" else wall_material_props["unit_weight_pcf"])
    # Centroid of stem from toe side (simplified for now, assuming vertical face)
    # This needs to be more accurate for trapezoidal section
    x_stem = wall_base_offset_from_toe + (t_base / 3) * ((2 * t_top + t_base) / (t_top + t_base))

    # Base Slab
    area_base_slab = B_base * D_f
    weight_base_slab = area_base_slab * (slab_material_props["unit_weight_kn_m3"] if params["units"] == "metric" else slab_material_props["unit_weight_pcf"])
    x_base_slab = B_base / 2

    # Soil on Heel
    # Assuming soil extends from back of wall to end of heel
    # Height of soil on heel is h_wall_stem
    area_soil_heel = B_heel * (h_wall_stem + active_side_ground_elevation)
    weight_soil_heel = area_soil_heel * (active_soil["unit_weight_kn_m3"] if params["units"] == "metric" else active_soil["unit_weight_pcf"])
    x_soil_heel = B_base - B_heel / 2

    # Soil on Toe (above base slab)
    # Assuming ground level is at top of foundation for toe side
    area_soil_toe = B_toe * passive_side_ground_elevation
    weight_soil_toe = area_soil_toe * (passive_soil["unit_weight_kn_m3"] if params["units"] == "metric" else passive_soil["unit_weight_pcf"])
    x_soil_toe = B_toe / 2

    # Total Vertical Force and Moment about Toe
    total_vertical_force = weight_stem + weight_base_slab + weight_soil_heel + weight_soil_toe
    resisting_moment_about_toe = (weight_stem * x_stem) + \
                                 (weight_base_slab * x_base_slab) + \
                                 (weight_soil_heel * x_soil_heel) + \
                                 (weight_soil_toe * x_soil_toe)

    # --- Earth Pressure Calculations ---
    # Groundwater depth from ground surface
    groundwater_depth_from_surface = D_f + groundwater_level_below_base

    # Active Pressure
    Pa_at_base = calculate_earth_pressure(active_soil, H_total, groundwater_depth_from_surface, is_active=True, surcharge_load=surcharge_load, active_side_slope_height=geometry["active_side_slope_height"])
    Pa_force = 0.5 * Pa_at_base * H_total # Triangular distribution
    y_Pa = H_total / 3 # Lever arm for active force from base

    # Passive Pressure (at toe side, up to foundation depth)
    # Adjust passive depth if foundation is lower than passive side ground
    passive_depth_for_pressure = D_f + foundation_lower_than_passive_side
    Pp_at_base = calculate_earth_pressure(passive_soil, passive_depth_for_pressure, groundwater_depth_from_surface, is_active=False)
    Pp_force = 0.5 * Pp_at_base * passive_depth_for_pressure # Triangular distribution
    y_Pp = passive_depth_for_pressure / 3 # Lever arm for passive force from base

    # Shear Key Resistance
    shear_key_resistance = 0.0
    if params["shear_key_used"] and params["slab_material"] == "concrete":
        if params["shear_key_position"] == "heel":
            # Shear key at heel is on the active side, so it does not contribute to passive resistance
            shear_key_resistance = 0.0
        else: # "toe" or "under_wall"
            # Depth of soil in front of the shear key
            shear_key_soil_depth_start = D_f
            shear_key_soil_depth_end = D_f + shear_key_depth

            # Passive pressure at the top of the shear key (at depth D_f)
            Pp_at_top_of_key = calculate_earth_pressure(passive_soil, shear_key_soil_depth_start, groundwater_depth_from_surface, is_active=False)
            # Passive pressure at the bottom of the shear key (at depth D_f + shear_key_depth)
            Pp_at_bottom_of_key = calculate_earth_pressure(passive_soil, shear_key_soil_depth_end, groundwater_depth_from_surface, is_active=False)

            # The force is the area of the trapezoid formed by the pressure diagram over the shear key depth
            shear_key_resistance = 0.5 * (Pp_at_top_of_key + Pp_at_bottom_of_key) * shear_key_depth


    # Overturning Moment about Toe
    overturning_moment = Pa_force * y_Pa

    # --- Stability Analysis ---
    # Factor of Safety Against Overturning
    FS_overturning = resisting_moment_about_toe / overturning_moment if overturning_moment > 0 else float('inf')

    # Sliding Force
    sliding_force = Pa_force - Pp_force # Net horizontal force

    # Resisting Force against Sliding (friction + passive resistance + shear key resistance)
    # Assuming friction angle between concrete and soil is 2/3 * phi_active
    friction_angle_base = (2/3) * active_soil["friction_angle_deg"]
    friction_resisting_force = total_vertical_force * math.tan(math.radians(friction_angle_base))
    total_resisting_sliding_force = friction_resisting_force + Pp_force + shear_key_resistance

    # Factor of Safety Against Sliding
    FS_sliding = total_resisting_sliding_force / sliding_force if sliding_force > 0 else float('inf')

    # Bearing Pressure Calculation
    # Location of resultant force from toe (x_bar)
    x_bar = (resisting_moment_about_toe - overturning_moment) / total_vertical_force
    e = x_bar - (B_base / 2) # Eccentricity

    # Check if resultant is within middle third (e <= B_base / 6)
    if abs(e) > B_base / 6:
        # Resultant outside middle third, pressure distribution is triangular
        q_max = (2 * total_vertical_force) / (3 * x_bar) if x_bar > 0 else float('inf')
        q_min = 0.0 # Assuming triangular distribution, min pressure is zero
    else:
        # Resultant within middle third, pressure distribution is trapezoidal
        q_max = (total_vertical_force / B_base) * (1 + (6 * e) / B_base)
        q_min = (total_vertical_force / B_base) * (1 - (6 * e) / B_base)

    # Factor of Safety Against Bearing Capacity
    FS_bearing = (active_soil["allowable_bearing_pressure_kpa"] if params["units"] == "metric" else active_soil["allowable_bearing_pressure_psf"]) / q_max if q_max > 0 else float('inf')

    return {
        "total_vertical_force": total_vertical_force,
        "resisting_moment_about_toe": resisting_moment_about_toe,
        "Pa_at_base": Pa_at_base,
        "Pa_force": Pa_force,
        "y_Pa": y_Pa,
        "Pp_at_base": Pp_at_base,
        "Pp_force": Pp_force,
        "y_Pp": y_Pp,
        "shear_key_resistance": shear_key_resistance,
        "overturning_moment": overturning_moment,
        "FS_overturning": FS_overturning,
        "sliding_force": sliding_force,
        "total_resisting_sliding_force": total_resisting_sliding_force,
        "FS_sliding": FS_sliding,
        "x_bar": x_bar,
        "e": e,
        "q_max": q_max,
        "q_min": q_min,
        "FS_bearing": FS_bearing,
        "weight_stem": weight_stem, # Added for testing
        "weight_base_slab": weight_base_slab, # Added for testing
        "weight_soil_heel": weight_soil_heel, # Added for testing
        "weight_soil_toe": weight_soil_toe, # Added for testing
    }