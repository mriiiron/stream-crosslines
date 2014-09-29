# ----------------------------------------------------------------------------------
# File Name    : StreamCrossSection.py
# Author       : Caiyi Felix Zhong
# Organization : UT Dallas
# Start Date   : Nov. 5th, 2013
#
# -- Description --
#
# To create a new feature class containing perpendicular cross section line segments
# at some starting point on an existing line feature class (i.e. the stream) at some
# regular interval (e.g. every 100 feet).
#
# This scripts is written for GISC 6317.501 - Computer Programming for GIS.
#
# -- Parameters --
#
# ID    Name                Direction   Type
# 0     Streams             Input       Polyline
# 1     Starting Points     Input       Feature Set (Interactive)
# 2     Length of Study     Input       Linear Unit
# 3     Interval            Input       Linear Unit
#
# -- Output --
#
# A new feature class, containing perpendicular cross section line segments.
#
# ----------------------------------------------------------------------------------

# Import ArcPy and NumPy
import arcpy
import numpy
import os

# Import my modules
import GeometryProcess
import UnitConvertion

# Set workspace
arcpy.env.workspace = arcpy.GetParameterAsText(0)
arcpy.env.overwriteOutput = True

# Get input streams, and interactively user-defined starting points
streams = arcpy.GetParameterAsText(1)
user_input_points = arcpy.FeatureSet(arcpy.GetParameterAsText(2))

# Get the length of study area, and the cross section spacing (as text here)
length_of_study_raw = arcpy.GetParameterAsText(3)
interval_raw = arcpy.GetParameterAsText(4)

# Match the unit of input parameters (to the unit of input stream's spatial reference)
stream_mpu = arcpy.Describe(streams).spatialReference.metersPerUnit
len_splited = length_of_study_raw.split()
intv_splited = interval_raw.split()
length_of_study_meters = UnitConvertion.UnitConvertionToMeters(float(len_splited[0]), len_splited[1])
interval_meters = UnitConvertion.UnitConvertionToMeters(float(intv_splited[0]), intv_splited[1])
length_of_study = length_of_study_meters / stream_mpu
interval = interval_meters / stream_mpu

# Save the user input points first
user_input_points.save(arcpy.env.workspace + "\\TEMPUserInputPoints.shp")

# Note: ONLY FEATURE LAYERS CAN BE SELECTED! Thus, transform the user input into a feature layer
arcpy.management.MakeFeatureLayer("TEMPUserInputPoints.shp", "points_lyr")

# Do selection, and ignore other points that are outside the streams
arcpy.management.SelectLayerByLocation("points_lyr", overlap_type = "INTERSECT", select_features = streams)
starting_points = arcpy.env.workspace + "\\TEMPStartingPoints.shp"
arcpy.management.CopyFeatures("points_lyr", starting_points)

# Get the number of streams selected
selected_stream_count = int(arcpy.management.GetCount(starting_points).getOutput(0))

# If no available starting point here, do nothing
if selected_stream_count == 0:
    arcpy.AddMessage("WARNING: No available starting points.")

else:

    # Get the output location and filename. This if for the cross points
    output_crosspoints = arcpy.GetParameterAsText(5)
    arcpy.management.CreateFeatureclass(arcpy.env.workspace, output_crosspoints, geometry_type = "Point", spatial_reference = arcpy.Describe(streams).spatialReference)
    cursor_icrosspoints = arcpy.da.InsertCursor(output_crosspoints, ["SHAPE@"])

    # This if for the cross lines
    output_crosslines = arcpy.GetParameterAsText(6)
    arcpy.management.CreateFeatureclass(arcpy.env.workspace, output_crosslines, "Polyline", spatial_reference = arcpy.Describe(streams).spatialReference)
    cursor_icrosslines = arcpy.da.InsertCursor(output_crosslines, ["SHAPE@"])

    # Iterate each available starting point
    with arcpy.da.SearchCursor(starting_points, "SHAPE@") as cursor_point:
        for row_point in cursor_point:

            # Test that if the current starting point matches a river
            # NOTE: In this case I have to cast PointGeometry to Point (using firstPoint property), or the within() won't work. I DON"T KNOW WHY.
            start_point = row_point[0].firstPoint

            # Iterate each stream, and find the stream that "matches" the current starting point
            with arcpy.da.SearchCursor(streams, "SHAPE@") as cursor_stream:
                for row_stream in cursor_stream:
                    if start_point.within(row_stream[0]) or start_point.touches(row_stream[0]):

                        # Get the stream as point list
                        stream_points = row_stream[0].getPart(0)

                        # Iterate each segment in the stream. Note that the number of segment is less than the number of points by 1
                        for i in range(0, stream_points.count - 1):

                            # Create a temporary polyline geometry for the current segment
                            stream_segment = GeometryProcess.ExtractSegment(stream_points, i)
                            
                            # arcpy.AddMessage("Segment {0}: ({1} {2}) ({3} {4})".format(i, stream_segment.firstPoint.X, stream_segment.firstPoint.Y, stream_segment.lastPoint.X, stream_segment.lastPoint.Y))

                            # Search until the starting point is on this segment
                            if numpy.allclose([start_point.X, start_point.Y], [stream_segment.firstPoint.X, stream_segment.firstPoint.Y], atol = 0.001) or start_point.within(stream_segment):
                                arcpy.AddMessage("Available Starting Point: ({0} {1})".format(start_point.X, start_point.Y))

                                # Create a sub-stream: Starts from starting point, ends with the original stream ends
                                # Note: I didn't use SplitLineAtPoint tool here, but it should work
                                substream_array = arcpy.Array()
                                substream_array.add(start_point)
                                for j in range(i + 1, stream_points.count):
                                    substream_array.add(stream_points[j])
                                substream = arcpy.Polyline(substream_array)
                                substream_points = substream.getPart(0)

                                # Draw cross sections
                                distance_along = interval
                                k = 0
                                former_segment = GeometryProcess.ExtractSegment(stream_points, 0)
                                while distance_along <= length_of_study:
                                    cross_point = substream.positionAlongLine(distance_along).firstPoint
                                    if numpy.allclose([cross_point.X, cross_point.Y], [substream.lastPoint.X, substream.lastPoint.Y], atol = 0.001):
                                        break
                                    while k < substream.pointCount - 1:
                                        substream_segment = GeometryProcess.ExtractSegment(stream_points, k)
                                        if numpy.allclose([cross_point.X, cross_point.Y], [substream_segment.firstPoint.X, substream_segment.firstPoint.Y]):
                                            cross_line = GeometryProcess.GetPerpendicularCrossline(former_segment.firstPoint, substream_segment.lastPoint, cross_point, interval)
                                            cursor_icrosslines.insertRow([cross_line])
                                            break
                                        if cross_point.within(substream_segment):
                                            cross_line = GeometryProcess.GetPerpendicularCrossline(substream_segment.firstPoint, substream_segment.lastPoint, cross_point, interval)
                                            cursor_icrosslines.insertRow([cross_line])
                                            break
                                        former_segment = substream_segment
                                        k = k + 1
                                    cursor_icrosspoints.insertRow([cross_point])
                                    distance_along += interval

                                # End processing this stream
                                break

                        # End processing this starting point
                        # We assume that each starting point only matches one stream
                        # If one starting point is on the intersection of two stream, only the first stream may be processed
                        break

    # Delete cursors
    del cursor_icrosspoints
    del cursor_icrosslines
    del cursor_point
    del cursor_stream

# Delete temporary feature class
arcpy.management.Delete(arcpy.env.workspace + "\\TEMPUserInputPoints.shp")
arcpy.management.Delete(arcpy.env.workspace + "\\TEMPStartingPoints.shp")
