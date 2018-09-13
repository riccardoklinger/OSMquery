# OSMQuery
OSMQuery is a [Python Toolbox](https://pro.arcgis.com/en/pro-app/arcpy/geoprocessing_and_python/a-quick-tour-of-python-toolboxes.htm) for making it easy (easier) to get data out of [OpenStreetMap (OSM)](https://wiki.openstreetmap.org) and into the Esri ecosystem. With OSMQuery, you can query an area of interest for OSM data (of specified kind) and obtain feature layers of the results, with point, line and/or area features depending on what kind of data OSM holds for your area. This toolbox works both in ArcGIS Pro and in ArcGIS Desktop 10.x.

## Contents and Usage
The OSMQuery toolbox comes with two tools:
- **Get OSM Data**: With this tool, you can query pre-defined (frequent) combinations of OSM tag keys (e.g. `amenity`) and OSM tag values (e.g. `atm`, `bench` or `fountain`) and obtain the results as feature layers. For a given OSM tag key, you can query several OSM tag values at once. Or you can even use the wildcard operator (*) in order to get feature with *any* value for the chosen OSM tag key.  
- **Get OSM Data (Expert Tool)**: With this tool, you can formulate your own queries and obtain the results as feature layers. Behind the scenes, the tool uses the [OSM Overpass API](https://wiki.openstreetmap.org/wiki/Overpass_API). Thus, your query syntax has to be compliant with the [Overpass API Language](https://wiki.openstreetmap.org/wiki/Overpass_API/Language_Guide).

What OSMQuery looks like in ArcMap:

![OSMQuery Toolbox structure in ArcMap](https://github.com/riccardoklinger/OSMquery/blob/master/docs/OSMQuery-in-ArcMap.png)

What the *Get OSM Data* tool of OSMQuery looks like in ArcMap:

![Get OSM Data tool GUI in ArcMap](https://github.com/riccardoklinger/OSMquery/blob/master/docs/OSMQuery-GUI-in-ArcMap.png)

And the same Toolbox in ArcGIS Pro:

![Toolbox in ArcGIS Pro](https://i.imgur.com/oSshKHE.png)

## Installation
Download this repository (and unzip, if necessary). Either navigate to it in ArcGIS Pro or ArcMap using the "Connect to Folder" function in the ArcCatalog window or add it using the "Add Toolbox" function. Only from within ArcGIS Pro or ArcMap you can restrict the area of interest to the map extent in your display. Running the tool from ArcCatalog you can use any of the other options for specifying your area of interest.

## Prerequisites
Apart from the core Python modules `datetime`, `json`, `time` and `os`, OSMQuery requires `arcpy` (of course) and `requests` to be installed. Depending on your Python version and environment you may or may not have `requests` installed already. You can test this, for example, by opening a Windows command prompt, starting Python (type `python`) and entering `import requests`. If your command prompt looks like this:

`>>> import requests`

`>>>`

you're all set. If an import error is displayed, you have to [install the Python `requests` module](http://docs.python-requests.org/en/master/user/install/) before using OSMQuery.

## More Details on Usage 
### Querying OSM Tags
OSM tags like, for example, `amenity=bakery` consist of a key (in the example: `amenity`) and a value (in the example: `bakery`). In the `Get OSM Data` tool for simple queries, select a key and value(s) pair for which OSM should be queried for features. In each run of the tool, you can use only one key but you can use one or several values. For example, you can query only for `amenity=atm` or you can query for both `amenity=atm` and `amenity=bank` in one run of the tool. If you chose to do the latter, the results for different tags (or more specifically: OSM values) are summarized into one feature class per geometry type.

### Handling of Data Models (OSM Tag Key-Value Pairs)
Both tools, `Get OSM Data` and `Get OSM Data (Expert Tool)`, will add all tags that occur in the features found in OSM as attributes (fields) as well as their values. The OSM tag keys become attribute names, the OSM tag values become attribute values. Specifically, in the case of querying multiple OSM tag values at once, e.g. `amenity=atm` and `amenity=bank`, your resulting feature layers will obtain the 'union' of the data models of the individual queries. In the example of `amenity=atm` and `amenity=bank` your resulting feature layer might have both the attributes `currencies` and `opening_hours`, where the former is only filled for ATMs and the latter is only filled for banks.

### Defining an Area of Interest
For defining the spatial extent of your query you can use two options: You can either enter a region name (which will be geocoded using the OSM-based geocoding service [Nominatim](https://nominatim.openstreetmap.org/search)) or you can define a bounding box using the standard ArcGIS Pro or ArcMap options, e.g. manually specifying coordinates, using the extent of a layer or the option *Same as Display*.

### Defining a Date and Time of Interest
Using the appropriate parameter you can set a reference date and time (the default is the current time). Both tools, `Get OSM Data` and `Get OSM Data (Expert Tool)`, will query OSM for the specified point in time and will only yield features that were part of OSM then. The reference date and time is given in [UTC (Cordinated Universal Time)](https://en.wikipedia.org/wiki/Coordinated_Universal_Time). 

### Working with the Resulting Data
After any of the two tools has run successfully, the results will be drawn on the map in up to three timestamped feature layers (one each for point features, line features, and polygon features). The respective feature classes will be stored in your Scratch Workspace (`arcpy.env.scratchWorkspace`). If you want to persist the results, you can export the feature layers from the table of contents of ArcGIS Pro or ArcMap (or directly from your Scratch Workspace) into new feature classes in a destination of your choosing.

![results in ArcGIS Pro](https://i.imgur.com/uEyxD2H.png)

## Limitations
Both tools in this toolbox rely on the [OSM Overpass API](https://wiki.openstreetmap.org/wiki/Overpass_API). As the size of an Overpass API query result is only known when the download of the resulting data is complete, it is not possible to give an estimate of the number of features a query yields, or the time-until-completion, during the query process. The Overpass API uses a timeout after which a query will not be completed. If you run into timeout problems consider narrowing your query thematically and/or spatially. For other limitations of the Overpass API and potential workarounds please consider the pertinent [OSM Wiki Page](https://wiki.openstreetmap.org/wiki/Overpass_API#Limitations).

## Contributors
The idea for OSMQuery was conceived and first implementations were done by [Riccardo Klinger](https://github.com/riccardoklinger) of [Esri Germany](https://www.esri.de), further contributions by [Ralph Straumann](https://github.com/rastrau) of [EBP](https://www.ebp.ch/en) and [michaelmgis](https://github.com/michaelmgis). Help us improve OSMQuery by [testing, filing bug reports, feature requests or ideas](https://github.com/riccardoklinger/OSMquery/issues). Thank you!

## License and Credits
OSMQuery is licensed under the GNU General Public License (GPL), see [LICENSE](https://github.com/riccardoklinger/OSMquery/blob/master/LICENSE).

OSMQuery relies on the [OSM Overpass API](https://wiki.openstreetmap.org/wiki/Overpass_API) which is licensed under the [GNU Affero GPL v3](https://www.gnu.org/licenses/agpl-3.0.en.html). All OSM data you obtain through this tool are, of course, [&copy; OSM contributors](https://www.openstreetmap.org/copyright).
