import math

def generate_svg_drawing(params, geometry, stability_results):
    width = 800
    height = 600
    scale = 50 # pixels per meter

    # Calculate coordinates
    # Origin at bottom-left of the base slab
    ox = 50
    oy = height - 50

    # Determine units for display
    length_unit = 'm' if params['units'] == 'metric' else 'ft'
    force_unit = 'kN' if params['units'] == 'metric' else 'lb'
    pressure_unit = 'kPa' if params['units'] == 'metric' else 'psf'

    # Base Slab coordinates
    base_slab_points = [
        (ox, oy),
        (ox + geometry["B_base"] * scale, oy),
        (ox + geometry["B_base"] * scale, oy - geometry["D_f"] * scale),
        (ox, oy - geometry["D_f"] * scale),
    ]

    # Wall Stem coordinates
    wall_bl_x = ox + geometry["wall_base_offset_from_toe"] * scale
    wall_bl_y = oy - geometry["D_f"] * scale

    if params["face_wall_position"] == "toe_side":
        wall_stem_points = [
            (wall_bl_x, wall_bl_y), # Bottom-left (front face at toe side)
            (wall_bl_x + geometry["t_base"] * scale, wall_bl_y), # Bottom-right
            (wall_bl_x + geometry["t_base"] * scale - (geometry["t_base"] - geometry["t_top"]) * scale, wall_bl_y - geometry["h_wall_stem"] * scale), # Top-right (sloped back)
            (wall_bl_x, wall_bl_y - geometry["h_wall_stem"] * scale), # Top-left (vertical front)
        ]
    else: # heel_side
        wall_stem_points = [
            (wall_bl_x, wall_bl_y), # Bottom-left
            (wall_bl_x + geometry["t_base"] * scale, wall_bl_y), # Bottom-right (front face at heel side)
            (wall_bl_x + geometry["t_base"] * scale, wall_bl_y - geometry["h_wall_stem"] * scale), # Top-right (vertical back)
            (wall_bl_x + (geometry["t_base"] - geometry["t_top"]) * scale, wall_bl_y - geometry["h_wall_stem"] * scale), # Top-left (sloped front)
        ]

    # Convert points to SVG polygon format
    base_slab_svg_points = " ".join([f"{p[0]},{p[1]}" for p in base_slab_points])
    wall_stem_svg_points = " ".join([f"{p[0]},{p[1]}" for p in wall_stem_points])

    svg_content = f"""
<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
  <rect x="0" y="0" width="{width}" height="{height}" fill="#f0f0f0"/>

  <!-- Ground Line -->
  <line x1="{ox}" y1="{oy - geometry["D_f"] * scale}" x2="{width - 50}" y2="{oy - geometry["D_f"] * scale}" stroke="#555" stroke-width="2"/>
  <text x="{ox + 10}" y="{oy - geometry["D_f"] * scale - 5}" font-size="12" fill="#555">Ground Level</text>

  <!-- Active Side Ground Elevation -->
  <line x1="{ox + geometry["B_base"] * scale}" y1="{oy - geometry["D_f"] * scale - geometry["active_side_ground_elevation"] * scale}" x2="{ox + geometry["B_base"] * scale + 100}" y2="{oy - geometry["D_f"] * scale - geometry["active_side_ground_elevation"] * scale}" stroke="#555" stroke-width="1" stroke-dasharray="5,5"/>
  <text x="{ox + geometry["B_base"] * scale + 110}" y="{oy - geometry["D_f"] * scale - geometry["active_side_ground_elevation"] * scale}" font-size="10" fill="#555">Active Side Ground</text>

  <!-- Passive Side Ground Elevation -->
  <line x1="{ox}" y1="{oy - geometry["D_f"] * scale - geometry["passive_side_ground_elevation"] * scale}" x2="{ox - 100}" y2="{oy - geometry["D_f"] * scale - geometry["passive_side_ground_elevation"] * scale}" stroke="#555" stroke-width="1" stroke-dasharray="5,5"/>
  <text x="{ox - 150}" y="{oy - geometry["D_f"] * scale - geometry["passive_side_ground_elevation"] * scale}" font-size="10" fill="#555">Passive Side Ground</text>

  <!-- Base Slab -->
  <polygon points="{base_slab_svg_points}" fill="#a0a0a0" stroke="black" stroke-width="2"/>

  <!-- Wall Stem -->
  <polygon points="{wall_stem_svg_points}" fill="#c0c0c0" stroke="black" stroke-width="2"/>

  <!-- Dimensions -->
  <line x1="{ox}" y1="{oy}" x2="{ox}" y2="{oy - geometry["H_total"] * scale}" stroke="blue" stroke-width="1" stroke-dasharray="5,5"/>
  <text x="{ox - 30}" y="{oy - geometry["H_total"] * scale / 2}" font-size="12" fill="blue" transform="rotate(-90 {ox - 30},{oy - geometry["H_total"] * scale / 2})">H_total: {geometry["H_total"]:.1f}{length_unit}</text>

  <line x1="{ox}" y1="{oy}" x2="{ox + geometry["B_base"] * scale}" y2="{oy}" stroke="blue" stroke-width="1" stroke-dasharray="5,5"/>
  <text x="{ox + geometry["B_base"] * scale / 2}" y="{oy + 20}" font-size="12" fill="blue">B_base: {geometry["B_base"]:.1f}{length_unit}</text>

  <line x1="{ox}" y1="{oy - geometry["D_f"] * scale}" x2="{ox + geometry["B_toe"] * scale}" y2="{oy - geometry["D_f"] * scale}" stroke="green" stroke-width="1" stroke-dasharray="2,2"/>
  <text x="{ox + geometry["B_toe"] * scale / 2}" y="{oy - geometry["D_f"] * scale - 10}" font-size="10" fill="green">Toe: {geometry["B_toe"]:.1f}{length_unit}</text>

  <line x1="{ox + geometry["B_toe"] * scale + geometry["t_base"] * scale}" y1="{oy - geometry["D_f"] * scale}" x2="{ox + geometry["B_base"] * scale}" y2="{oy - geometry["D_f"] * scale}" stroke="green" stroke-width="1" stroke-dasharray="2,2"/>
  <text x="{ox + geometry["B_toe"] * scale + geometry["t_base"] * scale + geometry["B_heel"] * scale / 2}" y="{oy - geometry["D_f"] * scale - 10}" font-size="10" fill="green">Heel: {geometry["B_heel"]:.1f}{length_unit}</text>

  <!-- Active Force Diagram -->
  <line x1="{ox + geometry["B_base"] * scale}" y1="{oy - geometry["D_f"] * scale}" x2="{ox + geometry["B_base"] * scale}" y2="{oy - geometry["H_total"] * scale}" stroke="red" stroke-width="2" marker-end="url(#arrowhead)"/>
  <polygon points="{ox + geometry["B_base"] * scale},{oy - geometry["D_f"] * scale} {ox + geometry["B_base"] * scale},{oy - geometry["H_total"] * scale} {ox + geometry["B_base"] * scale + stability_results["Pa_at_base"] * scale / 10},{oy - geometry["D_f"] * scale}" fill="red" fill-opacity="0.3"/>
  <text x="{ox + geometry["B_base"] * scale + 20}" y="{oy - geometry["H_total"] * scale / 2}" font-size="12" fill="red">Pa: {stability_results["Pa_force"]:.1f}{force_unit}</text>

  <!-- Passive Force Diagram -->
  <line x1="{ox}" y1="{oy - geometry["D_f"] * scale}" x2="{ox}" y2="{oy}" stroke="blue" stroke-width="2" marker-end="url(#arrowhead)"/>
  <polygon points="{ox},{oy - geometry["D_f"] * scale} {ox},{oy} {ox - stability_results["Pp_at_base"] * scale / 10},{oy - geometry["D_f"] * scale}" fill="blue" fill-opacity="0.3"/>
  <text x="{ox - 30}" y="{oy - geometry["D_f"] * scale / 2}" font-size="12" fill="blue">Pp: {stability_results["Pp_force"]:.1f}{force_unit}</text>

  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="0" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#555" />
    </marker>
  </defs>

</svg>
"""
    return svg_content