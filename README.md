# OSMquery
Query OSM data and add results to your ArcGIS project. The tool is supposed to work using ArcGIS Pro and ArcGIS Desktop (ArcMAP).
## Installation
Download this repo and place it somewhere. Either add it using the "connect to folder" function in ArcCatalog or add it using the "Add Toolbox" function.

![Toolbox in ArcGIS Pro](https://i.imgur.com/UU2S2QU.png)
## Usage
Select a tag and key pair. YOu can either enter an area name (which will be geocoded using [Nominatim](https://nominatim.openstreetmap.org/search)) or define a bounding box using coordinates given in the [EPSG 4326](https://epsg.io/4326).

After the finished geoprocessing, the results will be drawn on the map and three feature classes will be stored.

![results in ArcGIS Pro](https://i.imgur.com/voTjY0S.png)
