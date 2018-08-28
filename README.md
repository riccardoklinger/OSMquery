# OSMquery
Query OSM data for defined key-value pairs (tags) and an area of interest and add the results to your ArcGIS project as feature layers. The tool is supposed to work using ArcGIS Pro and ArcGIS Desktop 10.x.

## Installation
Download this repository (and unzip, if necessary). Either navigate to it in ArcGIS Pro or ArcMap using the "Connect to Folder" function in the ArcCatalog window or add it using the "Add Toolbox" function. Only from within ArcGIS Pro or ArcMap you can restrict the area of interest to the map extent in your display. Running the tool from ArcCatalog you can use any of the other options for specifying your area of interest.

![Toolbox in ArcGIS Pro](https://i.imgur.com/UU2S2QU.png)

## Usage
OSM tags like, for example, `amenity=bakery` consist of a key (in the example: `amenity`) and a value (in the example: `bakery`). In the tool, select a key and value pair for which OSM should be queried for features. In each run of the tool, you can use only one key but you can use one or several values. For example, you can query only for `amenity=atm` or you can query for both `amenity=atm` and `amenity=bank` in one run of the tool. If you chose to do the latter, the results for different tags (or more specifically: OSM values) are summarized into one feature class per geometry type.

The tool will add all tags that occur in the features found in OSM as attributes (fields) and their values. The OSM tag keys become attribute names, the OSM tag values become attribute values.

For defining the spatial extent of your query you can use two options: You can either enter an area name (which will be geocoded using the OSM-based geocoding service [Nominatim](https://nominatim.openstreetmap.org/search)) or you can define a bounding box using coordinates in the [EPSG 4326](https://epsg.io/4326) (also known as WGS 1984) spatial reference system. If you take the latter route you can e.g. use the option *Same as Display*, but in this case make sure that your data frame is in [EPSG 4326](https://epsg.io/4326) before opening the tool.

After the tool has run successfully, the results will be drawn on the map in up to three feature layers (one each for point features, line features, and polygon features) and the respective feature classes will be stored in your Scratch Workspace (`arcpy.env.scratchWorkspace`). 

![results in ArcGIS Pro](https://i.imgur.com/voTjY0S.png)

## Credits
All OSM data you obtain through this tool are, of course, [&copy; OSM contributors](https://www.openstreetmap.org/copyright).
