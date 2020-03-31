import shapely
import math
from random import getrandbits

def to_polygon(geometry, scale, x_min, y_max, id_str, label, link, value):
    centroid = geometry.centroid.coords[0]
    polygons = []
    if type(geometry) is shapely.geometry.multipolygon.MultiPolygon:
        for polygon in geometry:
            polygons.append(list(polygon.exterior.coords))
    elif type(geometry) is shapely.geometry.polygon.Polygon:
        polygons.append(list(geometry.exterior.coords))
    else:
        raise ValueError("Geometry is not a polygon or multipolygon")
    html = f'''<g class="thing" onmouseover="activate_label('{label}');" onmouseout="deactivate_label();">
               <a href="{link}" style="color:rgba(255,255,255,0.0);">'''
    for polygon in polygons:
        html += f'<polygon id="{id_str}" points="'
        for point in polygon:
            html += str(scale * (point[0] - x_min)) + ',' + str(scale * (y_max - point[1])) + ' '
        html += '"/>'
    html += "</a></g>"
    return html

def to_html(gdf, geometry_col, value_col, id_col=None, label_col=None, link_col=None, width=None):
    min_x = min([row[geometry_col].bounds[0] for i, row in gdf.iterrows()])
    min_y = min([row[geometry_col].bounds[1] for i, row in gdf.iterrows()])
    max_x = max([row[geometry_col].bounds[2] for i, row in gdf.iterrows()])
    max_y = max([row[geometry_col].bounds[3] for i, row in gdf.iterrows()])
    if not width:
        width = 1000
    scale = width / (max_x - min_x)
    height = math.ceil(scale * (max_y - min_y))
    
    num_regions = gdf.shape[0]
    
    geometries = list(gdf[geometry_col])
    
    values = list(gdf[value_col])
    
    if not id_col:
        ids = [f'region_id_{getrandbits(64)}' for i in range(num_regions)]
    else:
        ids = list(gdf[id_col])
    
    if not label_col:
        labels = ['' for i in range(num_regions)]
    else:
        labels = list(gdf[label_col])
        
    if not link_col:
        links = [None for i in range(num_regions)]
    else:
        links = list(gdf[link_col])
        
    
    html = '''<html>'''
    
    html += '''<style>'''
    for i in range(num_regions):
        html += '#' + str(ids[i]) + ' {stroke-width:1; stroke:white; fill:rgba(' + str(values[i]) +',255,0,1.0);}'
        html += '#' + str(ids[i]) + ':hover {stroke-width:1; stroke:white; fill:rgba(' + '0' + ',255,255,1.0);}'
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

    for i in range(num_regions):
        html += to_polygon(
            geometries[i], scale,
            min_x, max_y, ids[i], labels[i],
            links[i], values[i]
        )
        
    html += '</svg> </body></html>'
    return html