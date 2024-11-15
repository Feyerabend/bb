def is_point_inside_polygon(x, y, polygon):
    num_vertices = len(polygon)
    inside = False
    p1x, p1y = polygon[0]
    
    for i in range(num_vertices + 1):
        p2x, p2y = polygon[i % num_vertices]
        
        # on line between p1 and p2
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    
    return inside

def fill_polygon(polygon, width, height):
    """
    Fyller polygonen på ett raster baserat på Even-Odd-regeln.
    """
    # Skapa en bildraster (matris)
    raster = [[False] * width for _ in range(height)]
    
    # Iterera genom alla pixlar i rasterbilden
    for y in range(height):
        for x in range(width):
            # Om punkten (x, y) ligger innanför polygonen, fyll den
            if is_point_inside_polygon(x, y, polygon):
                raster[y][x] = True
    
    return raster

def print_raster(raster):
    """
    Skriver ut rasterbilden.
    
    :param raster: En lista med pixlar (True om fylld, False om inte).
    """
    for row in raster:
        print(' '.join(['#' if pixel else '.' for pixel in row]))

polygon = [(2, 2), (6, 2), (6, 6), (2, 6)]  # fyrkant
width = 10
height = 10

raster = fill_polygon(polygon, width, height)
print_raster(raster)

