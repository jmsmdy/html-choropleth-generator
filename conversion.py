import shapely
import math

def to_polygon(geometry, scale, x_min, y_max, label, link, value):
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
        html += f'<polygon id="polygon_{label}" points="'
        for point in polygon:
            html += str(scale * (point[0] - x_min)) + ',' + str(scale * (y_max - point[1])) + ' '
        html += '"/>'
    html += "</a></g>"
    return html

def to_html(gdf, label_col, link_col, geometry_col, value_col, width):
    min_x = min([row['geometry_simplified'].bounds[0] for i, row in gdf.iterrows()])
    min_y = min([row['geometry_simplified'].bounds[1] for i, row in gdf.iterrows()])
    max_x = max([row['geometry_simplified'].bounds[2] for i, row in gdf.iterrows()])
    max_y = max([row['geometry_simplified'].bounds[3] for i, row in gdf.iterrows()])
    scale = width / (max_x - min_x)
    height = math.ceil(scale * (max_y - min_y))
    html = '''<html>
                <style>'''
    for i, row in gdf.iterrows():
        polygon_id = f'polygon_{row[label_col]}'
        value = str(row[value_col])
        html += '#' + polygon_id + ' {stroke-width:1; stroke:black; fill:rgba(' + value +',255,0,1.0);}'
        html += '#' + polygon_id + ':hover {stroke-width:3; stroke:black; fill:rgba(' + value + ',255,0,1.0);}'
    html += '''</style>'''
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
        label = row[label_col]
        link = row[link_col]
        geometry = row[geometry_col]
        value = row[value_col]
        html += to_polygon(
            geometry, scale,
            min_x, max_y, label,
            link, value
        )
    html += '</svg> </body></html>'
    return html