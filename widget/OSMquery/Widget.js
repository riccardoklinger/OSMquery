define(['dojo/_base/declare',
    'dojo/_base/html',
    'dojo/on',
    'dojo/_base/lang',
    'dojo/_base/array',
    'dojo/dom',
'dojo/parser',
'jimu/BaseWidget',
'dojo/ready',
'dojo/store/Memory',
'dijit/form/ComboBox',
'dijit/registry',
'dojo/request',
'dojo/domReady!'
],
  function(declare, html,on, lang, array, dom, parser, BaseWidget, ready, Memory, ComboBox, registry, request) {
    //To create a widget, you need to derive from BaseWidget
    return declare([BaseWidget], {
      // Custom widget code goes here

      baseClass: 'jimu-widget-osmquery',

      //this property is set by the framework when widget is loaded.
      //name: 'CustomWidget',


      //methods to communication with app container:

      // postCreate: function() {
      //   this.inherited(arguments);
      //   console.log('postCreate');
      // },

      startup: function() {
        //this.inherited(arguments);
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
        dojo.connect(registry.byId('osmkey'),'onChange',lang.hitch(this, 'keyHasChanged'));
        keyStore = new Memory({data: keys}	);
        console.log(registry.byId("osmkey"));
        //connect search button with function:
        this.own(on(dojo.byId("getOSMdata"),	'click', lang.hitch(this, 'doSearch')));
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
        QUERY_START = "[out:json][timeout:60]"
        QUERY_DATE = '[date:"timestamp"];('
        QUERY_END = ');(._;>;);out;>;'
        var key = dojo.byId("osmkey").value;
        var tag = dojo.byId("osmtag").value;
        request.post("http://overpass-api.de/api/interpreter", {
        data: '[out:json][timeout:60][date:"2018-09-16T18:48:39Z"];(node["amenity"="school"](58.710191847296,-4.449434890700729,59.43312109760033,-0.9760399259956395);way["amenity"="school"](58.710191847296,-4.449434890700729,59.43312109760033,-0.9760399259956395);relation["amenity"="school"](58.710191847296,-4.449434890700729,59.43312109760033,-0.9760399259956395););(._;>;);out;>;',
        headers: {
        },
        handleAs: "json"
    }).then(function(response){
        //response holds now all the information
        console.log(response.version);
    });
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
