import math
from earth_pressure import calculate_earth_pressure

def calculate_rebar_area(Mu_knm, b_mm, d_mm, fc_mpa, fy_mpa):
    """Calculates required steel area (As) for a rectangular section based on ACI 318.
    Mu_knm: Factored moment in kN.m
    b_mm: Width of the section in mm
    d_mm: Effective depth in mm
    fc_mpa: Concrete compressive strength in MPa
    fy_mpa: Steel yield strength in MPa
    """
    # Convert Mu to N.mm
    Mu_nmm = Mu_knm * 1e6

    # ACI 318 strength reduction factor for flexure (assuming tension controlled section)
    phi = 0.9

    # Calculate Rn = Mu / (phi * b * d^2)
    Rn = Mu_nmm / (phi * b_mm * d_mm**2)

    # Calculate rho = (0.85 * fc / fy) * (1 - sqrt(1 - (2 * Rn) / (0.85 * fc)))
    # Ensure the term inside sqrt is not negative due to floating point inaccuracies or very high Rn
    sqrt_term = 1 - (2 * Rn) / (0.85 * fc_mpa)
    if sqrt_term < 0:
        sqrt_term = 0 # Handle cases where Rn is too high, indicating concrete crushing

    rho = (0.85 * fc_mpa / fy_mpa) * (1 - math.sqrt(sqrt_term))

    # Calculate As = rho * b * d
    As_mm2 = rho * b_mm * d_mm

    return As_mm2

def calculate_rebar_info(params, geometry, wall_material_props, active_soil, groundwater_level_below_base):
    rebar_info = "N/A (Stone Masonry)"
    if params["wall_material"] == "concrete":
        if params["units"] == "metric":
            fc_val = wall_material_props["f_c_prime_mpa"]
            fy_val = wall_material_props["f_y_mpa"]
            d_unit_factor = 1000 # m to mm
            moment_unit = "kN.m/m"
            area_unit = "mm^2/m"
        else: # imperial
            fc_val = wall_material_props["f_c_prime_psi"]
            fy_val = wall_material_props["f_y_psi"]
            d_unit_factor = 12 # ft to inches
            moment_unit = "kip.ft/ft"
            area_unit = "in^2/ft"

        # Stem Wall Rebar (Main Reinforcement)
        # Assuming cantilever action, max moment at base of stem
        # Pressure at base of stem (excluding foundation depth)
        Pa_at_stem_base = calculate_earth_pressure(active_soil, geometry["h_wall_stem"], groundwater_level_below_base, is_active=True, surcharge_load=geometry["surcharge_load"])
        # Moment at base of stem (triangular pressure distribution)
        Mu_stem = (1.2 * 0.5 * Pa_at_stem_base * geometry["h_wall_stem"]) * (geometry["h_wall_stem"] / 3) # Factored moment (1.2 for earth pressure)

        # Effective depth 'd' for stem (assuming 75mm cover or 3 inches)
        cover = 0.075 if params["units"] == "metric" else (3/12) # 3 inches in feet
        d_stem = (geometry["t_base"] - cover)
        d_stem_calc_unit = d_stem * d_unit_factor # Convert to mm or inches
        b_stem_calc_unit = 1000 if params["units"] == "metric" else 12 # 1 meter width or 1 foot width

        if d_stem_calc_unit > 0:
            As_stem = calculate_rebar_area(Mu_stem, b_stem_calc_unit, d_stem_calc_unit, fc_val, fy_val)
            rebar_info = f"Stem Wall Main Rebar (As): {As_stem:.2f} {area_unit}"
        else:
            rebar_info = "Stem Wall Rebar: Effective depth is zero or negative. Check dimensions."

        # Base Slab Rebar (Heel and Toe)
        # This is a simplified approach and needs more detailed analysis for actual design
        # For now, just calculate a nominal rebar for the base slab
        Mu_base_slab_nominal = 10.0 # kN.m/m (example nominal moment)
        d_base_slab = (geometry["D_f"] - cover)
        d_base_slab_calc_unit = d_base_slab * d_unit_factor
        b_base_slab_calc_unit = 1000 if params["units"] == "metric" else 12

        if d_base_slab_calc_unit > 0:
            As_base_slab = calculate_rebar_area(Mu_base_slab_nominal, b_base_slab_calc_unit, d_base_slab_calc_unit, fc_val, fy_val)
            rebar_info += f"\nBase Slab Nominal Rebar (As): {As_base_slab:.2f} {area_unit}"
        else:
            rebar_info += "\nBase Slab Rebar: Effective depth is zero or negative. Check dimensions."
    return rebar_info