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
        this.areaId = new Array();
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
        this.own(on(this.map, "pan", lang.hitch(this, this.updateExtent)));
        this.own(on(this.map, "zoomEnd", lang.hitch(this, this.updateExtent)));
        this.own(on(this.map, "update-end", lang.hitch(this, this.updateExtent)));
        dojo.connect(registry.byId('osmkey'),'onChange',lang.hitch(this, 'keyHasChanged'));

        registry.byId("getLocation").connect("onClick", lang.hitch(this, this.getExtent()));
        //dojo.byId("getLocation").connect("onClick", function test(){console.log("clicked")});
        //dojo.connect(dojo.byId("getLocation"), "onClick", OSMQueryWidget.getExtent(dojo.byId("region").value));

        keyStore = new Memory({data: keys}	);
        //this.own(on(dojo.byId("getOSMdata"),	'click', lang.hitch(this, this.doSearch)));

        this.locationFound = false;
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

        regSet=dojo.byId("regionalSetting").value;
        if (regSet == "region"){
          domStyle.set("extent", "visibility", "collapse");
          domStyle.set("regionTable", "visibility", "visible");
          if (this.locationFound == false){
            var LocButton = registry.byId("getOSMdata");
            LocButton.set("disabled", true);
            //domStyle.set("getOSMdata", "disabled ", true);
          }
        }
        else {
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
                  console.log(response[object]);
                  nominatim_area_id = response[object].osm_id;
                  OSMQueryWidget.areaId.push('area(' + String(parseInt(nominatim_area_id) + 3600000000) + ')->.searchArea;');
                  OSMQueryWidget.areaId.push('(area.searchArea);');
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

        //getExtent:
        if (dojo.byId("regionalSetting").value== "extent"){
          console.log(dojo.byId("region").value);
          OSMQueryWidget.areaId.push("");
          OSMQueryWidget.areaId.push("(" + dojo.byId("ymin").innerHTML + "," + dojo.byId("xmin").innerHTML + "," + dojo.byId("ymax").innerHTML + "," + dojo.byId("xmax").innerHTML + ")");
          createRequest
          .then(runRequest);
        } else {
          //queryExtent = ""
          //console.log(OSMQueryWidget.getExtent);
          //queryExtent = "(" + dojo.byId("ymin").innerHTML + "," + dojo.byId("xmin").innerHTML + "," + dojo.byId("ymax").innerHTML + "," + dojo.byId("xmax").innerHTML + ")"
          //var areaId;
          //this.areaId=this.getExtent(dojo.byId("region").value);
          //this.getExtent(dojo.byId("region").value)
          //.then(runRequest);
          /*var NominatimRun = 0;
          //while (this.areaId[0]<1){
          //()  if (NominatimRun <1){
              this.areaId[0]=this.getExtent(dojo.byId("region").value);
            }
            NominatimRun = 1;
          }
          console.log("Area= ");
          //this.area = this.areaId[0];

          console.log(this.area);*/

        }

        //
        //var queryExtent = "(" + String(extent[0].y) + "," + String(extent[0].x) + "," + String(extent[1].y) + "," + String(extent[1].x) + ")";

      },
      createRequest:function(){
        this.inherited(arguments);
        var key = dojo.byId("osmkey").value;
        var tag = dojo.byId("osmtag").value;
        if (tag=="* (any value, including the ones listed below)"){
          tag = "";
        }

        esriConfig.defaults.io.corsEnabledServers.push("overpass-api.de");
        dataUrl  = "http://overpass-api.de/api/interpreter";
        console.log(queryExtent);
        var requestSend = false;
        this.layersRequest = esriRequest({
          url: dataUrl,
          content: {data:'[out:json][timeout:60][date:"2018-09-16T18:48:39Z"]' + OSMQueryWidget.areaId[0] + ';(node["' + key + '"="' + tag + '"]' + OSMQueryWidget.areaId[1] + ';);(._;>;);out;>;'},
          handleAs: "json",
          callbackParamName: "callback"
        });
      },
      runRequest:function(){
        this.inherited(arguments);
        OSMQueryWidget.layersRequest.then(
          function(response) {
            if(confirm("Your Query response contains " + response.elements.length + " objects. You want to add them?")){
              //check for needed layers:
              var pointGL = null;
              for(element in response.elements){
                if(response.elements[element].type == "node"){
                  if (!pointGL){
                    pointGL = OSMQueryWidget.createPointGraphicsLayer();
                  }
                  OSMQueryWidget.createPoints(pointGL, response.elements[element])
                }
              }
              console.log(pointGL);
              OSMQueryWidget.map.addLayer(pointGL);
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
      createPoints:function(gl, element){
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
        s = new SimpleMarkerSymbol().setSize(60);
        var g = new Graphic(new Point(element.lon, element.lat), s, attr, infoTemplate);
        pointGL.add(g);
      },
      // onOpen: function(){
      //   console.log('onOpen');
      // },

      // onClose: function(){
      //   console.log('onClose');
      // },

      // onMinimize: function(){
      //   console.log('onMinimize');
      // },

      // onMaximize: function(){
      //   console.log('onMaximize');
      // },

/*      proofAdministrator:function(){

        var info = new OAuthInfo({
          popup: true,
          portalUrl: this.appConfig.portalUrl
          });
          IdentityManager.registerOAuthInfos([info]);

          portal = new arcgisPortal.Portal(this.appConfig.portalUrl).signIn().then(
            function (portalUser){
              console.log("Signed in to the portal: ", portalUser.role);
            }
          ).otherwise(
          function (error){
            console.log("Error occurred while signing in: ", error);
          }
          );
      },*/

      // onSignOut: function(){
      //   console.log('onSignOut');
      // }

      // onPositionChange: function(){
      //   console.log('onPositionChange');
      // },

      // resize: function(){
      //   console.log('resize');
      // }

      //methods to communication between widgets:

    });
  });
