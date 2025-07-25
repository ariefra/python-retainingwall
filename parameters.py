# --- Input Parameters with Default Values ---
default_params = {
    "units": "metric",  # "metric" or "imperial"
    "wall_height_m": 5.0,  # Height of the wall from foundation base to top of wall
    "foundation_depth_m": 1.0, # Depth of foundation below ground level
    "toe_length_m": 1.5, # Length of the toe from face of wall
    "heel_length_m": 2.5, # Length of the heel from face of wall
    "wall_top_width_m": 0.3, # Width of the wall at the top
    "wall_base_width_m": 0.6, # Width of the wall at the base
    "wall_material": "concrete", # "concrete" or "stone_masonry"
    "slab_material": "concrete", # "concrete", "cement_treated_base", or "none"
    "face_wall_position": "toe_side", # "toe_side" or "heel_side"
    "active_soil_type": "ordinary_soil",
    "passive_soil_type": "ordinary_soil",
    "groundwater_level_m_below_base": 1.0, # Depth of groundwater below foundation base
    "shear_key_used": False,
    "shear_key_position": "under_wall", # "toe", "heel", "under_wall"
    "shear_key_depth_m": 0.5,
    "shear_key_width_m": 0.5,
    "output_html": False, # New parameter for HTML output
    "active_side_ground_elevation_m": 5.0, # New parameter: active side ground elevation relative to top of foundation
    "passive_side_ground_elevation_m": 0.0, # New parameter: passive side ground elevation relative to top of foundation
    "point_load_kn": 0.0, # New parameter: point load on active side
    "point_load_distance_from_wall_m": 1.0, # New parameter: distance of point load from wall face
    "surcharge_load_kpa": 0.0, # New parameter: surcharge load on active side
    "foundation_lower_than_passive_side_m": 0.0, # New parameter: foundation depth below passive side ground
}

# --- Soil Properties ---
soil_properties = {
    "ordinary_soil": {
        "unit_weight_kn_m3": 18.0,  # kN/m^3
        "friction_angle_deg": 30.0, # degrees
        "cohesion_kpa": 0.0,        # kPa
        "allowable_bearing_pressure_kpa": 150.0, # kPa
    },
    "loose_backfill_soil": {
        "unit_weight_kn_m3": 16.0,
        "friction_angle_deg": 25.0,
        "cohesion_kpa": 0.0,
        "allowable_bearing_pressure_kpa": 100.0,
    },
    "compacted_to_cbr_6_percent_soil": {
        "unit_weight_kn_m3": 19.0,
        "friction_angle_deg": 32.0,
        "cohesion_kpa": 5.0,
        "allowable_bearing_pressure_kpa": 200.0,
    },
    "boulder_compacted_to_cbr_40_percent": {
        "unit_weight_kn_m3": 21.0,
        "friction_angle_deg": 38.0,
        "cohesion_kpa": 10.0,
        "allowable_bearing_pressure_kpa": 300.0,
    },
}

# --- Material Properties ---
material_properties = {
    "concrete": {
        "unit_weight_kn_m3": 24.0, # kN/m^3
        "f_c_prime_mpa": 28.0,     # Concrete compressive strength in MPa
        "f_y_mpa": 420.0,          # Steel yield strength in MPa
    },
    "stone_masonry": {
        "unit_weight_kn_m3": 22.0,
    },
    "cement_treated_base": {
        "unit_weight_kn_m3": 20.0,
    },
}