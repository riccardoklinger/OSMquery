define(['dojo/_base/declare',
    'dojo/_base/html',
    'dojo/on',
    'dojo/_base/lang',
    'dijit/_WidgetsInTemplateMixin',
    'dojo/_base/array',
    'dojo/dom',
    'dojo/parser',
    'jimu/BaseWidget',
    'dojo/ready',
    'dojo/store/Memory',
    'dijit/form/ComboBox',
    'dijit/registry',
    'esri/request',
    //'esri/map',
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
    //'esri/graphic',
    //'esri/Color',
    'dojo/domReady!'
],
  function(declare,
    html,
    on,
    lang,
    _WidgetsInTemplateMixin,
    array,
    dom,
    parser,
    BaseWidget,
    ready,
    Memory,
    ComboBox,
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
    projection
  ) {
    //To create a widget, you need to derive from BaseWidget
    return declare([BaseWidget, _WidgetsInTemplateMixin], {
      // Custom widget code goes here

      baseClass: 'jimu-widget-osmquery',

      //this property is set by the framework when widget is loaded.
      //name: 'CustomWidget',


      //methods to communication with app container:

      postCreate: function() {
         this.inherited(arguments);
         console.log(this.map.spatialReference);
         console.log('postCreate');
      },

      startup: function() {
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
        k = 0;
        for (key in Configuration){
          if (Configuration.hasOwnProperty(key)){
            keys.push(key);
            registry.byId("osmkey").get('store').add({ name: key, id: k });
            k+=1;
          }
        }
        this.own(on(this.map, "pan", lang.hitch(this, this.updateExtent)));
        this.own(on(this.map, "zoomEnd", lang.hitch(this, this.updateExtent)));
        this.own(on(this.map, "update-end", lang.hitch(this, this.updateExtent)));
        dojo.connect(registry.byId('osmkey'),'onChange',lang.hitch(this, 'keyHasChanged'));
        keyStore = new Memory({data: keys}	);
        //console.log(registry.byId("osmkey"));
        //console.log(registry.byId("map"));
        //connect search button with function:
        this.own(on(dojo.byId("getOSMdata"),	'click', lang.hitch(this, this.doSearch)));
        //this.own(on(dojo.byId("getOSMdata"),	'click', lang.hitch(this, this.getExtent)));

      },
      keyHasChanged:function() {

        var Configuration = this.config;
        //clear current combobox store
        var folderListLength = registry.byId("osmtag").store.data.length
        for(var n=0; n < folderListLength; n++){
          registry.byId("osmtag").get('store').remove(n)
        };

        //populate box again:
        k = 0;
        currentKey = dojo.byId("osmkey").value;
        tags = new Array();
        for (tag in Configuration[currentKey]){
            registry.byId("osmtag").get('store').add({ name: Configuration[currentKey][tag], id: k });
            k+=1;
        }
      },
      doSearch:function(){
        this.inherited(arguments);
        QUERY_START = "[out:json][timeout:60]"
        QUERY_DATE = '[date:"timestamp"];('
        QUERY_END = ');(._;>;);out;>;'
        //getExtent:
        queryExtent = "(" + dojo.byId("ymin").innerHTML + "," + dojo.byId("xmin").innerHTML + "," + dojo.byId("ymax").innerHTML + "," + dojo.byId("xmax").innerHTML + ")"
        //var queryExtent = "(" + String(extent[0].y) + "," + String(extent[0].x) + "," + String(extent[1].y) + "," + String(extent[1].x) + ")";
        var key = dojo.byId("osmkey").value;
        var tag = dojo.byId("osmtag").value;
        var gl = new GraphicsLayer();
        //points = new Array()
        var s = new SimpleMarkerSymbol().setSize(60);
          this.map.addLayer(gl);
          esriConfig.defaults.io.corsEnabledServers.push("overpass-api.de");
          dataUrl  = "http://overpass-api.de/api/interpreter";
          console.log(queryExtent);
          var layersRequest = esriRequest({
            url: dataUrl,
            content: {data:'[out:json][timeout:60][date:"2018-09-16T18:48:39Z"];(node["amenity"="school"]' + queryExtent + ';);(._;>;);out;>;'},
            handleAs: "json",
            callbackParamName: "callback"
          });
            layersRequest.then(
              function(response) {
                if(confirm("Your Query response contains " + response.elements.length + " objects. You want to add them?")){
                  for(element in response.elements){
                    console.log(response.elements[element]);
                    if(response.elements[element].type == "node"){
                        var attr = response.elements[element].tags;
                        for (key in attr){
                            if (key.indexOf(":")>0){
                              attr[key.replace(":","_")] = attr[key];
                              delete attr[key];
                            }
                        }
                        console.log(attr);
                        infoText = "";
                        for (key in attr){
                          //console.log(attr);
                          //console.log(key);
                          infoText += key + ":" + "${" + key + "}<br>";
                          //console.log(infoText);
                        }
                        var infoTemplate = new InfoTemplate();
                        infoTemplate.title = "Attributes";
                        infoTemplate.content = infoText;
                        var g = new Graphic(new Point(response.elements[element].lon, response.elements[element].lat), s, attr, infoTemplate);
                        gl.add(g);
                    }
                  }

                }
            }, function(error) {
              console.log("Error: ", error.message);
            });
      },
      updateExtent:function(){
          this.inherited(arguments);
        // we need to convert the extent to 4326 coordinate pairs;
        //console.log(extent);
        if (this.map.extent.spatialReference.wkid != 4326){
          targetsr = new SpatialReference(4326);
          sourcesr = this.map.extent.spatialReference;
          var extentStr = "";
          LL = new Point(this.map.extent.xmin,this.map.extent.ymin, sourcesr);
          UR = new Point(this.map.extent.xmax,this.map.extent.ymax, sourcesr);
          projection.load().then(function() {
            LLProj = projection.project(LL, targetsr);
            extentStr+= String(Math.round(LLProj.y*100)/100) + ",";
            extentStr+= String(Math.round(LLProj.x*100)/100) + ",";
            URProj = projection.project(UR, targetsr);
            extentStr+= String(Math.round(URProj.y*100)/100) + ",";
            extentStr+= String(Math.round(URProj.x*100)/100);
            queryExtent = "(" + extentStr + ")";
            dojo.byId("ymin").innerHTML = String(Math.round(LLProj.y*10000)/10000);
            dojo.byId("xmin").innerHTML = String(Math.round(LLProj.x*10000)/10000);
            dojo.byId("ymax").innerHTML = String(Math.round(URProj.y*10000)/10000);
            dojo.byId("xmax").innerHTML = String(Math.round(URProj.x*10000)/10000);
          });
        }
      },
      //currently this function is not visible inside the then function call:
      createPoints:function(x,y){
        console.log(x);
      }
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

      // onSignIn: function(credential){
      //   /* jshint unused:false*/
      //   console.log('onSignIn');
      // },

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
