import arcpy


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [Tool]


class Tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Tool"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
            displayName="Digital Elevation Model",
            name="in_DEM",
            datatype="GPRasterLayer",
            parameterType="Required",
            direction="Input")

        param1 = arcpy.Parameter(
            displayName="Water Level Raster",
            name="in_Water",
            datatype="GPRasterLayer",
            parameterType="Required",
            direction="Input")

        param2 = arcpy.Parameter(
            displayName="Initial Water Shapefile",
            name="in_waterbody",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")

        param3 = arcpy.Parameter(
            displayName="Sea Level Rise in Inches",
            name="in_SLR_in",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input")

        param4 = arcpy.Parameter(
            displayName="Uncertainty",
            name="in_Uncertainty",
            datatype="GPDouble",
            parameterType="Optional")

        param4.value = 6.2

        param5 = arcpy.Parameter(
            displayName = r"Letter ID (for identification, not computation)",
            name="in_Id",
            datatype="GPString",
            parameterType="Optional")
       

        param6 = arcpy.Parameter(
            displayName="Working Directory",
            name="in_WD",
            datatype="DEFolder",
            parameterType="Required")
      
        params = [param0, param1, param2, param3, param4, param5, param6]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        
        # Import arcpy module
        import arcpy
        from arcpy import env
        from arcpy.sa import *

        #Get the Spatial Reference from the reference file
        reference="G://Steve/Spatial_Reference/reference.prj"
        


        # Script arguments

	
        Digital_Elevation_Model = parameters[0].valueAsText

        Tide_Raster = parameters[1].valueAsText

        Initial_Water = parameters[2].valueAsText

        Sea_Level_Rise_Inches = parameters[3].valueAsText

        Uncertainty = parameters[4].valueAsText

        LetterId = parameters[5].valueAsText

        Working_Directory = parameters[6].valueAsText

        Water_Depth_Output_Dir = "%s/%s_%s.img", Working_Directory, LetterId, Sea_Level_Rise_Inches  
        
       
	Final_Output_Name = "%s_%s.shp" %(LetterId, Sea_Level_Rise_Inches) 
	
        
        scratchworkspace2 = "G:\\temp"
        my_temp="%s/mytemp.img" %(scratchworkspace2)
	


        # Local variables:
        # just keep them in memory, don't need them.        


        # Set Geoprocessing environments
        arcpy.env.scratchWorkspace = "G:\\temp"

        ####Baseline Run####

        Final_Output_Name = "%s_BE_%s.shp" %(LetterId, Sea_Level_Rise_Inches) 
        Final_Output_Layer_Name = "%s_BE_%s" %(LetterId, Sea_Level_Rise_Inches) 
        # Process: Depth Raster
        Water_Depth_Output = Raster(Digital_Elevation_Model) - (Raster(Tide_Raster) + (float(Sea_Level_Rise_Inches) / float(12)))
        
        # Process: Offset Best Calc

        Offset = Water_Depth_Output

        # Process: Reclassify
	reclassified_to_1 = Con(Offset <= 0, 1, 0)

        arcpy.Delete_management(my_temp)    
	reclassified_to_1.save(my_temp)
        
        # Process: Convert to Polygon
	arcpy.CreateFeatureclass_management(scratchworkspace2, "temp_fc","POLYGON", spatial_reference=26918)
        path_to_new_fc = scratchworkspace2 + "/" + Final_Output_Name
	#arcpy.AddMessage(path_to_new_fc)        
        arcpy.RasterToPolygon_conversion(reclassified_to_1, path_to_new_fc, "SIMPLIFY")

        # Process: Convert To Layer and Select
	arcpy.MakeFeatureLayer_management(path_to_new_fc, Final_Output_Layer_Name , '"GRIDCODE" = 1')
        arcpy.SelectLayerByLocation_management(Final_Output_Layer_Name, 'INTERSECT', Initial_Water, 5, 'NEW_SELECTION')
        
        arcpy.FeatureClassToShapefile_conversion(Final_Output_Layer_Name, Working_Directory)
        
	arcpy.Delete_management(path_to_new_fc)
        arcpy.Delete_management(my_temp)
	arcpy.Delete_management("%s/temp_fc.shp" % scratchworkspace2)
	

  	####Offset Run####

        Final_Output_Name = "%s_BC_%s.shp" %(LetterId, Sea_Level_Rise_Inches) 
	Final_Output_Layer_Name = "%s_BC_%s" %(LetterId, Sea_Level_Rise_Inches) 

	# Process: Depth Raster
        Water_Depth_Output = Raster(Digital_Elevation_Model) - (Raster(Tide_Raster) + (float(Sea_Level_Rise_Inches) / float(12)))
        
        # Process: Offset Best Calc

        Offset = Water_Depth_Output + (float(Uncertainty) / 12.0) 

        # Process: Reclassify
	reclassified_to_1 = Con(Offset <= 0, 1, 0)

        arcpy.Delete_management(my_temp)    
	reclassified_to_1.save(my_temp)
        
        # Process: Convert to Polygon
	arcpy.CreateFeatureclass_management(scratchworkspace2, "temp_fc","POLYGON", spatial_reference=26918)
        path_to_new_fc = scratchworkspace2 + "/" + Final_Output_Name
        arcpy.RasterToPolygon_conversion(reclassified_to_1, path_to_new_fc, "SIMPLIFY")

        # Process: Convert To Layer and Select
	arcpy.MakeFeatureLayer_management(path_to_new_fc, Final_Output_Layer_Name , '"GRIDCODE" = 1')
        arcpy.SelectLayerByLocation_management(Final_Output_Layer_Name, 'INTERSECT', Initial_Water, 5, 'NEW_SELECTION')
        
        arcpy.FeatureClassToShapefile_conversion(Final_Output_Layer_Name, Working_Directory)
        
	arcpy.Delete_management(path_to_new_fc)
        arcpy.Delete_management(my_temp)
	arcpy.Delete_management("%s/temp_fc.shp" % scratchworkspace2)

        return
