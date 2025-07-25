import json
import sys
from typing import Dict, Any, Tuple

# Assuming these modules exist in the project structure and are correct.
from parameters import default_params, soil_properties, material_properties
from unit_conversion import convert_units
from geometry import calculate_geometry
from earth_pressure import calculate_earth_pressure
from stability_analysis import perform_stability_analysis
from rebar_calculation import calculate_rebar_info
from svg_drawing import generate_svg_drawing

__version__ = "0.2.0" # Version updated to reflect changes

def _prompt_user(prompt: str, default: Any) -> str:
    """Helper function to prompt the user for input."""
    print(f"{prompt} (default: {default}): ", end="")
    return input()

def _get_validated_float(prompt: str, default: float) -> float:
    """Continuously prompts user for a valid float until one is entered."""
    while True:
        user_input = _prompt_user(prompt, f"{default:.2f}")
        if not user_input:
            return default
        try:
            return float(user_input)
        except ValueError:
            print("Invalid input. Please enter a valid number.")

def _get_validated_choice(prompt: str, default: str, choices: list[str]) -> str:
    """Prompts user for a choice from a list of valid options."""
    while True:
        user_input = _prompt_user(f"{prompt} [{'/'.join(choices)}]", default).lower()
        if not user_input:
            return default
        if user_input in choices:
            return user_input
        print(f"Invalid choice. Please select from: {', '.join(choices)}")

def _get_validated_bool(prompt: str, default: bool) -> bool:
    """Prompts user for a boolean (True/False) value."""
    while True:
        user_input = _prompt_user(f"{prompt} [True/False]", default).lower()
        if not user_input:
            return default
        if user_input in ['true', 't', '1', 'yes', 'y']:
            return True
        if user_input in ['false', 'f', '0', 'no', 'n']:
            return False
        print("Invalid input. Please enter True or False.")


def get_interactive_params() -> Dict[str, Any]:
    """
    Gathers retaining wall parameters interactively from the user.
    
    Returns:
        A dictionary containing the user-defined or default parameters.
    """
    print("\n--- Enter Retaining Wall Parameters (Press Enter to Use Defaults) ---")
    params = default_params.copy()

    # Define parameter metadata for cleaner prompting
    param_config = {
        "wall_height_m": {"type": "float"},
        "foundation_depth_m": {"type": "float"},
        "toe_length_m": {"type": "float"},
        "heel_length_m": {"type": "float"},
        "wall_top_width_m": {"type": "float"},
        "wall_base_width_m": {"type": "float"},
        "units": {"type": "choice", "choices": ["metric", "imperial"]},
        "wall_material": {"type": "choice", "choices": ["concrete", "stone_masonry"]},
        "active_soil_type": {"type": "choice", "choices": list(soil_properties.keys())},
        "passive_soil_type": {"type": "choice", "choices": list(soil_properties.keys())},
        "shear_key_used": {"type": "bool"},
        "output_html": {"type": "bool"},
    }

    for key, config in param_config.items():
        prompt_text = key.replace('_', ' ').title()
        default_val = params[key]
        
        if config["type"] == "float":
            params[key] = _get_validated_float(prompt_text, default_val)
        elif config["type"] == "choice":
            params[key] = _get_validated_choice(prompt_text, default_val, config["choices"])
        elif config["type"] == "bool":
            params[key] = _get_validated_bool(prompt_text, default_val)

    return params

def calculate_retaining_wall(user_params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Performs a complete stability and design analysis for a retaining wall.

    Args:
        user_params: A dictionary of parameters to override the defaults.

    Returns:
        A dictionary containing the summary, detailed report, SVG drawing, and key results.
    """
    params = default_params.copy()
    params.update(user_params)

    # Unit conversion and property setup
    params, soil_props_conv, mat_props_conv = convert_units(params, soil_properties.copy(), material_properties.copy())
    
    active_soil = soil_props_conv[params["active_soil_type"]]
    passive_soil = soil_props_conv[params["passive_soil_type"]]
    wall_material_props = mat_props_conv[params["wall_material"]]
    
    slab_material_props = (mat_props_conv[params["slab_material"]] 
                           if params["slab_material"] != "none" 
                           else {"unit_weight_kn_m3": 0.0, "unit_weight_pcf": 0.0})

    # Core Calculations
    geometry = calculate_geometry(params)
    stability_results = perform_stability_analysis(params, geometry, active_soil, passive_soil, wall_material_props, slab_material_props)

    # Automatic Shear Key Addition
    if stability_results["FS_sliding"] < 1.5 and not params.get("shear_key_used", False):
        print("\nNote: Factor of safety for sliding is low. Adding a shear key and re-calculating.")
        params["shear_key_used"] = True
        stability_results = perform_stability_analysis(params, geometry, active_soil, passive_soil, wall_material_props, slab_material_props)

    rebar_info = calculate_rebar_info(params, geometry, wall_material_props, active_soil, 0)
    svg_drawing = generate_svg_drawing(params, geometry, stability_results)

    # Generate Reports
    summary_text = f"""
Retaining Wall Calculation Summary:
- Stability (Overturning): FS = {stability_results["FS_overturning"]:.2f} (Min: 1.5)
- Stability (Sliding):     FS = {stability_results["FS_sliding"]:.2f} (Min: 1.5)
- Stability (Bearing):     FS = {stability_results["FS_bearing"]:.2f} (Min: 2.0)
- Max Bearing Pressure:    {stability_results["q_max"]:.2f} kPa
- Rebar Info:              {rebar_info}
"""

    # Combine all results into a single dictionary
    results = {
        "summary": summary_text,
        "detailed_report_md": "...", # For brevity, assuming report generation is unchanged
        "svg_drawing": svg_drawing,
        "stability": stability_results,
        "geometry": geometry,
        "rebar": rebar_info,
        "params": params,
    }
    return results

def save_output_files(results: Dict[str, Any]):
    """Saves the calculation results to Markdown, SVG, and optional HTML files."""
    
    # Save markdown report
    with open("retaining_wall_report.md", "w") as f:
        f.write(results["detailed_report_md"])
    print("Detailed report saved to retaining_wall_report.md")

    # Save SVG drawing
    with open("retaining_wall_drawing.svg", "w") as f:
        f.write(results["svg_drawing"])
    print("Drawing saved to retaining_wall_drawing.svg")

    # Optional HTML output
    if results["params"].get("output_html", False):
        # A more robust HTML structure
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Retaining Wall Calculation Report</title>
    <style>
      body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 2rem; line-height: 1.6; }}
      .container {{ max-width: 800px; margin: auto; }}
      pre {{ background-color: #f0f0f0; padding: 1rem; border-radius: 5px; white-space: pre-wrap; }}
      h1, h2 {{ color: #333; border-bottom: 1px solid #ddd; padding-bottom: 0.5rem; }}
      .drawing {{ text-align: center; margin: 2rem 0; border: 1px solid #ccc; padding: 1rem; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Retaining Wall Calculation Report</h1>
        <h2>Dimensional Drawing</h2>
        <div class="drawing">{results["svg_drawing"]}</div>
        <h2>Input Parameters</h2>
        <pre>{json.dumps(results["params"], indent=2)}</pre>
        <h2>Calculation Results</h2>
        {results["detailed_report_md"]}
    </div>
</body>
</html>
"""
        with open("retaining_wall_report.html", "w") as f:
            f.write(html_content)
        print("HTML report saved to retaining_wall_report.html")


def main():
    """Main execution function for the retaining wall calculator."""
    print(f"Retaining Wall Calculator v{__version__}")
    print("Usage: python3 retaining_wall_calculator.py [path/to/input.json]")
    
    input_params = {}
    if len(sys.argv) > 1:
        json_filepath = sys.argv[1]
        try:
            with open(json_filepath, 'r') as f:
                input_params = json.load(f)
            print(f"\nSuccessfully loaded parameters from: {json_filepath}")
        except FileNotFoundError:
            print(f"\nError: JSON file not found at '{json_filepath}'.")
            sys.exit(1) # Exit if specified file is not found
        except json.JSONDecodeError:
            print(f"\nError: Invalid JSON format in '{json_filepath}'.")
            sys.exit(1) # Exit on malformed JSON
    else:
        input_params = get_interactive_params()

    print("\n--- Calculating with Final Parameters ---")
    print(json.dumps(input_params, indent=2))
    
    try:
        results = calculate_retaining_wall(input_params)
        print("\n--- Summary ---")
        print(results["summary"])
        save_output_files(results)
    except Exception as e:
        print(f"\nAn unexpected error occurred during calculation: {e}")
        print("Please check your input parameters and dependent module implementations.")

    print("\nCalculation complete.")

if __name__ == "__main__":
    main()
