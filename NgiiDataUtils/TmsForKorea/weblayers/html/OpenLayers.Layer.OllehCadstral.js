﻿/* Copyright (c) 2006-2012 by OpenLayers Contributors (see authors.txt for 
 * full list of contributors). Published under the 2-clause BSD license.
 * See license.txt in the OpenLayers distribution or repository for the
 * full text of the license. */

/**
 * @requires OpenLayers/Layer/XYZ.js
 */

OpenLayers.Layer.OllehCadstral = OpenLayers.Class(OpenLayers.Layer.XYZ, {

    name: "OllehCadstralMap",
    url: [
        "http://map.ktgis.com/CadastralMap/cadastral4.04.1_0527/layers/_alllayers/l${z}/r${y}/c${x}.png"
    ],
    
    resolutions: [2048, 1024, 512, 256, 128, 64, 32, 16, 8, 4, 2, 1, 0.5],
    sphericalMercator: false,
    buffer: 0,
    numZoomLevels: 13,
    minResolution: 0.5,
    maxResolution: 2048,
    units: "m",
    projection: new OpenLayers.Projection("EPSG:5179"),
    displayOutsideMaxExtent: false,
    maxExtent: new OpenLayers.Bounds(171162, 1214781, 1744026, 2787645),
    
    initialize: function(name, options) {
        if (!options) options = {resolutions: [2048, 1024, 512, 256, 128, 64, 32, 16, 8, 4, 2, 1, 0.5]};
        else if (!options.resolutions) options.resolutions = [2048, 1024, 512, 256, 128, 64, 32, 16, 8, 4, 2, 1, 0.5];
        var newArgs = [name, null, options];
        OpenLayers.Layer.XYZ.prototype.initialize.apply(this, newArgs);
    },
    
    clone: function(obj) {
        if (obj == null) {
            obj = new OpenLayers.Layer.OllehCadstral(
                this.name, this.getOptions());
        }
        obj = OpenLayers.Layer.XYZ.prototype.clone.apply(this, [obj]);
        return obj;
    },
    
    getXYZ: function(bounds) {
        var res = this.getServerResolution();
        var x = Math.floor((bounds.left - this.maxExtent.left) / (res * this.tileSize.w));
        var y = Math.floor((this.maxExtent.top - bounds.bottom) / (res * this.tileSize.h));
        var z = this.getServerZoom();
        
        var sz = new String(z);
        var uz = sz;
        
        if (sz.length == 1) {
            uz = '0' + sz;
        }
        
        var sx = parseInt(x).toString(16);
        var ux = sx;
        
        if (sx.length == 1) 
            ux = '0000000' + sx;
        else if (sx.length == 2) 
            ux = '000000' + sx;
        else if (sx.length == 3) 
            ux = '00000' + sx;
        else if (sx.length == 4) 
            ux = '0000' + sx;
        else if (sx.length == 5) 
           ux = '000' + sx;
        else if (sx.length == 6) 
            ux = '00' + sx;
        else if (sx.length == 7) 
            ux = '0' + sx;
        
        var sy = parseInt(y - 1).toString(16);
        var uy = sy;
        
        if (sy.length == 1) 
            uy = '0000000' + sy;
        else if (sy.length == 2) 
            uy = '000000' + sy;
        else if (sy.length == 3) 
            uy = '00000' + sy;
        else if (sy.length == 4) 
            uy = '0000' + sy;
        else if (sy.length == 5) 
            uy = '000' + sy;
        else if (sy.length == 6) 
            uy = '00' + sy;
        else if (sy.length == 7) 
            uy = '0' + sy;
            
        return {'x': ux, 'y': uy, 'z': uz};
    },
    
    CLASS_NAME: "OpenLayers.Layer.OllehCadstral"
});
