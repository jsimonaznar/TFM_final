def pointinpoly(point, polygon):
    """
    Check if a given point is inside of a specific region. Based on Ray-Tracing Algorithm

    Parameters:
    - point: Coordinates [longitude, latitude] of the point to be checked
    - polygon: Coordinates of the polygon's vertices
    """
    x, y = point

    # Adjust point coordinates to roi.vertices reference system
    if x <= -90:
        x += 180
    elif x > 90:
        x -= 180
    

    inside = False
    n = len(polygon)
    p1x, p1y = polygon[0]

    # Iterates through each edge of the polygon
    for i in range(n + 1):
        p2x, p2y = polygon[i % n] # Ensures that it goes back to the first vertex

        # Check if the point is within the y-range of the polygon edge
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    # Compute the intersection of the horizontal line through the point with the polygon edge
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside

        p1x, p1y = p2x, p2y

    return inside