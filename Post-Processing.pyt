import arcpy
from arcpy import env

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Post-Processing"
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
	    displayName   = "Layers to Merge",
            name          = "layers_in",
	    multiValue    = True,
            datatype      = "GPLayer",
	    parameterType = "Required")
        
        param1 = arcpy.Parameter(
            displayName="Working Directory",
            name="in_WD",
            datatype="DEFolder",
            parameterType="Required")

	param2 = arcpy.Parameter(
	    displayName   = "Output Name",
            name          = "output_name",
	    datatype      = "GPString",
            parameterType = "Optional")

	param2.value = "Output"
	     
	params = [param0, param1, param2]
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

	input_layer_list  = parameters[0].valueAsText
	working_directory = parameters[1].valueAsText
	output_name       = parameters[2].valueAsText
        #spatial_reference = arcpy.SpatialReference(26918)

	
	#Set the Workspace
	env.workspace = working_directory	        
	

	#union the layers into one shapefile

	print(input_layer_list)
	arcpy.Union_analysis(in_features = input_layer_list, out_feature_class = "merged") 

	#Dissolve the features
	arcpy.Dissolve_management ("merged.shp", "dissolved")

	#Simplilfy
	arcpy.SimplifyPolygon_cartography("dissolved.shp", "simplified", "POINT_REMOVE", 5, 1000, "NO_CHECK", "NO_KEEP")
	
	#Smooth
	arcpy.SmoothPolygon_cartography("simplified.shp", "smoothed" ,"PAEK",50,"NO_FIXED","NO_CHECK")
	
	#split into parts
	arcpy.MultipartToSinglepart_management("smoothed.shp", output_name)	   	

	#garbage collection
	arcpy.Delete_management("merged.shp")
	arcpy.Delete_management("dissolved.shp")
	arcpy.Delete_management("simplified.shp")
	arcpy.Delete_management("smoothed.shp")

        return