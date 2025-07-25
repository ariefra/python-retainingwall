
# --- Unit Conversion Function ---
def convert_units(params, soil_properties, material_properties):
    if params["units"] == "imperial":
        # Conversion factors
        m_to_ft = 3.28084
        kn_m3_to_pcf = 6.366 # 1 kN/m^3 = 6.366 pcf (approx)
        kpa_to_psf = 20.885 # 1 kPa = 20.885 psf (approx)
        mpa_to_psi = 145.038 # 1 MPa = 145.038 psi (approx)
        kn_to_lb = 224.809 # 1 kN = 224.809 lb (approx)

        # Convert linear dimensions from meters to feet
        params["wall_height_ft"] = params["wall_height_m"] * m_to_ft
        params["foundation_depth_ft"] = params["foundation_depth_m"] * m_to_ft
        params["toe_length_ft"] = params["toe_length_m"] * m_to_ft
        params["heel_length_ft"] = params["heel_length_m"] * m_to_ft
        params["wall_top_width_ft"] = params["wall_top_width_m"] * m_to_ft
        params["wall_base_width_ft"] = params["wall_base_width_m"] * m_to_ft
        params["groundwater_level_ft_below_base"] = params["groundwater_level_m_below_base"] * m_to_ft
        params["shear_key_depth_ft"] = params["shear_key_depth_m"] * m_to_ft
        params["shear_key_width_ft"] = params["shear_key_width_m"] * m_to_ft
        params["active_side_ground_elevation_ft"] = params["active_side_ground_elevation_m"] * m_to_ft
        params["passive_side_ground_elevation_ft"] = params["passive_side_ground_elevation_m"] * m_to_ft
        params["point_load_lb"] = params["point_load_kn"] * kn_to_lb
        params["point_load_distance_from_wall_ft"] = params["point_load_distance_from_wall_m"] * m_to_ft
        params["surcharge_load_psf"] = params["surcharge_load_kpa"] * kpa_to_psf
        params["foundation_lower_than_passive_side_ft"] = params["foundation_lower_than_passive_side_m"] * m_to_ft

        # Convert soil properties
        for soil_type in soil_properties:
            soil_properties[soil_type]["unit_weight_pcf"] = soil_properties[soil_type]["unit_weight_kn_m3"] * kn_m3_to_pcf
            soil_properties[soil_type]["allowable_bearing_pressure_psf"] = soil_properties[soil_type]["allowable_bearing_pressure_kpa"] * kpa_to_psf

        # Convert material properties
        for material_type in material_properties:
            if "unit_weight_kn_m3" in material_properties[material_type]:
                material_properties[material_type]["unit_weight_pcf"] = material_properties[material_type]["unit_weight_kn_m3"] * kn_m3_to_pcf
            if "f_c_prime_mpa" in material_properties[material_type]:
                material_properties[material_type]["f_c_prime_psi"] = material_properties[material_type]["f_c_prime_mpa"] * mpa_to_psi
            if "f_y_mpa" in material_properties[material_type]:
                material_properties[material_type]["f_y_psi"] = material_properties[material_type]["f_y_mpa"] * mpa_to_psi

    return params, soil_properties, material_properties
