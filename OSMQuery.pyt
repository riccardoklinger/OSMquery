import arcpy


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "OSM Query Toolbox"
        self.alias = "OSM Query Toolbox"

        # List of tool classes associated with this toolbox
        self.tools = [Tool]

class Tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Get OSM Data"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        ###let's read the config files with Tags and keys###
        from os.path import dirname, join, exists, abspath, isfile
        from json import load
        json_file_config = join(dirname(abspath(__file__)), 'config/tags.json')
        #json_file_config = r'C:/inetpub/wwwroot/OSMquery/config/tags.json'
        ###currently C:/inetpub/wwwroot/OSMquery/config.json


        param0 = arcpy.Parameter(
            displayName="Tag",
            name="in_tag",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        if isfile(json_file_config):
            with open(json_file_config) as f:
                config_json = load(f)

        tagArray = []
        for tag in config_json:
            tagArray.append(tag)
        param0.filter.list = tagArray
        params = [param0]
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
        return
