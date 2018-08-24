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
    def getConfig(self, configItem):
        from os.path import dirname, join, exists, abspath, isfile
        from json import load
        ###load config file
        json_file_config = join(dirname(abspath(__file__)), 'config/tags.json')
        if isfile(json_file_config):
            with open(json_file_config) as f:
                config_json = load(f)
        array = []
        ###select all major tags:
        if configItem == "all":
            for tag in config_json:
                array.append(tag)
        ###select all keys for the desried tag:
        if configItem != "all":
            for key in config_json[configItem]:
                array.append(key)
        return array
    def getParameterInfo(self):
        """Define parameter definitions"""
        ###let's read the config files with Tags and keys###
        param0 = arcpy.Parameter(
            displayName="Tag",
            name="in_tag",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        param0.filter.list = self.getConfig('all')
        param0.value = param0.filter.list[0]
        param1 = arcpy.Parameter(
            displayName="Key",
            name="in_key",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        params = [param0, param1]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        #update the parameters of keys accroding the values of "in_tag"
        parameters[1].filter.list = self.getConfig(parameters[0].value)
        #parameters[1].value = parameters[1].filter.list[0]
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return
    def execute(self, parameters, messages):
        """The source code of the tool."""
        arcpy.AddMessage("collecting " + parameters[0].value + " " + parameters[1].value)
        return
