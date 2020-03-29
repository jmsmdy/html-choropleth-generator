import shapely

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
    html = f'<g class="thing"> <a href="{link}" style="color:rgba(255,255,255,0.0);">'
    for polygon in polygons:
        html += '<polygon points="'
        for point in polygon:
            html += str(scale * (point[0] - x_min)) + ',' + str(scale * (y_max - point[1])) + ' '
        html += '" style="stroke:black;stroke-width:1"/>'
    html += f'''</a><g>
                <text x={200}, y={450} text-anchor="left" dominant-baseline="middle"> {label} </text>
                </g></g>'''
    return html

def to_html(gdf, label_column, link_column, geometry_column, pixels):
    min_x = min([row['geometry_simplified'].bounds[0] for i, row in gdf.iterrows()])
    min_y = min([row['geometry_simplified'].bounds[1] for i, row in gdf.iterrows()])
    max_x = max([row['geometry_simplified'].bounds[2] for i, row in gdf.iterrows()])
    max_y = max([row['geometry_simplified'].bounds[3] for i, row in gdf.iterrows()])
    if (max_y - min_y) > (max_x - min_x):
        scale = pixels / (max_y - min_y)
    else:
        scale = pixels / (max_x - min_x)
    html = '''<html>
                <style>
                  .thing polygon {fill: white;}
                  .thing:hover polygon{fill: orange;}
                  
                  .thing g text {fill: rgba(255,255,255,0.0);
                      font-size:140px;
                      pointer-events: none;
                  }

                  .thing:hover g text{ /*the span will display just on :hover state*/
                        font-size:140px;
                        fill:rgba(255, 0, 0, 1.0);
                        text-shadow: #000 0px 0px 10px;
                        pointer-events: none;
                  }
                </style>''' + f'<body> <h1> SELECT A REGION </h1><svg height="{pixels}" width="{pixels}">' # style="transform:scaleY(-1);">'
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