
# --- Geometry Calculation Function ---
def calculate_geometry(params):
    if params["units"] == "metric":
        wall_height = params["wall_height_m"]
        foundation_depth = params["foundation_depth_m"]
        toe_length = params["toe_length_m"]
        heel_length = params["heel_length_m"]
        t_top = params["wall_top_width_m"]
        t_base = params["wall_base_width_m"]
        groundwater_level_below_base = params["groundwater_level_m_below_base"]
        shear_key_depth = params["shear_key_depth_m"]
        shear_key_width = params["shear_key_width_m"]
        active_side_ground_elevation = params["active_side_ground_elevation_m"]
        passive_side_ground_elevation = params["passive_side_ground_elevation_m"]
        point_load = params["point_load_kn"]
        point_load_distance_from_wall = params["point_load_distance_from_wall_m"]
        surcharge_load = params["surcharge_load_kpa"]
        foundation_lower_than_passive_side = params["foundation_lower_than_passive_side_m"]
    else: # imperial
        wall_height = params["wall_height_ft"]
        foundation_depth = params["foundation_depth_ft"]
        toe_length = params["toe_length_ft"]
        heel_length = params["heel_length_ft"]
        t_top = params["wall_top_width_ft"]
        t_base = params["wall_base_width_ft"]
        groundwater_level_below_base = params["groundwater_level_ft_below_base"]
        shear_key_depth = params["shear_key_depth_ft"]
        shear_key_width = params["shear_key_width_ft"]
        active_side_ground_elevation = params["active_side_ground_elevation_ft"]
        passive_side_ground_elevation = params["passive_side_ground_elevation_ft"]
        point_load = params["point_load_lb"]
        point_load_distance_from_wall = params["point_load_distance_from_wall_ft"]
        surcharge_load = params["surcharge_load_psf"]
        foundation_lower_than_passive_side = params["foundation_lower_than_passive_side_ft"]

    # Total height from base of foundation to top of wall
    h_wall_stem = wall_height
    H_total = h_wall_stem + foundation_depth

    # Calculate base width based on face_wall_position
    if params["face_wall_position"] == "toe_side":
        B_base = toe_length + t_base + heel_length
        wall_base_offset_from_toe = toe_length
    else: # heel_side
        B_base = toe_length + t_base + heel_length
        wall_base_offset_from_toe = B_base - heel_length - t_base

    # Ground slope on active side if wall height is less than active side ground elevation
    active_side_slope_height = 0.0
    if wall_height < active_side_ground_elevation:
        active_side_slope_height = active_side_ground_elevation - wall_height

    return {
        "H_total": H_total,
        "h_wall_stem": h_wall_stem,
        "D_f": foundation_depth,
        "B_toe": toe_length,
        "B_heel": heel_length,
        "t_top": t_top,
        "t_base": t_base,
        "groundwater_level_below_base": groundwater_level_below_base,
        "shear_key_depth": shear_key_depth,
        "shear_key_width": shear_key_width,
        "B_base": B_base,
        "wall_base_offset_from_toe": wall_base_offset_from_toe,
        "active_side_ground_elevation": active_side_ground_elevation,
        "passive_side_ground_elevation": passive_side_ground_elevation,
        "active_side_slope_height": active_side_slope_height,
        "point_load": point_load,
        "point_load_distance_from_wall": point_load_distance_from_wall,
        "surcharge_load": surcharge_load,
        "foundation_lower_than_passive_side": foundation_lower_than_passive_side,
    }
