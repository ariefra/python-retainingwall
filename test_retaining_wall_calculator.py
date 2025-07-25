import unittest
import re
import json
from parameters import default_params, soil_properties, material_properties
from unit_conversion import convert_units
from geometry import calculate_geometry
from earth_pressure import calculate_earth_pressure
from stability_analysis import perform_stability_analysis
from rebar_calculation import calculate_rebar_area, calculate_rebar_info
from svg_drawing import generate_svg_drawing

# Re-implement the main calculation function for testing purposes
def calculate_retaining_wall_for_test(user_params=None):
    params = default_params.copy()
    if user_params:
        params.update(user_params)

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

    # Rebar Calculation (ACI-318)
    rebar_info = calculate_rebar_info(params, geometry, wall_material_props, active_soil, geometry["groundwater_level_below_base"])

    # Generate SVG Drawing
    svg_drawing = generate_svg_drawing(params, geometry)

    # --- Summarize Results ---
    summary_text = f"""
Retaining Wall Calculation Summary:

Geometry:
  Total Height (H_total): {geometry["H_total"]:.2f} {'m' if params["units"] == "metric" else 'ft'}
  Stem Wall Height (h_wall_stem): {geometry["h_wall_stem"]:.2f} {'m' if params["units"] == "metric" else 'ft'}
  Base Slab Width (B_base): {geometry["B_base"]:.2f} {'m' if params["units"] == "metric" else 'ft'}

Stability Analysis:
  Factor of Safety (Overturning): {stability_results["FS_overturning"]:.2f}
  Factor of Safety (Sliding): {stability_results["FS_sliding"]:.2f}
  Maximum Bearing Pressure (q_max): {stability_results["q_max"]:.2f} {'kPa' if params["units"] == "metric" else 'psf'}
  Factor of Safety (Bearing Capacity): {stability_results["FS_bearing"]:.2f}

Rebar Information: {rebar_info}
"""

    detailed_report_md = f"""
# Retaining Wall Calculation Report

## Input Parameters
```json
{json.dumps(params, indent=2)}
```

## Soil Properties
Active Soil: {params["active_soil_type"]}
  Unit Weight: {active_soil["unit_weight_kn_m3"] if params["units"] == "metric" else active_soil["unit_weight_pcf"] } {'kN/m^3' if params["units"] == "metric" else 'pcf'}
  Friction Angle: {active_soil["friction_angle_deg"]} degrees
  Cohesion: {active_soil["cohesion_kpa"] if params["units"] == "metric" else active_soil["cohesion_kpa"] * 20.885 } {'kPa' if params["units"] == "metric" else 'psf'}
  Allowable Bearing Pressure: {active_soil["allowable_bearing_pressure_kpa"] if params["units"] == "metric" else active_soil["allowable_bearing_pressure_psf"] } {'kPa' if params["units"] == "metric" else 'psf'}

Passive Soil: {params["passive_soil_type"]}
  Unit Weight: {passive_soil["unit_weight_kn_m3"] if params["units"] == "metric" else passive_soil["unit_weight_pcf"] } {'kN/m^3' if params["units"] == "metric" else 'pcf'}
  Friction Angle: {passive_soil["friction_angle_deg"]} degrees
  Cohesion: {passive_soil["cohesion_kpa"] if params["units"] == "metric" else passive_soil["cohesion_kpa"] * 20.885 } {'kPa' if params["units"] == "metric" else 'psf'}

## Geometry
- Total Height (H_total): {geometry["H_total"]:.2f} {'m' if params["units"] == "metric" else 'ft'}
- Stem Wall Height (h_wall_stem): {geometry["h_wall_stem"]:.2f} {'m' if params["units"] == "metric" else 'ft'}
- Foundation Depth (D_f): {geometry["D_f"]:.2f} {'m' if params["units"] == "metric" else 'ft'}
- Toe Length (B_toe): {geometry["B_toe"]:.2f} {'m' if params["units"] == "metric" else 'ft'}
- Heel Length (B_heel): {geometry["B_heel"]:.2f} {'m' if params["units"] == "metric" else 'ft'}
- Wall Top Width (t_top): {geometry["t_top"]:.2f} {'m' if params["units"] == "metric" else 'ft'}
- Wall Base Width (t_base): {geometry["t_base"]:.2f} {'m' if params["units"] == "metric" else 'ft'}
- Base Slab Width (B_base): {geometry["B_base"]:.2f} {'m' if params["units"] == "metric" else 'ft'}

## Component Weights and Moments
- Stem Wall Weight: {stability_results["weight_stem"]:.2f} {'kN/m' if params["units"] == "metric" else 'lb/ft'}
- Base Slab Weight: {stability_results["weight_base_slab"]:.2f} {'kN/m' if params["units"] == "metric" else 'lb/ft'}
- Soil on Heel Weight: {stability_results["weight_soil_heel"]:.2f} {'kN/m' if params["units"] == "metric" else 'lb/ft'}
- Total Vertical Force: {stability_results["total_vertical_force"]:.2f} {'kN/m' if params["units"] == "metric" else 'lb/ft'}
- Resisting Moment about Toe: {stability_results["resisting_moment_about_toe"]:.2f} {'kN.m/m' if params["units"] == "metric" else 'lb.ft/ft'}

## Earth Pressure
- Active Pressure at Base: {stability_results["Pa_at_base"]:.2f} {'kPa' if params["units"] == "metric" else 'psf'}
- Active Force (Pa): {stability_results["Pa_force"]:.2f} {'kN/m' if params["units"] == "metric" else 'lb/ft'} (acting at {stability_results["y_Pa"]:.2f} {'m' if params["units"] == "metric" else 'ft'} from base)
- Passive Pressure at Base: {stability_results["Pp_at_base"]:.2f} {'kPa' if params["units"] == "metric" else 'psf'}
- Passive Force (Pp): {stability_results["Pp_force"]:.2f} {'kN/m' if params["units"] == "metric" else 'lb/ft'} (acting at {stability_results["y_Pp"]:.2f} {'m' if params["units"] == "metric" else 'ft'} from base)
- Overturning Moment about Toe: {stability_results["overturning_moment"]:.2f} {'kN.m/m' if params["units"] == "metric" else 'lb.ft/ft'}
- Shear Key Resistance: {stability_results["shear_key_resistance"]:.2f} {'kN/m' if params["units"] == "metric" else 'lb/ft'}

## Stability Analysis
- Factor of Safety (Overturning): {stability_results["FS_overturning"]:.2f}
- Net Sliding Force: {stability_results["sliding_force"]:.2f} {'kN/m' if params["units"] == "metric" else 'lb/ft'}
- Total Resisting Sliding Force: {stability_results["total_resisting_sliding_force"]:.2f} {'kN/m' if params["units"] == "metric" else 'lb/ft'}
- Factor of Safety (Sliding): {stability_results["FS_sliding"]:.2f}
- Eccentricity (e): {stability_results["e"]:.2f} {'m' if params["units"] == "metric" else 'ft'}
- Maximum Bearing Pressure (q_max): {stability_results["q_max"]:.2f} {'kPa' if params["units"] == "metric" else 'psf'}
- Minimum Bearing Pressure (q_min): {stability_results["q_min"]:.2f} {'kPa' if params["units"] == "metric" else 'psf'}
- Factor of Safety (Bearing Capacity): {stability_results["FS_bearing"]:.2f}

## Rebar Information
{rebar_info}
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


class TestRetainingWallCalculator(unittest.TestCase):

    def test_default_calculation(self):
        results = calculate_retaining_wall_for_test()
        self.assertIsNotNone(results)
        self.assertIn("FS_overturning", results)
        self.assertIn("FS_sliding", results)
        self.assertIn("FS_bearing", results)
        self.assertIn("q_max", results)

        # Basic checks for reasonable values (these are not strict assertions, just sanity checks)
        self.assertGreater(results["FS_overturning"], 0.0)
        self.assertGreater(results["FS_sliding"], 0.0)
        self.assertGreater(results["FS_bearing"], 0.0)
        self.assertGreater(results["q_max"], 0.0)

    def test_overridden_parameters(self):
        user_overrides = {
            "wall_height_m": 6.0,
            "active_soil_type": "loose_backfill_soil",
            "passive_soil_type": "compacted_to_cbr_6_percent_soil",
            "groundwater_level_m_below_base": 0.5,
        }
        results = calculate_retaining_wall_for_test(user_overrides)

        self.assertIsNotNone(results)
        self.assertIn("FS_overturning", results)
        self.assertIn("FS_sliding", results)
        self.assertIn("FS_bearing", results)
        self.assertIn("q_max", results)

        # Check if parameters were actually overridden (e.g., by checking summary)
        self.assertIn("\"wall_height_m\": 6.0", str(results["detailed_report_md"]))
        self.assertIn("loose_backfill_soil", str(results["detailed_report_md"]))

    def test_imperial_units_calculation(self):
        user_overrides = {"units": "imperial"}
        results = calculate_retaining_wall_for_test(user_overrides)

        self.assertIsNotNone(results)
        self.assertIn("FS_overturning", results)
        self.assertIn("FS_sliding", results)
        self.assertIn("FS_bearing", results)
        self.assertIn("q_max", results)

        # Check if units are reflected in the summary
        self.assertIn("ft", results["summary"])
        self.assertIn("psf", results["summary"])
        self.assertIn("in^2/ft", results["summary"])

    def test_slab_material_none_and_shear_key(self):
        user_overrides = {
            "slab_material": "none",
            "shear_key_used": True,
        }
        results = calculate_retaining_wall_for_test(user_overrides)

        self.assertIsNotNone(results)
        # Expect shear key resistance to be 0 if slab_material is 'none'
        self.assertIn("Shear Key Resistance: 0.00", results["detailed_report_md"])

    def test_shear_key_position_heel(self):
        user_overrides = {
            "shear_key_used": True,
            "shear_key_position": "heel",
            "slab_material": "concrete",
        }
        results = calculate_retaining_wall_for_test(user_overrides)
        self.assertIsNotNone(results)
        # Expect shear key resistance to be 0 if shear_key_position is 'heel'
        self.assertIn("Shear Key Resistance: 0.00", results["detailed_report_md"])

    def test_groundwater_effect(self):
        # Run with no groundwater
        user_overrides_no_gw = {"groundwater_level_m_below_base": 100.0} # Effectively no groundwater
        results_no_gw = calculate_retaining_wall_for_test(user_overrides_no_gw)

        # Run with groundwater at base of foundation
        user_overrides_with_gw = {"groundwater_level_m_below_base": 0.0}
        results_with_gw = calculate_retaining_wall_for_test(user_overrides_with_gw)

        # Extract Active Force values using regex
        pa_no_gw_match = re.search(r"Active Force \(Pa\): (\d+\.\d+)", results_no_gw["detailed_report_md"])
        pa_with_gw_match = re.search(r"Active Force \(Pa\): (\d+\.\d+)", results_with_gw["detailed_report_md"])

        self.assertIsNotNone(pa_no_gw_match)
        self.assertIsNotNone(pa_with_gw_match)

        pa_no_gw = float(pa_no_gw_match.group(1))
        pa_with_gw = float(pa_with_gw_match.group(1))

        # Expect active force to be higher with groundwater due to hydrostatic pressure
        self.assertGreater(pa_with_gw, pa_no_gw)


if __name__ == '__main__':
    unittest.main()