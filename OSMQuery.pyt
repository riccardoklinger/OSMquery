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
        contributors         : Riccardo Klinger, Ralph Straumann, Michael Marz
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
try:
    # For Python 3.0 and later
    from urllib.request import Request, urlopen, quote
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import Request, urlopen, quote
import json
import time
import datetime
import random
from os.path import dirname, join, abspath

# Constants for building the query to an Overpass API
QUERY_START = "[out:json][timeout:60]"
QUERY_DATE = '[date:"timestamp"];('
QUERY_END = ');(._;>;);out;>;'

# Set some environment settings
arcpy.env.overwriteOutput = True
arcpy.env.addOutputsToMap = True


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "OSM Query Toolbox"
        self.alias = "OSMQueryToolbox"

        # List of tool classes associated with this toolbox
        self.tools = [GetOSMDataSimple, GetOSMDataExpert]
    @classmethod
    def get_server_URL(self):
        """Load the configuration file and find Overpass API endpoints"""
        # Load JSON file with configuration info
        json_file = join(dirname(abspath(__file__)), 'config/servers.json')
        try:
            with open(json_file) as f:
                config_json = json.load(f)
        except IOError:
            arcpy.AddError('Configuration file %s not found.' % json_file)
        except ValueError:
            arcpy.AddError('Configuration file %s is not valid JSON.' %
                           json_file)
        return random.choice(config_json["overpass_servers"])
    @classmethod
    def create_result_fc(cls, geometry_type, fields, timestamp):
        fc_name = '%ss_%s' % (geometry_type, str(timestamp))
        fc = join(arcpy.env.scratchWorkspace, fc_name)

        arcpy.AddMessage("\nCreating %s feature layer %s..." %
                         (geometry_type.lower(), fc_name))
        if geometry_type == 'Line':
            geometry_type = 'Polyline'
        arcpy.CreateFeatureclass_management(arcpy.env.scratchWorkspace,
                                            fc_name, geometry_type.upper(),
                                            "", "DISABLED", "DISABLED",
                                            arcpy.SpatialReference(4326), "")
        arcpy.AddMessage("\tAdding attribute OSM_ID...")
        arcpy.AddField_management(fc, "OSM_ID", "DOUBLE", 12, 0, "", "OSM_ID")
        arcpy.AddMessage("\tAdding attribute DATETIME...")
        arcpy.AddField_management(fc, "DATETIME", "DATE", "", "", "",
                                  "DateTime")
        for field in fields:
            try:
                field = field.replace(":", "")
                if field[0].isdigit():
                    field = "_" + field
                arcpy.AddMessage("\tAdding attribute %s..." % field)
                arcpy.AddField_management(fc, field, "STRING", 255, "", "",
                                          field, "NULLABLE")
            except arcpy.ExecuteError as error:
                arcpy.AddError(error)
                arcpy.AddError("\tAdding attribute %s failed.")
        return fc

    @classmethod
    def extract_features_from_json(cls, data):
        """Extract lists of point, line, polygon objects from an Overpass API
        response JSON object"""
        points = [e for e in data['elements'] if e["type"] == "node"]
        lines = [e for e in data['elements'] if e["type"] == "way" and
                 (e["nodes"][0] != e["nodes"][len(e["nodes"])-1])]
        polygons = [e for e in data['elements'] if e["type"] == "way" and
                    (e["nodes"][0] == e["nodes"][len(e["nodes"])-1])]
        return points, lines, polygons

    @classmethod
    def get_attributes_from_features(cls, features):
        fc_fields = set()
        for element in [e for e in features if "tags" in e]:
            for tag in element["tags"]:
                fc_fields.add(tag)
        return fc_fields

    @classmethod
    def fill_feature_classes(cls, data, request_time, geoOnly):
        fcs = [None, None, None]

        # ------------------------------------------------------
        # Creating feature classes according to the response
        # ------------------------------------------------------

        # Extract geometries (if present) from JSON data: points (nodes),
        # lines (open ways; i.e. start and end node are not identical) and
        # polygons (closed ways)
        points, lines, polygons = Toolbox.extract_features_from_json(data)

        # Per geometry type, gather all atributes present in the data
        # through elements per geometry type and collect their attributes
        # if user wants to get all the attributes
        if geoOnly == False:
            point_fc_fields = Toolbox.get_attributes_from_features(points)
            line_fc_fields = Toolbox.get_attributes_from_features(lines)
            polygon_fc_fields = Toolbox.get_attributes_from_features(polygons)
        else:
            point_fc_fields = []
            line_fc_fields = []
            polygon_fc_fields = []
        # Per geometry type, create a feature class if there are features in
        # the data
        timestamp = int(time.time())
        if len(points) > 0:
            point_fc = Toolbox.create_result_fc('Point', point_fc_fields,
                                                timestamp)
            point_fc_cursor = arcpy.InsertCursor(point_fc)
            fcs[0] = point_fc
        else:
            arcpy.AddMessage("\nData contains no point features.")

        if len(lines) > 0:
            line_fc = Toolbox.create_result_fc('Line', line_fc_fields,
                                               timestamp)
            line_fc_cursor = arcpy.InsertCursor(line_fc)
            fcs[1] = line_fc
        else:
            arcpy.AddMessage("\nData contains no line features.")

        if len(polygons) > 0:
            polygon_fc = Toolbox.create_result_fc('Polygon', polygon_fc_fields,
                                               timestamp)
            polygon_fc_cursor = arcpy.InsertCursor(polygon_fc)
            fcs[2] = polygon_fc
        else:
            arcpy.AddMessage("\nData contains no polygon features.")

        # ------------------------------------------------------
        # Filling feature classes according to the response
        # ------------------------------------------------------

        for element in data['elements']:
            # Deal with nodes first
            try:
                if element["type"] == "node" and "tags" in element:
                    row = point_fc_cursor.newRow()
                    point_geometry = \
                        arcpy.PointGeometry(arcpy.Point(element["lon"],
                                                        element["lat"]),
                                            arcpy.SpatialReference(4326))
                    row.setValue("SHAPE", point_geometry)
                    row.setValue("OSM_ID", element["id"])
                    row.setValue("DATETIME", request_time)
                    if not geoOnly:
                        for tag in element["tags"]:
                            try:
                                if tag[0].isdigit():
                                    row.setValue("_" + tag.replace(":", ""),
                                             element["tags"][tag])
                                else:
                                    row.setValue(tag.replace(":", ""),
                                             element["tags"][tag])
                            except:
                                arcpy.AddMessage("Adding value failed.")
                    point_fc_cursor.insertRow(row)
                    del row
                if element["type"] == "way" and "tags" in element:
                    # Get needed node geometries:
                    nodes = element["nodes"]
                    node_geometry = []
                    # Find nodes in reverse mode
                    for node in nodes:
                        for NodeElement in data['elements']:
                            if NodeElement["id"] == node:
                                node_geometry.append(
                                        arcpy.Point(NodeElement["lon"],
                                                    NodeElement["lat"]))
                                break
                    if nodes[0] == nodes[len(nodes) - 1]:
                        row = polygon_fc_cursor.newRow()
                        pointArray = arcpy.Array(node_geometry)
                        row.setValue("SHAPE", pointArray)
                        row.setValue("OSM_ID", element["id"])
                        row.setValue("DATETIME", request_time)
                        # Now deal with the way tags:
                        if not geoOnly:
                            if "tags" in element:
                                for tag in element["tags"]:
                                    try:
                                        if tag[0].isdigit():
                                            row.setValue("_" + tag.replace(":", ""),
                                                     element["tags"][tag])
                                        else:
                                            row.setValue(tag.replace(":", ""),
                                                     element["tags"][tag])
                                    except:
                                        arcpy.AddMessage("Adding value failed.")
                        polygon_fc_cursor.insertRow(row)
                        del row
                    else:  # lines have different start end endnodes:
                        row = line_fc_cursor.newRow()
                        pointArray = arcpy.Array(node_geometry)
                        row.setValue("SHAPE", pointArray)
                        row.setValue("OSM_ID", element["id"])
                        row.setValue("DATETIME", request_time)
                        # now deal with the way tags:
                        if not geoOnly:
                            if "tags" in element:
                                for tag in element["tags"]:
                                    try:
                                        if tag[0].isdigit():
                                            row.setValue("_" + tag.replace(":", ""),
                                                     element["tags"][tag])
                                        else:
                                            row.setValue(tag.replace(":", ""),
                                                     element["tags"][tag])
                                    except:
                                        arcpy.AddMessage("Adding value failed.")
                        line_fc_cursor.insertRow(row)
                        del row
            except:
                arcpy.AddWarning("OSM element %s could not be written to FC" %
                                 element["id"])
        if fcs[0]:
            del point_fc_cursor
        if fcs[1]:
            del line_fc_cursor
        if fcs[2]:
            del polygon_fc_cursor
        return fcs

    @classmethod
    def set_spatial_reference(cls, srs, transformation):
        """Given a Spatial Reference System string and (potentially) a
        transformation, create an arcpy.SpatialReference object and (if given)
        set the geographic transformation in the environment settings."""
        if srs is not None:
            spatial_reference = arcpy.SpatialReference()
            spatial_reference.loadFromString(srs)
        else:
            spatial_reference = arcpy.SpatialReference(4326)
        if transformation is not None:
            arcpy.env.geographicTransformations = transformation
        return spatial_reference

    @classmethod
    def get_bounding_box(cls, extent_indication_method, region_name, extent):
        """ Given a method for indicating the extent to be queried and either
        a region name or an extent object, construct the string with extent
        information for querying the Overpass API"""
        if extent_indication_method == "Define a bounding box":
            if extent.spatialReference == arcpy.SpatialReference(4326):
                # No reprojection necessary for EPSG:4326 coordinates
                bounding_box = [extent.YMin, extent.XMin, extent.YMax,
                                extent.XMax]
            else:
                # The coordinates of the extent object need to be reprojected
                # to EPSG:4326 for query building
                ll = arcpy.PointGeometry(arcpy.Point(extent.XMin, extent.YMin),
                                         extent.spatialReference).projectAs(
                        arcpy.SpatialReference(4326))
                ur = arcpy.PointGeometry(arcpy.Point(extent.XMax, extent.YMax),
                                         extent.spatialReference).projectAs(
                        arcpy.SpatialReference(4326))
                bounding_box = [ll.extent.YMin, ll.extent.XMin, ur.extent.YMax,
                                ur.extent.XMax]
            return '', '(%s);' % ','.join(str(e) for e in bounding_box)

        elif extent_indication_method == "Geocode a region name":
            # Get an area ID from Nominatim geocoding service
            NOMINATIM_URL = 'https://nominatim.openstreetmap.org/search?q=' \
                            '%s&format=json' % region_name
            arcpy.AddMessage("\nGecoding region using Nominatim: %s..." %
                             NOMINATIM_URL)
            nominatim_response = urlopen(NOMINATIM_URL)
            try:
                nominatim_data = json.loads(nominatim_response.read().decode("utf-8"))
                arcpy.AddMessage(nominatim_data)
                for result in nominatim_data:
                    if result["osm_type"] == "relation":
                        nominatim_area_id = result['osm_id']
                        try:
                            arcpy.AddMessage("\tFound region %s" %
                                             result['display_name'])
                        except:
                            arcpy.AddMessage("\tFound region %s" %
                                             nominatim_area_id)
                        break
                bounding_box_head = 'area(%s)->.searchArea;' % \
                                    (int(nominatim_area_id) + 3600000000)
                bounding_box_data = '(area.searchArea);'
                return bounding_box_head, bounding_box_data
            except:
                arcpy.AddError("\tNo region found!")
                return '', ''
        else:
            raise ValueError


class GetOSMDataSimple(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Get OSM Data"
        self.description = "Get OpenStreetMap data using relatively simple, " \
                           "pre-formulated queries to the Overpass API"
        self.canRunInBackground = False

    def get_config(self, config_item):
        """Load the configuration file and find either major OSM tag keys or
        suitable OSM tag values for a given key"""
        # Load JSON file with configuration info
        json_file = join(dirname(abspath(__file__)), 'config/tags.json')
        try:
            with open(json_file ) as f:
                config_json = json.load(f)
        except IOError:
            arcpy.AddError('Configuration file %s not found.' % json_file)
        except ValueError:
            arcpy.AddError('Configuration file %s is not valid JSON.' %
                           json_file)
        # Compile a list of all major OSM tag keys
        if config_item == "all":
            return sorted([key for key in config_json])
        # Compile a list of all major OSM tag values for the given OSM tag key
        else:
            return sorted([value for value in config_json[config_item]])

    def getParameterInfo(self):
        """Define parameter definitions for the ArcGIS toolbox"""
        param0 = arcpy.Parameter(
                displayName="OSM tag key",
                name="in_tag",
                datatype="GPString",
                parameterType="Required",
                direction="Input")
        param0.filter.list = self.get_config('all')
        param0.value = param0.filter.list[0]
        param1 = arcpy.Parameter(
                displayName="OSM tag value",
                name="in_key",
                datatype="GPString",
                parameterType="Required",
                direction="Input",
                multiValue=True)
        param2 = arcpy.Parameter(
                displayName="Spatial extent indication method",
                name="in_regMode",
                datatype="GPString",
                parameterType="Required",
                direction="Input")
        param2.filter.list = ["Geocode a region name", "Define a bounding box"]
        param2.value = "Define a bounding box"
        param3 = arcpy.Parameter(
                displayName="Region name",
                name="in_region",
                datatype="GPString",
                parameterType="Optional",
                direction="Input")
        param4 = arcpy.Parameter(
                displayName="Bounding box",
                name="in_bbox",
                datatype="GPExtent",
                parameterType="Optional",
                direction="Input",
                enabled=False)
        param5 = arcpy.Parameter(
                displayName="Output CRS",
                name="in_crs",
                datatype="GPCoordinateSystem",
                parameterType="Optional",
                category="Adjust the CRS of the result data - default is "
                         "EPSG:4326 (WGS 1984):",
                direction="Input")
        param5.value = arcpy.SpatialReference(4326)
        param6 = arcpy.Parameter(
                displayName="Transformation",
                name="in_transformation",
                datatype="GPString",
                parameterType="Optional",
                category="Adjust the CRS of the result data - default is "
                         "EPSG:4326 (WGS 1984):",
                direction="Input",
                enabled=False)
        param7 = arcpy.Parameter(
                displayName="Reference date/time UTC",
                name="in_date",
                datatype="GPDate",
                parameterType="Optional",
                direction="Input")
        param7.value = datetime.datetime.utcnow()
        param8 = arcpy.Parameter(
                displayName="Save Coordinates only",
                name="in_coordsOnly",
                datatype="GPBoolean",
                parameterType="Optional",
                direction="Input")

        param_out0 = arcpy.Parameter(
                displayName="Layer containing OSM point data",
                name="out_nodes",
                datatype="GPFeatureLayer",
                parameterType="Derived",
                direction="Output")
        param_out1 = arcpy.Parameter(
                displayName="Layer containing OSM line data",
                name="out_ways",
                datatype="GPFeatureLayer",
                parameterType="Derived",
                direction="Output")
        param_out2 = arcpy.Parameter(
                displayName="Layer containing OSM polygon data",
                name="out_poly",
                datatype="GPFeatureLayer",
                parameterType="Derived",
                direction="Output")

        return [param0, param1, param2, param3, param4, param5, param6,
                param7, param8, param_out0, param_out1, param_out2]

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, params):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""

        # Update the parameters of keys accroding the values of "in_tag"
        params[1].filter.list = self.get_config(params[0].value)

        # Switch the availability of the 'region name' parameter and the
        # 'extent' parameter depending on which extent indication method is
        # selected
        if params[2].value == "Geocode a region name":
            params[3].enabled = True
            params[4].enabled = False
        else:
            params[3].enabled = False
            params[4].enabled = True

        if params[5].value is not None:
            target_sr = arcpy.SpatialReference()
            # target_sr.loadFromString(params[5].value).exportToString())
            target_sr.loadFromString(params[5].value)
            # If necessary, find candidate transformations between EPSG:4326
            # and <target_sr> and offer them in the dropdown menu
            if target_sr.factoryCode != 4326:
                params[6].enabled = True
                params[6].filter.list = arcpy.ListTransformations(
                        arcpy.SpatialReference(4326), target_sr)
                params[6].value = params[6].filter.list[0]
            if target_sr.factoryCode == 4326:
                params[6].enabled = False
        return

    def updateMessages(self, params):
        """Modify the messages created by internal validation for each tool
        parameter. This method is called after internal validation."""
        # If only time is selected, year will be autofilled with "1899"
        earliest_date = datetime.datetime(2004, 8, 9, 0, 0)
        if params[7].value < earliest_date:
            params[7].setWarningMessage("No or invalid date provided. The "
                                        "date to be queried must be "
                                        "2004-08-09 (9 August 2004) or later.")
        return

    def execute(self, params, messages):
        """The code that is run, when the ArcGIS tool is run."""

        query_date = QUERY_DATE.replace("timestamp", params[7].value.strftime(
                "%Y-%m-%dT%H:%M:%SZ"))

        # Create the spatial reference and set the geographic transformation
        # in the environment settings (if given)
        sr = Toolbox.set_spatial_reference(params[5].value, params[6].value)

        # Get the bounding box-related parts of the Overpass API query, using
        # the indicated extent or by geocoding a region name given by the user
        bbox_head, bbox_data = Toolbox.get_bounding_box(params[2].value,
                                                        params[3].value,
                                                        params[4].value)

        # Get the list of OSM tag values checked by the user. The tool makes
        # the user supply at least one key.
        tag_key = params[0].value
        tag_values = params[1].value.exportToString().split(";")

        # If the wildcard (*) option is selected, replace any other tag value
        # that might be selected
        if "'* (any value, including the ones listed below)'" in tag_values:
            arcpy.AddMessage("\nCollecting " + tag_key + " = * (any value)")
            node_data = 'node["' + tag_key + '"]'
            way_data = 'way["' + tag_key + '"]'
            relation_data = 'relation["' + tag_key + '"]'
        # Query only for one tag value
        elif len(tag_values) == 1:
            tag_value = tag_values[0]
            arcpy.AddMessage("\nCollecting " + tag_key + " = " + tag_value)
            node_data = 'node["' + tag_key + '"="' + tag_value + '"]'
            way_data = 'way["' + tag_key + '"="' + tag_value + '"]'
            relation_data = 'relation["' + tag_key + '"="' + tag_value + '"]'
        # Query for a combination of tag values
        elif len(tag_values) > 1:
            tag_values = "|".join(tag_values)
            arcpy.AddMessage("\nCollecting " + tag_key + " = " + tag_values)
            node_data = 'node["' + tag_key + '"~"' + tag_values + '"]'
            way_data = 'way["' + tag_key + '"~"' + tag_values + '"]'
            relation_data = 'relation["' + tag_key + '"~"' + tag_values + '"]'

        query = (QUERY_START + query_date + bbox_head +
                 node_data + bbox_data +
                 way_data + bbox_data +
                 relation_data + bbox_data +
                 QUERY_END)

        arcpy.AddMessage("Issuing Overpass API query:")
        arcpy.AddMessage(query)
        # Get the server to use from the config:
        QUERY_URL = Toolbox.get_server_URL()
        arcpy.AddMessage("Server used for the query:")
        arcpy.AddMessage(QUERY_URL)
        q = Request(QUERY_URL)
        q.add_header("User-Agent", "OSMquery/https://github.com/riccardoklinger/OSMquery")
        response = urlopen(q, query.encode('utf-8'))

        #response = requests.get(QUERY_URL, params={'data': query})
        if response.getcode() != 200:
            arcpy.AddMessage("\tOverpass server response was %s" %
                             response.getcode())
            return
        try:
            #data = response.json()
            data = json.loads(response.read())
        except:
            arcpy.AddMessage("\tOverpass API responded with non JSON data: ")
            arcpy.AddError(response.read())
            return
        if len(data["elements"]) == 0:
            arcpy.AddMessage("\tNo data found!")
            return
        else:
            arcpy.AddMessage("\tCollected %s objects (including reverse "
                             "objects)" % len(data["elements"]))

        result_fcs = Toolbox.fill_feature_classes(data, params[7].value, params[8].value)
        if result_fcs[0]:
            params[9].value = result_fcs[0]
        if result_fcs[1]:
            params[10].value = result_fcs[1]
        if result_fcs[2]:
            params[11].value = result_fcs[2]
        return


class GetOSMDataExpert(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Get OSM Data (Expert Tool)"
        self.description = "Get OpenStreetMap data using fully customizable " \
                           "queries to the Overpass API"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
                displayName="Overpass Query",
                name="in_query",
                datatype="GPString",
                parameterType="Required",
                direction="Input"
        )
        param0.value = 'node(47.158,102.766,47.224,102.923);'
        param1 = arcpy.Parameter(
                displayName="Reference date/time UTC",
                name="in_date",
                datatype="GPDate",
                parameterType="Optional",
                direction="Input",
        )
        now = datetime.datetime.utcnow()
        param1.value = now.strftime("%d.%m.%Y %H:%M:%S")
        param_out0 = arcpy.Parameter(
                displayName="Layer containing OSM point data",
                name="out_nodes",
                datatype="GPFeatureLayer",
                parameterType="Derived",
                direction="Output"
        )
        param_out1 = arcpy.Parameter(
                displayName="Layer containing OSM line data",
                name="out_ways",
                datatype="GPFeatureLayer",
                parameterType="Derived",
                direction="Output"
        )
        param_out2 = arcpy.Parameter(
                displayName="Layer containing OSM polygon data",
                name="out_poly",
                datatype="GPFeatureLayer",
                parameterType="Derived",
                direction="Output"
        )
        return [param0, param1, param_out0, param_out1, param_out2]


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


    def execute(self, params, messages):
        """The source code of the tool."""
        # Get data using urllib

        query_date = QUERY_DATE.replace("timestamp", params[1].value.strftime(
                "%Y-%m-%dT%H:%M:%SZ"))
        query = (QUERY_START + query_date + params[0].valueAsText +
                 QUERY_END)
        arcpy.AddMessage("Issuing Overpass API query:")
        arcpy.AddMessage(query)
        # Get the server to use from the config:
        QUERY_URL = Toolbox.get_server_URL()
        arcpy.AddMessage("Server used for the query:")
        arcpy.AddMessage(QUERY_URL)
        q = Request(QUERY_URL)
        q.add_header("User-Agent", "OSMquery/https://github.com/riccardoklinger/OSMquery")
        response = urlopen(q, query.encode('utf-8'))
        if response.getcode() != 200:
            arcpy.AddMessage("\tOverpass server response was %s" %
                             response.getcode())
            return
        try:
            data = json.loads(response.read())
        except:
            arcpy.AddMessage("\tOverpass API responded with non JSON data: ")
            arcpy.AddError(response.read())
            return
        if len(data["elements"]) == 0:
            arcpy.AddMessage("\tNo data found!")
            return
        else:
            arcpy.AddMessage("\nData contains no polygon features.")
        arcpy.AddMessage("\tCollected %s objects (including reverse objects)" %
                         len(data["elements"]))

        result_fcs = Toolbox.fill_feature_classes(data, params[1].value, True)
        if result_fcs[0]:
            params[2].value = result_fcs[0]
        if result_fcs[1]:
            params[3].value = result_fcs[1]
        if result_fcs[2]:
            params[4].value = result_fcs[2]
        return
