# -*- coding: utf-8 -*-
"""
/***************************************************************************
 OSMQuery
 A Python toolbox for ArcGIS
 OSM Overpass API frontend
                             -------------------
        begin                : 2018-08-20
        copyright            : (C) 2018 by Riccardo Klinger
        email                : riccardo.klinger at gmail dot com
        contributor          : Riccardo Klinger
 ***************************************************************************/
/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

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
    def getServer(self):
        from os.path import dirname, join, exists, abspath, isfile
        from json import load
        ###load config file
        json_file_config = join(dirname(abspath(__file__)), 'config/servers.json')
        if isfile(json_file_config):
            with open(json_file_config) as f:
                config_json = load(f)
        array = []
        ###select all major tags:
        for server in config_json["overpass_servers"]:
            array.append(server)
        return array
    def getParameterInfo(self):
        """Define parameter definitions"""
        ###let's read the config files with Tags and keys###
        param0 = arcpy.Parameter(
            displayName="Tag",
            name="in_tag",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )
        param0.filter.list = self.getConfig('all')
        param0.value = param0.filter.list[0]
        param1 = arcpy.Parameter(
            displayName="Key",
            name="in_key",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )
        param2 = arcpy.Parameter(
            displayName="Spatial Extent",
            name="in_regMode",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )
        param2.filter.list = ["geocode region","define simple bounding box"]
        param2.value = "geocode region"
        param3 = arcpy.Parameter(
            displayName="Region",
            name="in_region",
            datatype="GPString",
            parameterType="Optional",
            direction="Input"
        )
        param4 = arcpy.Parameter(
            displayName="Area Of Interest",
            name="in_bbox",
            datatype="GPExtent",
            parameterType="Optional",
            direction="Input"
        )
        param_out0 = arcpy.Parameter(
            displayName="Layer Containing the Points",
            name="out_nodes",
            datatype="GPFeatureLayer",
            parameterType="Derived",
            direction="Output"
        )
        param_out1 = arcpy.Parameter(
            displayName="Layer Containing the Polylines",
            name="out_ways",
            datatype="GPFeatureLayer",
            parameterType="Derived",
            direction="Output"
        )
        param_out2 = arcpy.Parameter(
            displayName="Layer Containing the Polygons",
            name="out_poly",
            datatype="GPFeatureLayer",
            parameterType="Derived",
            direction="Output"
        )
        params = [param0, param1, param2, param3, param4, param_out0, param_out1, param_out2]

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
        if parameters[2].value == "geocode region":
            parameters[3].enabled = True
            parameters[4].enabled = False
        else:
            parameters[3].enabled = False
            parameters[4].enabled = True
        #parameters[1].value = parameters[1].filter.list[0]
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return
    def execute(self, parameters, messages):
        """The source code of the tool."""
        arcpy.AddMessage("collecting " + parameters[0].value + " " + parameters[1].value)
        import json
        import requests
        url = "http://overpass-api.de/api/interpreter"
        start = "[out:json][timeout:25];("
        if parameters[2].value != "geocode region":
            bboxHead = ''
            bbox = [parameters[4].value.YMin,parameters[4].value.XMin,parameters[4].value.YMax,parameters[4].value.XMax]
            bboxData = '(' + ','.join(str(e) for e in bbox) + ');'
        else:
            ###getting areaID from Nominatim:
            nominatimURL = 'https://nominatim.openstreetmap.org/search?q=' + parameters[3].valueAsText + '&format=json'
            NominatimResponse = requests.get(nominatimURL)
            arcpy.AddMessage("gecode region using the url " + nominatimURL)
            try:
                NominatimData = NominatimResponse.json()

                for result in NominatimData:
                    if result["osm_type"] == "relation":
                        areaID = result['osm_id']
                        try:
                            arcpy.AddMessage("found area " + result['display_name'])
                        except:
                            arcpy.AddMessage("found area " + str(areaID))
                        break
                bboxHead = 'area(' + str(int(areaID) + 3600000000) + ')->.searchArea;'
                bboxData = '(area.searchArea);'
            except:
                arcpy.AddError("no area found!")
                return
        #get data using urllib
        nodeData = 'node["' + parameters[0].value + '"="' + parameters[1].value + '"]'
        wayData = 'way["' + parameters[0].value + '"="' + parameters[1].value + '"]'
        relationData = 'relation["' + parameters[0].value + '"="' + parameters[1].value + '"]'
        end = ');(._;>;);out;>;'
        query = start + bboxHead + nodeData + bboxData + wayData + bboxData + relationData + bboxData + end
        arcpy.AddMessage("Overpass API Query:")
        arcpy.AddMessage(query)
        response = requests.get(url,params={'data': query})
        if response.status_code!=200:
            arcpy.AddMessage("server response was " + str(response.status_code) )
            return
        try:
            data = response.json()
        except:
            arcpy.AddMessage("server responded with non JSON data: ")
            arcpy.AddError(response.text)
            return
        if len(data["elements"]) == 0:
            arcpy.AddMessage("No data found!")
            return
        else:
            arcpy.AddMessage("collected " + str(len(data["elements"])) + " objects (incl. reverse objects)")
        arcpy.env.overwriteOutput = True
        arcpy.env.addOutputsToMap = True
        ###determine sorts of feature classes:
        def createFieldArray(element, array):
            for tag in element["tags"]:
                if tag not in array:
                    array.append(tag)
            return array
        import time
        time =  int(time.time())
        ########################################################
        ###creating feature classes according to the response###
        ########################################################
        pointsCreated = False
        linesCreated = False
        polygonsCreated = False
        for element in data['elements']:
            if element["type"]=="node" and pointsCreated == 0 and "tags" in element:
                nodesFCName = "Points_" + str(time)
                nodeFields = []
                nodesFC = arcpy.CreateFeatureclass_management(arcpy.env.scratchWorkspace, nodesFCName, "POINT", "", "DISABLED", "DISABLED", arcpy.SpatialReference(4326), "")
                for element in data['elements']:
                    if element["type"]=="node":
                    ###some elements don't have tags.
                        if "tags" in element:
                            nodeFields = createFieldArray(element, nodeFields)
                arcpy.AddField_management(nodesFC,"OSM_ID", "DOUBLE", 12,0, "",  "OSM_ID")
                for tag in nodeFields:
                    try:
                        arcpy.AddField_management(nodesFC, tag.replace(":", ""), "STRING", 255, "", "",  tag.replace(":", "_"), "NULLABLE")
                        arcpy.AddMessage("adding field " + tag + " to point shapefile")
                    except:
                        arcpy.AddMessage("adding field " + tag + " failed")
                pointsCreated = True
                arcpy.AddMessage("point shapefile created")
                rowsNodesFC = arcpy.InsertCursor(nodesFC)
            if (element["type"]=="way" and linesCreated == 0 and (element["nodes"][0] != element["nodes"][len(element["nodes"])-1])) and "tags" in element:
                waysFCName = "Lines_" + str(time)
                wayFields = []
                waysFC = arcpy.CreateFeatureclass_management(arcpy.env.scratchWorkspace, waysFCName, "POLYLINE", "", "DISABLED", "DISABLED", arcpy.SpatialReference(4326), "")
                for element in data['elements']:
                    if element["type"]=="way" and element["nodes"][0] != element["nodes"][len(element["nodes"])-1]:
                        if "tags" in element:
                            wayFields = createFieldArray(element, wayFields)
                arcpy.AddField_management(waysFC,"OSM_ID", "DOUBLE", 12,0, "",  "OSM_ID")
                for tag in wayFields:
                    try:
                        arcpy.AddField_management(waysFC, tag.replace(":", ""), "STRING", 255, "", "",  tag.replace(":", "_"), "NULLABLE")
                        arcpy.AddMessage("adding field " + tag + "  to line shapefile")
                    except:
                        arcpy.AddMessage("adding field " + tag + " failed")
                linesCreated = True
                arcpy.AddMessage("line shapefile created")
                rowsWaysFC = arcpy.InsertCursor(waysFC)
            if (element["type"]=="way" and polygonsCreated == 0 and element["nodes"][0] == element["nodes"][len(element["nodes"])-1]) and "tags" in element:
                polysFCName = "Polygons_" + str(time)
                polyFields = []
                polyFC = arcpy.CreateFeatureclass_management(arcpy.env.scratchWorkspace, polysFCName, "POLYGON", "", "DISABLED", "DISABLED", arcpy.SpatialReference(4326), "")
                for element in data['elements']:
                    if element["type"]=="way" and element["nodes"][0] == element["nodes"][len(element["nodes"])-1]:
                        if "tags" in element:
                            polyFields = createFieldArray(element, polyFields)
                arcpy.AddField_management(polyFC,"OSM_ID", "DOUBLE", 12,0, "",  "OSM_ID")
                for tag in polyFields:
                    try:
                        arcpy.AddField_management(polyFC, tag.replace(":", ""), "STRING", 255, "", "",  tag.replace(":", "_"), "NULLABLE")
                        arcpy.AddMessage("adding field " + tag + "  to polygon shapefile")
                    except:
                        arcpy.AddMessage("adding field " + tag + " failed")
                polygonsCreated = True
                arcpy.AddMessage("polygon shapefile created")
                rowsPolyFC = arcpy.InsertCursor(polyFC)
        #######################################################
        ###filling feature classes according to the response###
        #######################################################
        for element in data['elements']:
            ###we deal with nodes first
            if element["type"]=="node" and "tags" in element:
                row = rowsNodesFC.newRow()
                PtGeometry = arcpy.PointGeometry(arcpy.Point(element["lon"], element["lat"]), arcpy.SpatialReference(4326))
                row.setValue("SHAPE", PtGeometry)
                row.setValue("OSM_ID", element["id"])
                for tag in element["tags"]:
                    try:
                        row.setValue(tag.replace(":", ""), element["tags"][tag])
                    except:
                        arcpy.AddMessage("adding value failed")
                rowsNodesFC.insertRow(row)
                del row
            if element["type"]=="way" and "tags" in element:
                ### getting needed Node Geometries:
                nodes = element["nodes"]
                nodeGeoemtry = []
                ### finding nodes in reverse mode
                for node in nodes:
                    for NodeElement in data['elements']:
                        if NodeElement["id"] == node:
                            nodeGeoemtry.append(arcpy.Point(NodeElement["lon"],NodeElement["lat"]))
                            break
                if nodes[0]==nodes[len(nodes)-1]:
                    arcpy.AddMessage("treating way as polygon")
                    row = rowsPolyFC.newRow()
                    pointArray = arcpy.Array(nodeGeoemtry)
                    row.setValue("SHAPE", pointArray)
                    row.setValue("OSM_ID", element["id"])
                    ###now deal with the way tags:
                    if "tags" in element:
                        for tag in element["tags"]:
                            try:
                                row.setValue(tag.replace(":", ""), element["tags"][tag])
                            except:
                                arcpy.AddMessage("adding value failed")
                    rowsPolyFC.insertRow(row)
                    del row
                else: #lines have different start end endnodes:
                    arcpy.AddMessage("treating way as polyline")
                    row = rowsWaysFC.newRow()
                    pointArray = arcpy.Array(nodeGeoemtry)
                    row.setValue("SHAPE", pointArray)
                    row.setValue("OSM_ID", element["id"])
                    ###now deal with the way tags:
                    if "tags" in element:
                        for tag in element["tags"]:
                            try:
                                row.setValue(tag.replace(":", ""), element["tags"][tag])
                            except:
                                arcpy.AddMessage("adding value failed")
                    rowsWaysFC.insertRow(row)
                    del row
        import os
        if pointsCreated == True:
            del rowsNodesFC
            parameters[5].value = arcpy.env.scratchWorkspace + os.sep + nodesFCName
        if linesCreated == True:
            del rowsWaysFC
            parameters[6].value = arcpy.env.scratchWorkspace + os.sep + waysFCName
        if polygonsCreated == True:
            del rowsPolyFC
            parameters[7].value = arcpy.env.scratchWorkspace + os.sep + polysFCName
        return
