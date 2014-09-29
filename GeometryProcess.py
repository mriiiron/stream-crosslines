import arcpy
import math

def CreateSegment(p1, p2):
    return arcpy.Polyline(arcpy.Array([arcpy.Point(p1.X, p1.Y), arcpy.Point(p2.X, p2.Y)]))

def ExtractSegment(point_array, i):
    return arcpy.Polyline(arcpy.Array([arcpy.Point(point_array[i].X, point_array[i].Y), arcpy.Point(point_array[i + 1].X, point_array[i + 1].Y)]))

def GetPerpendicularCrossline(line_segment_point_1, line_segment_point_2, cross_point, cross_line_length_half):
    x1 = line_segment_point_1.X
    y1 = line_segment_point_1.Y
    x2 = line_segment_point_2.X
    y2 = line_segment_point_2.Y
    if x1 == x2:
        x1_cross = cross_point.X - cross_line_length_half
        y1_cross = cross_point.Y
        x2_cross = cross_point.X + cross_line_length_half
        y2_cross = cross_point.Y
    else:
        if x1 > x2:
            (x1, y1, x2, y2) = (x2, y2, x1, y1)
        tanA = (y2 - y1) / (x2 - x1)
        cosA = 1.0 / math.sqrt(1.0 + tanA ** 2)
        sinA = tanA / math.sqrt(1.0 + tanA ** 2)
        x1_cross = cross_point.X - cross_line_length_half * sinA
        y1_cross = cross_point.Y + cross_line_length_half * cosA
        x2_cross = cross_point.X + cross_line_length_half * sinA
        y2_cross = cross_point.Y - cross_line_length_half * cosA
    return arcpy.Polyline(arcpy.Array([arcpy.Point(x1_cross, y1_cross), arcpy.Point(x2_cross, y2_cross)]))
