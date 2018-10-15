define(['dojo/_base/declare',
    'dojo/_base/html',
    'dojo/on',
    'dojo/_base/lang',
    'dijit/_WidgetsInTemplateMixin',
    'dojo/_base/array',
    'dojo/dom',
    "dojo/dom-style",
    'dojo/parser',
    'jimu/BaseWidget',
    'dojo/ready',
    'dojo/store/Memory',
    'dijit/form/ComboBox',
    "dijit/form/FilteringSelect",
    'dijit/registry',
    'esri/request',
    'esri/graphic',
    'esri/Color',
    "esri/InfoTemplate",
    'esri/layers/layer',
    'esri/layers/GraphicsLayer',
        "esri/symbols/SimpleMarkerSymbol",
        "esri/symbols/SimpleLineSymbol",
        "esri/symbols/SimpleFillSymbol",
        "esri/geometry/Geometry",
        "esri/geometry/Point",
        "esri/geometry/Polyline",
        "esri/geometry/Polygon",
        'esri/SpatialReference',
        "esri/geometry/projection",
        'esri/arcgis/Portal',
	'esri/arcgis/OAuthInfo',
  'esri/IdentityManager',
    'dojo/domReady!'
],
  function(declare,
    html,
    on,
    lang,
    _WidgetsInTemplateMixin,
    array,
    dom,
    domStyle,
    parser,
    BaseWidget,
    ready,
    Memory,
    ComboBox,
    FilteringSelect,
    registry,
    esriRequest,
    //Map,
    Graphic,
    Color,
    InfoTemplate,
    Layer,
    GraphicsLayer,
    SimpleMarkerSymbol, SimpleLineSymbol, SimpleFillSymbol,
    Geometry,
    Point,
    Polyline,
    Polygon,
    SpatialReference,
    projection,
    arcgisPortal,
    OAuthInfo,
    IdentityManager
  ) {
    return declare([BaseWidget, _WidgetsInTemplateMixin], {
      baseClass: 'jimu-widget-osmquery',
      postCreate: function() {
         this.inherited(arguments);
         console.log(this.map.spatialReference);
         console.log('postCreate');
      },

      startup: function() {
        //this.proofAdministrator();
        OSMQueryWidget = this;
        OSMQueryWidget.inherited(arguments);
        //fill select box with items:
        json = new Array();
        //get current input:
        parser.parse();
        var OSMkeys= dojo.byId("osmkey");
        //registry.byId("osmkey").get('store').add({ name: "Test", id: 0 });
        //add all other items:
        keys = new Array();
        //getting configuration:
        var Configuration = this.config;
        //fill region select
        var select = registry.byId("regionalSetting");
        option1 = { value: "bbox", label: "BBOX definition", selected: false };
        option2 = { value: "region", label: "Region definition", selected: true };
        select.addOption([option1, option2]); // add all options at once as an array
        //registry.byId("regionalSetting").get('store').add({ name: "BBOX definition", id: 0 });
        //registry.byId("regionalSetting").get('store').add({ name: "Region definition", id: 1 });
        //dojo.attr("regionalSetting", "value", "BBOX definition");
        domStyle.set("extent", "visibility", "collapse");
        dojo.connect(registry.byId('regionalSetting'),'onChange',lang.hitch(this, 'regionalSettingsChanged'));

        //k = 0;
        for (key in Configuration){
          if (Configuration.hasOwnProperty(key)){

            //var select = registry.byId("regionalSetting");
            option = { value: key, label: key, selected: false };
            keys.push(option);

            //registry.byId("osmkey").get('store').add({ name: key, id: k });
            //k+=1;
          }
        }
        registry.byId("osmkey").addOption(keys);
        //dojo.attr("osmkey", "value", "shop");
        //dojo.attr("osmtag", "value", "bakery");
        this.keyHasChanged();
        this.updateExtent();
        this.locationFound = false;
        this.regionalSettingsChanged();
        this.own(on(this.map, "pan", lang.hitch(this, this.updateExtent)));
        this.own(on(this.map, "zoomEnd", lang.hitch(this, this.updateExtent)));
        this.own(on(this.map, "update-end", lang.hitch(this, this.updateExtent)));
        dojo.connect(registry.byId('osmkey'),'onChange',lang.hitch(this, 'keyHasChanged'));
        dojo.connect(registry.byId("getLocation"), "onClick", lang.hitch(this, 'getExtent'));
        //registry.byId("getLocation").on("click", this.getExtent());
        //dojo.byId("getLocation").connect("onClick", function test(){console.log("clicked")});
        //dojo.connect(dojo.byId("getLocation"), "onClick", OSMQueryWidget.getExtent(dojo.byId("region").value));

        keyStore = new Memory({data: keys}	);
        dojo.connect(registry.byId("getOSMdata"), "onClick", lang.hitch(this, 'doSearch'));
        //this.own(on(dojo.byId("getOSMdata"),	'onClick', lang.hitch(this, "doSearch")));


      },
      keyHasChanged:function() {

        var Configuration = this.config;
        //clear current combobox store
        var folderListLength = registry.byId("osmtag").options.length;
        for(var n=0; n < folderListLength; n++){

          registry.byId("osmtag").removeOption(registry.byId('osmtag').options[0]);

        };
        currentKey = registry.byId("osmkey").value;
        //tags = new Array();
        console.log(currentKey);
        for (tag in Configuration[currentKey]){
            registry.byId("osmtag").addOption([{ value: Configuration[currentKey][tag], label: Configuration[currentKey][tag], selected: false }]);
        }
      },
      regionalSettingsChanged:function(){
        //get current state:
        this.inherited(arguments);
        console.log(this.locationFound);

        regSet=registry.byId("regionalSetting").value;
        console.log(regSet);
        if (regSet == "region"){
          domStyle.set("extent", "visibility", "collapse");
          domStyle.set("regionTable", "visibility", "visible");
          if (this.locationFound == false){
            registry.byId("getOSMdata").set("disabled", true);
          } else {
            registry.byId("getOSMdata").set("disabled", false);
          }
        }
        else {
          registry.byId("getOSMdata").set("disabled", false);
          domStyle.set("regionTable", "visibility", "collapse");
          domStyle.set("extent", "visibility", "visible");
        }

      },
      getExtent:function(){
        this.inherited(arguments);
        regionString = dojo.byId("region").value;
        //console.log(regionString);
        esriConfig.defaults.io.corsEnabledServers.push("nominatim.openstreetmap.org");
          nominatimURL  = 'https://nominatim.openstreetmap.org/search?q=' + regionString + "&format=json";
          console.log(nominatimURL);
          var regionRequest = esriRequest({
            url: nominatimURL,
            disableIdentityLookup:  true,
            handleAs: "json"
            //callbackParamName: "callback"
          });
          regionRequest.then(
            function(response) {
              for(object in response){
                console.log(response[object]);
                if(response[object].osm_type == "relation"){
                  //console.log(response[object]);
                  nominatim_area_id = response[object].osm_id;
                  OSMQueryWidget.areaId = new Array();
                  OSMQueryWidget.areaId.push('area(' + String(parseInt(nominatim_area_id) + 3600000000) + ')->.searchArea;');
                  OSMQueryWidget.areaId.push('(area.searchArea);');
                  OSMQueryWidget.areaString = response[object].display_name;
                  dojo.byId("region").value = OSMQueryWidget.areaString;
                  OSMQueryWidget.locationFound = true;
                  OSMQueryWidget.regionalSettingsChanged();
                  break;
                }
              }
            }, function(error) {
            console.log("Error: ", error.message);
          }
        );
        return;
      },
      doSearch:function(){
        this.inherited(arguments);
        QUERY_START = "[out:json][timeout:60]";
        QUERY_DATE = '[date:"timestamp"];(';
        QUERY_END = ');(._;>;);out;>;';

        //getExtent if not alread assigned:
        if (registry.byId("regionalSetting").value== "bbox"){
          //console.log(dojo.byId("region").value);
          OSMQueryWidget.areaId = new Array();
          OSMQueryWidget.areaId.push("");
          OSMQueryWidget.areaId.push("(" + dojo.byId("ymin").innerHTML + "," + dojo.byId("xmin").innerHTML + "," + dojo.byId("ymax").innerHTML + "," + dojo.byId("xmax").innerHTML + ");");
          //this.createRequest.then(this.runRequest);
          //
        }
        var key = registry.byId("osmkey").value;
        var tag = registry.byId("osmtag").value;
        //convert if everything is needed
        if (tag[0]=="*"){
          selector= '["' + key + '"]';
        } else {
          selector = '["' + key + '"="' + tag + '"]';
        }
        esriConfig.defaults.io.corsEnabledServers.push("overpass-api.de");
        dataUrl  = "http://overpass-api.de/api/interpreter";
        dataJSON = '[out:json][timeout:60][date:"2018-09-16T18:48:39Z"];' + OSMQueryWidget.areaId[0];
        dataJSON += '(node' + selector + OSMQueryWidget.areaId[1];
        dataJSON += 'way' + selector + OSMQueryWidget.areaId[1];
        dataJSON += 'relation' + selector + OSMQueryWidget.areaId[1] + ');';
        dataJSON += '(._;>;);out;>;'
        this.layersRequest = esriRequest({
          url: dataUrl,
          content: {data:dataJSON},
          handleAs: "json",
          callbackParamName: "callback"
        });
        OSMQueryWidget.layersRequest.then(
          function(response) {
            if(confirm("Your Query response contains " + response.elements.length + " objects. You want to add them?")){
              //check for needed layers:
              var pointGL = null;
              var lineGL = null;
              var polyGL = null;
              for(element in response.elements){
                if(response.elements[element].type == "node"){
                  if (!pointGL){
                    pointGL = OSMQueryWidget.createPointGraphicsLayer();
                  }
                  OSMQueryWidget.createPoints(pointGL, response.elements[element])
                }
                if(response.elements[element].type == "way"){
                  path = new Array();
                  //create array of point coordinates:
                  for (node in response.elements[element].nodes){
                    for (point in response.elements){
                      if (response.elements[element].nodes[node] == response.elements[point].id){
                        path.push([response.elements[point].lon,response.elements[point].lat]);
                        break;
                      }
                    }
                  }
                  if (response.elements[element].nodes[0] != response.elements[element].nodes[response.elements[element].nodes.length - 1]){
                    if (!lineGL){
                      lineGL = OSMQueryWidget.createLineGraphicsLayer();
                    }
                    OSMQueryWidget.createLines(lineGL, response.elements[element], path)
                  }
                  else {
                    if (!polyGL){
                      polyGL = OSMQueryWidget.createPolygonGraphicsLayer();
                    }
                    OSMQueryWidget.createPolygons(polyGL, response.elements[element], path)
                  }
                }
              }
              OSMQueryWidget.map.addLayer(pointGL);
              OSMQueryWidget.map.addLayer(lineGL);
              OSMQueryWidget.map.addLayer(polyGL);
            }
        }, function(error) {
          console.log("Error: ", error.message);
        });

      },
      updateExtent:function(){
        this.inherited(arguments);
        if (this.map.extent.spatialReference.wkid != 4326){
          targetsr = new SpatialReference(4326);
          sourcesr = this.map.extent.spatialReference;
          var extentStr = "";
          LL = new Point(this.map.extent.xmin,this.map.extent.ymin, sourcesr);
          UR = new Point(this.map.extent.xmax,this.map.extent.ymax, sourcesr);
          projection.load().then(function() {
            LLProj = projection.project(LL, targetsr);
            URProj = projection.project(UR, targetsr);
            queryExtent = "(" + extentStr + ")";
            dojo.byId("ymin").innerHTML = String(Math.round(LLProj.y*10000)/10000);
            dojo.byId("xmin").innerHTML = String(Math.round(LLProj.x*10000)/10000);
            dojo.byId("ymax").innerHTML = String(Math.round(URProj.y*10000)/10000);
            dojo.byId("xmax").innerHTML = String(Math.round(URProj.x*10000)/10000);
          });
        }
      },
      createPointGraphicsLayer:function(){
        console.log("add point layer");
        pointGL = new GraphicsLayer();
        pointGL.id = "nodes";
        if (this.map.graphicsLayerIds.includes("nodes")){

          for (var j = 0; j < this.map.graphicsLayerIds.length; j++) {
            var layer = this.map.getLayer(this.map.graphicsLayerIds[j]);
            if (layer.id == "nodes") {
              this.map.removeLayer(layer);
            }
          }
        }
        return pointGL;
      },
      createLineGraphicsLayer:function(){
        console.log("add line layer");
        lineGL = new GraphicsLayer();
        lineGL.id = "lines";
        if (this.map.graphicsLayerIds.includes("lines")){

          for (var j = 0; j < this.map.graphicsLayerIds.length; j++) {
            var layer = this.map.getLayer(this.map.graphicsLayerIds[j]);
            if (layer.id == "lines") {
              this.map.removeLayer(layer);
            }
          }
        }
        return lineGL;
      },
      createPolygonGraphicsLayer:function(){
        console.log("add polygon layer");
        polyGL = new GraphicsLayer();
        polyGL.id = "polygons";
        if (this.map.graphicsLayerIds.includes("polygons")){

          for (var j = 0; j < this.map.graphicsLayerIds.length; j++) {
            var layer = this.map.getLayer(this.map.graphicsLayerIds[j]);
            if (layer.id == "polygons") {
              this.map.removeLayer(layer);
            }
          }
        }
        return polyGL;
      },
      createInfoTemplate(element){
        var attr = element.tags;
        for (key in attr){
            if (key.indexOf(":")>0){
              attr[key.replace(":","_")] = attr[key];
              delete attr[key];
            }
        }
        infoText = "";
        for (key in attr){
          infoText += key + ":" + "${" + key + "}<br>";
        }
        var infoTemplate = new InfoTemplate();
        infoTemplate.title = "Attributes";
        infoTemplate.content = infoText;
        return [attr, infoTemplate]
      },
      createPoints:function(gl, element){
        if (element.tags){
          attr = this.createInfoTemplate(element);
          s = new SimpleMarkerSymbol().setSize(10).setColor(new Color(new Color([255,0,0,0.8])));
          var g = new Graphic(new Point(element.lon, element.lat), s, attr[0], attr[1]);
          pointGL.add(g);
        }
      },
      createLines:function(gl, element, path){
        //check if polygon:

        attr = this.createInfoTemplate(element);
        s = new SimpleLineSymbol().setWidth(5).setColor(new Color(new Color([255,255,0,0.8])));

        //loop over the nodes:

        var g = new Graphic(new Polyline(
          {
            hasZ: false,
            hasM: false,
            paths: [path],
            spatialReference: { wkid: 4326 }
          }), s, attr[0], attr[1]);
        lineGL.add(g);
      },
      createPolygons:function(gl, element, path){

        attr = this.createInfoTemplate(element);
        s = new SimpleFillSymbol()
        s.color= [ 51,51, 204, 0.8 ];
        var g = new Graphic(new Polygon(
          {
            hasZ: false,
            hasM: false,
            rings: [path],
            spatialReference: { wkid: 4326 }
          }), s, attr[0], attr[1]);
        polyGL.add(g);
      },
    });
  });
