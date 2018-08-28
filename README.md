# OSMquery
Query OSM data and add results to your ArcGIS project. The tool is supposed to work using ArcGIS Pro and ArcGIS Desktop 10.x (ArcMap).
## Installation
Download this repo and place it somewhere. Either add it using the "Connect to folder" function in ArcCatalog (or the ArcCatalog window within ArcMap) or add it using the "Add Toolbox" function.

![Toolbox in ArcGIS Pro](https://i.imgur.com/UU2S2QU.png)

## Usage
OSM tags like, for example, `amenity=bakery` consist of keys (in the example: `amenity`) and values (in the example: `bakery`). In the tool, select a key and value pair for which OSM features should be queried. Per run of the tool, you can use only one key but you can use several values. For example, you could query for `amenity=atm` and `amenity=bank` in one run of the tool. If you chose to do this, the results are summarized in one feature class per geometry type.

The tool will add all tags that occur in the features found in OSM as attributes (fields) and their values. The OSM tag keys become attribute names, the OSM tag values become attribute values.

For defining the spatial extent of your query you can use two options: You can either enter an area name (which will be geocoded using [Nominatim](https://nominatim.openstreetmap.org/search)) or define a bounding box using coordinates given in the [EPSG 4326](https://epsg.io/4326) (also known as WGS 1984) spatial reference system. If you take the latter route and want to use the option *Same as Display* make sure that your data frame is in [EPSG 4326](https://epsg.io/4326).

After the tool has run successfully, the results will be drawn on the map in up to three feature layers (one each for point features, line features, and polygon features) and the respective feature classes will be stored in your `arcpy.env.scratchWorkspace`.

![results in ArcGIS Pro](https://i.imgur.com/voTjY0S.png)

## Credits
All OSM data you obtain through this tool are, of course, [&copy; OSM contributors](https://www.openstreetmap.org/copyright).