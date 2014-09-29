import arcpy

arcpy.env.workspace = r"C:\testdata"

arcpy.ImportToolbox("Stream.tbx")
arcpy.myextra.StreamCrossSection("Streams.shp", "StartingPointDebugger.shp", "22222 Feet", "2222 Feet")
