import shapely
import math

def to_polygon(geometry, scale, x_min, y_max, label, link):
    centroid = geometry.centroid.coords[0]
    polygons = []
    if type(geometry) is shapely.geometry.multipolygon.MultiPolygon:
        for polygon in geometry:
            polygons.append(list(polygon.exterior.coords))
    elif type(geometry) is shapely.geometry.polygon.Polygon:
        polygons.append(list(geometry.exterior.coords))
    else:
        raise ValueError("Geometry is not a polygon or multipolygon")
    html = f'''<g class="thing" onmouseover="activate_label('{label}');" onmouseout="deactivate_label();"> <a href="{link}" style="color:rgba(255,255,255,0.0);">'''
    for polygon in polygons:
        html += '<polygon points="'
        for point in polygon:
            html += str(scale * (point[0] - x_min)) + ',' + str(scale * (y_max - point[1])) + ' '
        html += '" style="stroke:black;stroke-width:1"/>'
    html += "</a></g>"
    return html

def to_html(gdf, label_column, link_column, geometry_column, width):
    min_x = min([row['geometry_simplified'].bounds[0] for i, row in gdf.iterrows()])
    min_y = min([row['geometry_simplified'].bounds[1] for i, row in gdf.iterrows()])
    max_x = max([row['geometry_simplified'].bounds[2] for i, row in gdf.iterrows()])
    max_y = max([row['geometry_simplified'].bounds[3] for i, row in gdf.iterrows()])
    scale = width / (max_x - min_x)
    height = math.ceil(scale * (max_y - min_y))
    html = '''<html>
                <style>
                  .thing polygon {fill: white;}
                  .thing:hover polygon{fill: orange;}
                </style>'''
    html += '''<script>
               function activate_label(label) {
                   document.getElementById("region_label").innerText = label;
               }
               function deactivate_label() {
                   document.getElementById("region_label").innerText = "Select a Region";
               }
               </script>'''
    html += f'<body> <h1 id="region_label">Select a Region</h1><svg height="{height}" width="{width}">'
    for i, row in gdf.iterrows():
        label = row[label_column]
        link = row[link_column]
        geometry = row[geometry_column]
        html += to_polygon(
            geometry, scale,
            min_x, max_y, label, link
        )
    html += '</svg> </body></html>'
    return html