

from parameters import default_params, soil_properties, material_properties
from unit_conversion import convert_units
from geometry import calculate_geometry
from earth_pressure import calculate_earth_pressure
from stability_analysis import perform_stability_analysis
from rebar_calculation import calculate_rebar_area, calculate_rebar_info
from svg_drawing import generate_svg_drawing
import json
import sys

__version__ = "0.1.0" # Added version information

def read_params_from_json(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def get_interactive_params(current_params):
    print("\n--- Enter Parameters (Press Enter for Default) ---")
    for key, default_value in default_params.items():
        if key in ["wall_height_m", "foundation_depth_m", "toe_length_m", "heel_length_m",
                   "wall_top_width_m", "wall_base_width_m", "groundwater_level_m_below_base",
                   "shear_key_depth_m", "shear_key_width_m", "active_side_ground_elevation_m",
                   "passive_side_ground_elevation_m", "point_load_kn", "point_load_distance_from_wall_m",
                   "surcharge_load_kpa", "foundation_lower_than_passive_side_m"]:
            prompt = f"{key} ({default_value:.2f} m/ft): "
            user_input = input(prompt)
            if user_input:
                current_params[key] = float(user_input)
        elif key in ["shear_key_used", "output_html"]:
            prompt = f"{key} ({default_value}) [True/False]: "
            user_input = input(prompt).lower()
            if user_input == 'true':
                current_params[key] = True
            elif user_input == 'false':
                current_params[key] = False
        elif key == "units":
            prompt = f"{key} ({default_value}) [metric/imperial]: "
            user_input = input(prompt).lower()
            if user_input in ['metric', 'imperial']:
                current_params[key] = user_input
        elif key == "wall_material":
            prompt = f"{key} ({default_value}) [concrete/stone_masonry]: "
            user_input = input(prompt).lower()
            if user_input in ['concrete', 'stone_masonry']:
                current_params[key] = user_input
        elif key == "slab_material":
            prompt = f"{key} ({default_value}) [concrete/cement_treated_base/none]: "
            user_input = input(prompt).lower()
            if user_input in ['concrete', 'cement_treated_base', 'none']:
                current_params[key] = user_input
        elif key == "face_wall_position":
            prompt = f"{key} ({default_value}) [toe_side/heel_side]: "
            user_input = input(prompt).lower()
            if user_input in ['toe_side', 'heel_side']:
                current_params[key] = user_input
        elif key in ["active_soil_type", "passive_soil_type"]:
            soil_options = ', '.join(soil_properties.keys())
            prompt = f"{key} ({default_value}) [{soil_options}]: "
            user_input = input(prompt).lower()
            if user_input in soil_properties.keys():
                current_params[key] = user_input
        elif key == "shear_key_position":
            prompt = f"{key} ({default_value}) [toe/heel/under_wall]: "
            user_input = input(prompt).lower()
            if user_input in ['toe', 'heel', 'under_wall']:
                current_params[key] = user_input

    return current_params

def calculate_retaining_wall(user_params=None):
    params = default_params.copy()
    if user_params:
        params.update(user_params)

    # Define units for display
    if params["units"] == "metric":
        params["units_display"] = {
            "length": "m",
            "force": "kN",
            "pressure": "kPa",
            "unit_weight": "kN/m^3",
            "force_per_length": "kN/m",
            "moment_per_length": "kN.m/m",
            "area_per_length": "mm^2/m",
        }
    else:
        params["units_display"] = {
            "length": "ft",
            "force": "lb",
            "pressure": "psf",
            "unit_weight": "pcf",
            "force_per_length": "lb/ft",
            "moment_per_length": "lb.ft/ft",
            "area_per_length": "in^2/ft",
        }

    # Convert units if imperial
    params, soil_properties_converted, material_properties_converted = convert_units(params, soil_properties.copy(), material_properties.copy())

    # Get soil properties (using converted if imperial)
    active_soil = soil_properties_converted[params["active_soil_type"]]
    passive_soil = soil_properties_converted[params["passive_soil_type"]]

    # Get material properties (using converted if imperial)
    wall_material_props = material_properties_converted[params["wall_material"]]
    # Handle 'none' case for slab material
    if params["slab_material"] == "none":
        slab_material_props = {"unit_weight_kn_m3": 0.0, "unit_weight_pcf": 0.0}
    else:
        slab_material_props = material_properties_converted[params["slab_material"]]

    # Calculate geometry
    geometry = calculate_geometry(params)

    # Perform stability analysis
    stability_results = perform_stability_analysis(params, geometry, active_soil, passive_soil, wall_material_props, slab_material_props)

    # Shear Key Automation
    if stability_results["FS_sliding"] < 1.5 and params["slab_material"] == "concrete":
        params["shear_key_used"] = True
        # Re-run stability analysis with shear key if it was not used initially and FS is low
        stability_results = perform_stability_analysis(params, geometry, active_soil, passive_soil, wall_material_props, slab_material_props)

    # Rebar Calculation (ACI-318)
    rebar_info = calculate_rebar_info(params, geometry, wall_material_props, active_soil, geometry["groundwater_level_below_base"])

    # Generate SVG Drawing
    svg_drawing = generate_svg_drawing(params, geometry, stability_results)

    # --- Summarize Results ---
    summary_text = f"""
Retaining Wall Calculation Summary:

Geometry:
  Total Height (H_total): {geometry["H_total"]:.2f} {params["units_display"]["length"]}
  Stem Wall Height (h_wall_stem): {geometry["h_wall_stem"]:.2f} {params["units_display"]["length"]}
  Base Slab Width (B_base): {geometry["B_base"]:.2f} {params["units_display"]["length"]}

Stability Analysis:
  Factor of Safety (Overturning): {stability_results["FS_overturning"]:.2f}
  Factor of Safety (Sliding): {stability_results["FS_sliding"]:.2f}
  Maximum Bearing Pressure (q_max): {stability_results["q_max"]:.2f} {params["units_display"]["pressure"]}
  Factor of Safety (Bearing Capacity): {stability_results["FS_bearing"]:.2f}

Rebar Information: {rebar_info}
"""

    # LaTeX formulas as raw strings
    ka_formula = r"$K_a = \tan^2(45^\circ - \phi/2)$"
    kp_formula = r"$K_p = \tan^2(45^\circ + \phi/2)$"
    pressure_formula = r"$P = \gamma \cdot h \cdot K + q \cdot K$"
    w_stem_formula = r"$W_{{stem}} = A_{{stem}} \cdot \gamma_{{wall}}$"
    w_base_formula = r"$W_{{base}} = B_{{base}} \cdot D_f \cdot \gamma_{{slab}}$"
    w_soil_heel_formula = r"$W_{{soil,heel}} = B_{{heel}} \cdot H_{{soil,heel}} \cdot \gamma_{{soil,active}}$"
    w_soil_toe_formula = r"$W_{{soil,toe}} = B_{{toe}} \cdot H_{{soil,toe}} \cdot \gamma_{{soil,passive}}$"
    mr_formula = r"$M_R = \sum (W_i \cdot x_i)$"
    pa_force_formula = r"$P_a = 0.5 \cdot P_{{a,base}} \cdot H_{{total}}$"
    pp_force_formula = r"$P_p = 0.5 \cdot P_{{p,base}} \cdot D_f$"
    mo_formula = r"$M_O = P_a \cdot y_a$"
    shear_key_resistance_formula = r"Calculated as passive resistance over the shear key depth."
    fso_formula = r"$FS_O = M_R / M_O$"
    fss_formula = r"$FS_S = (W_{{total}} \cdot \tan(\delta) + P_p + R_{{shear\\_key}}) / P_a$"
    bearing_pressure_formula = r"$q_{{max/min}} = (V/B) \cdot (1 \pm 6e/B)$"
    fsb_formula = r"$FS_B = q_{{allowable}} / q_{{max}}$"
    rn_formula = r"$R_n = M_u / (\phi \cdot b \cdot d^2)$"
    rho_formula = r"$\rho = (0.85 f'_c / f_y) \cdot (1 - \sqrt{1 - (2 R_n) / (0.85 f'_c)})$"
    as_formula = r"$A_s = \rho \cdot b \cdot d$"

    detailed_report_md = f"""
# Retaining Wall Calculation Report

## Input Parameters
```json
{json.dumps(params, indent=2)}
```

## Soil Properties
Active Soil: {params["active_soil_type"]}
  Unit Weight: {active_soil["unit_weight_kn_m3"] if params["units"] == "metric" else active_soil["unit_weight_pcf"] } {params["units_display"]["unit_weight"]}
  Friction Angle: {active_soil["friction_angle_deg"]} degrees
  Cohesion: {active_soil["cohesion_kpa"] if params["units"] == "metric" else active_soil["cohesion_kpa"] * 20.885 } {params["units_display"]["pressure"]}
  Allowable Bearing Pressure: {active_soil["allowable_bearing_pressure_kpa"] if params["units"] == "metric" else active_soil["allowable_bearing_pressure_psf"] } {params["units_display"]["pressure"]}

Passive Soil: {params["passive_soil_type"]}
  Unit Weight: {passive_soil["unit_weight_kn_m3"] if params["units"] == "metric" else passive_soil["unit_weight_pcf"] } {params["units_display"]["unit_weight"]}
  Friction Angle: {passive_soil["friction_angle_deg"]} degrees
  Cohesion: {passive_soil["cohesion_kpa"] if params["units"] == "metric" else passive_soil["cohesion_kpa"] * 20.885 } {params["units_display"]["pressure"]}

## Geometry
- Total Height (H_total): {geometry["H_total"]:.2f} {params["units_display"]["length"]}
- Stem Wall Height (h_wall_stem): {geometry["h_wall_stem"]:.2f} {params["units_display"]["length"]}
- Foundation Depth (D_f): {geometry["D_f"]:.2f} {params["units_display"]["length"]}
- Toe Length (B_toe): {geometry["B_toe"]:.2f} {params["units_display"]["length"]}
- Heel Length (B_heel): {geometry["B_heel"]:.2f} {params["units_display"]["length"]}
- Wall Top Width (t_top): {geometry["t_top"]:.2f} {params["units_display"]["length"]}
- Wall Base Width (t_base): {geometry["t_base"]:.2f} {params["units_display"]["length"]}
- Base Slab Width (B_base): {geometry["B_base"]:.2f} {params["units_display"]["length"]}

## Component Weights and Moments
- Stem Wall Weight: {stability_results["weight_stem"]:.2f} {params["units_display"]["force_per_length"]}
- Base Slab Weight: {stability_results["weight_base_slab"]:.2f} {params["units_display"]["force_per_length"]}
- Soil on Heel Weight: {stability_results["weight_soil_heel"]:.2f} {params["units_display"]["force_per_length"]}
- Soil on Toe Weight: {stability_results["weight_soil_toe"]:.2f} {params["units_display"]["force_per_length"]}
- Total Vertical Force: {stability_results["total_vertical_force"]:.2f} {params["units_display"]["force_per_length"]}
- Resisting Moment about Toe: {stability_results["resisting_moment_about_toe"]:.2f} {params["units_display"]["moment_per_length"]}

## Earth Pressure
- Active Pressure at Base: {stability_results["Pa_at_base"]:.2f} {params["units_display"]["pressure"]}
- Active Force (Pa): {stability_results["Pa_force"]:.2f} {params["units_display"]["force_per_length"]} (acting at {stability_results["y_Pa"]:.2f} {params["units_display"]["length"]} from base)
- Passive Pressure at Base: {stability_results["Pp_at_base"]:.2f} {params["units_display"]["pressure"]}
- Passive Force (Pp): {stability_results["Pp_force"]:.2f} {params["units_display"]["force_per_length"]} (acting at {stability_results["y_Pp"]:.2f} {params["units_display"]["length"]} from base)
- Overturning Moment about Toe: {stability_results["overturning_moment"]:.2f} {params["units_display"]["moment_per_length"]}
- Shear Key Resistance: {stability_results["shear_key_resistance"]:.2f} {params["units_display"]["force_per_length"]}

## Stability Analysis
- Factor of Safety (Overturning): {stability_results["FS_overturning"]:.2f}
- Net Sliding Force: {stability_results["sliding_force"]:.2f} {params["units_display"]["force_per_length"]}
- Total Resisting Sliding Force: {stability_results["total_resisting_sliding_force"]:.2f} {params["units_display"]["force_per_length"]}
- Factor of Safety (Sliding): {stability_results["FS_sliding"]:.2f}
- Eccentricity (e): {stability_results["e"]:.2f} {params["units_display"]["length"]}
- Maximum Bearing Pressure (q_max): {stability_results["q_max"]:.2f} {params["units_display"]["pressure"]}
- Minimum Bearing Pressure (q_min): {stability_results["q_min"]:.2f} {params["units_display"]["pressure"]}
- Factor of Safety (Bearing Capacity): {stability_results["FS_bearing"]:.2f}

## Rebar Information
{rebar_info}

## Detailed Formulas and Steps

### 1. Earth Pressure Coefficients
- Active Earth Pressure Coefficient (Rankine): {ka_formula}
- Passive Earth Pressure Coefficient (Rankine): {kp_formula}

### 2. Earth Pressure at Depth
- Pressure ($P$) at depth ($h$): {pressure_formula}
  - Where $\gamma$ is unit weight of soil, $q$ is surcharge load, $K$ is earth pressure coefficient.
- For groundwater, submerged unit weight is used below groundwater table, and hydrostatic pressure is added.

### 3. Component Weights and Moments
- Stem Wall Weight: {w_stem_formula}
- Base Slab Weight: {w_base_formula}
- Soil on Heel Weight: {w_soil_heel_formula}
- Soil on Toe Weight: {w_soil_toe_formula}
- Resisting Moment about Toe: {mr_formula}

### 4. Earth Forces
- Active Force ($P_a$): {pa_force_formula}
- Passive Force ($P_p$): {pp_force_formula}
- Overturning Moment ($M_O$): {mo_formula}
- Shear Key Resistance: {shear_key_resistance_formula}

### 5. Stability Analysis
- Factor of Safety against Overturning ($FS_O$): {fso_formula}
- Factor of Safety against Sliding ($FS_S$): {fss_formula}
  - Where $\delta$ is friction angle between base and soil (typically 2/3 $\phi_{{active}}$).
- Bearing Pressure: {bearing_pressure_formula}
  - Where $V$ is total vertical force, $B$ is base width, $e$ is eccentricity.
- Factor of Safety against Bearing Capacity ($FS_B$): {fsb_formula}

### 6. Rebar Calculation (ACI 318)
- Required Steel Area ($A_s$): Calculated based on factored moment ($M_u$), concrete strength ($f'_c$), and steel yield strength ($f_y$).
  - $R_n = M_u / (\phi \cdot b \cdot d^2)$
  - $\rho = (0.85 f'_c / f_y) \cdot (1 - \sqrt{1 - (2 R_n) / (0.85 f'_c)})$
  - $A_s = \rho \cdot b \cdot d$
"""

    results = {
        "summary": summary_text,
        "detailed_report_md": detailed_report_md,
        "svg_drawing": svg_drawing,
        "FS_overturning": stability_results["FS_overturning"],
        "FS_sliding": stability_results["FS_sliding"],
        "FS_bearing": stability_results["FS_bearing"],
        "q_max": stability_results["q_max"],
        "params": params, # Include params in results for easy access in main block
    }

    return results

# --- Main Execution Block ---
if __name__ == "__main__":
    print(f"Retaining Wall Calculation Program (Version {__version__})")
    print("Usage: python3 retaining_wall_calculator.py [json_input_file]")
    print("       If no file is provided, interactive input will be used.")

    input_params = {}
    if len(sys.argv) > 1:
        json_filepath = sys.argv[1]
        try:
            input_params = read_params_from_json(json_filepath)
            print(f"Reading parameters from {json_filepath}")
        except FileNotFoundError:
            print(f"Error: JSON file not found at {json_filepath}. Using default parameters.")
            input_params = default_params.copy()
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON format in {json_filepath}. Using default parameters.")
            input_params = default_params.copy()
    else:
        input_params = get_interactive_params(default_params.copy())

    print("\n--- Input Parameters Used ---")
    print(json.dumps(input_params, indent=2))

    calculation_results = calculate_retaining_wall(input_params)

    print("\n--- Summary ---")
    print(calculation_results["summary"])

    # Save markdown report
    with open("retaining_wall_report.md", "w") as f:
        f.write(calculation_results["detailed_report_md"])
    print("\nDetailed report saved to retaining_wall_report.md")

    # Save SVG drawing
    with open("retaining_wall_drawing.svg", "w") as f:
        f.write(calculation_results["svg_drawing"])
    print("Drawing saved to retaining_wall_drawing.svg")

    # Optional HTML output
    if calculation_results["params"]["output_html"]:
        # Replace markdown code blocks with pre/code tags and embed SVG
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
<title>Retaining Wall Calculation Report</title>
<style>
  body {{ font-family: sans-serif; margin: 20px; }}
  pre {{ background-color: #eee; padding: 10px; border-radius: 5px; overflow-x: auto; }}
  h1, h2, h3 {{ color: #333; }}
  details {{ margin-bottom: 10px; border: 1px solid #ccc; border-radius: 5px; padding: 10px; }}
  summary {{ font-weight: bold; cursor: pointer; }}
</style>
</head>
<body>
<h1>Retaining Wall Calculation Report</h1>

<details>
  <summary>Input Parameters</summary>
  <pre><code>{json.dumps(calculation_results["params"], indent=2)}</code></pre>
</details>

{calculation_results["detailed_report_md"].replace("```json", "<pre><code>").replace("```", "</code></pre>")}

<h2>Dimensional Drawing</h2>
{calculation_results["svg_drawing"]}

</body>
</html>
"""
        with open("retaining_wall_report.html", "w") as f:
            f.write(html_content)
        print("HTML report saved to retaining_wall_report.html")

    print("\nCalculation complete.")
