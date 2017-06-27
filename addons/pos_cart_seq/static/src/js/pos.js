odoo.define('pos_cart_seq.pos', function (require) {
"use strict";

//var PosBaseWidget = require('point_of_sale.BaseWidget');
//var chrome = require('point_of_sale.chrome');
//var gui = require('point_of_sale.gui');
var models = require('point_of_sale.models');
//var screens = require('point_of_sale.screens');
//var core = require('web.core');
//var Model = require('web.DataModel');
var formats = require('web.formats');
var utils = require('web.utils');
//var QWeb = core.qweb;
//var _t = core._t;
var round_di = utils.round_decimals;
var round_pr = utils.round_precision;

var _super_order = models.Order.prototype;

models.Order = models.Order.extend({
	
	/* ---- Order Lines --- */
    add_orderline: function(line){
    	
    	var orderline = _super_order.add_orderline.apply(this,arguments);
    	//console.log("OOOOOOOOOOO",orderline)
    	this.orderlines.add(line);
        var orderlines = this.orderlines.models
        for (var i=0;i<orderlines.length;i++){
        	//console.log(orderlines[i],"iiiiiiiiiiiii.")
        	orderlines[i]['line_no'] = i+1
        }
        this.set('orderLines').models =orderlines
    },
    	
    
    add_product: function(product, options){
        if(this._printed){
            this.destroy();
            return this.pos.get_order().add_product(product, options);
        }
        this.assert_editable();
        options = options || {};
        var attr = JSON.parse(JSON.stringify(product));
        attr.pos = this.pos;
        attr.order = this;
        var orderline_len = this.orderlines.length
        var line = new models.Orderline({}, {pos: this.pos, order: this, product: product,line_no:orderline_len+1});

        if(options.quantity !== undefined){
            line.set_quantity(options.quantity);
        }
        if(options.price !== undefined){
            line.set_unit_price(options.price);
        }
        if(options.discount !== undefined){
            line.set_discount(options.discount);
        }

        if(options.extras !== undefined){
            for (var prop in options.extras) { 
                line[prop] = options.extras[prop];
            }
        }

        var last_orderline = this.get_last_orderline();
        if( last_orderline && last_orderline.can_be_merged_with(line) && options.merge !== false){
            last_orderline.merge(line);
        }else{
            this.orderlines.add(line);
        }
        this.select_orderline(this.get_last_orderline());

        if(line.has_product_lot){
            this.display_lot_popup();
        }
    },
	
	
	
});

var _super_orderline = models.Orderline.prototype;

models.Orderline = models.Orderline.extend({
	
	initialize: function(attr, options) {
		//console.log("iiiiiiiiiiii")
		_super_orderline.initialize.call(this,attr, options);
		this.line_no = options.line_no;
	},
	
	set_quantity: function(quantity){
        this.order.assert_editable();
        if(quantity === 'remove'){
        	//console.log('222-----')
            this.order.remove_orderline(this);
            var orderlines = this.order.orderlines.models;
            for (var i=0;i< orderlines.length;i++){
            	orderlines[i]['line_no'] = i+1
            }
            this.set('orderLines').models =orderlines;
            this.order.orderlines.each(function(line){
        		line.order.select_orderline(line);
        	});
            return;
        }else{
            var quant = parseFloat(quantity) || 0;
            var unit = this.get_unit();
            if(unit){
                if (unit.rounding) {
                    this.quantity    = round_pr(quant, unit.rounding);
                    var decimals = this.pos.dp['Product Unit of Measure'];
                    this.quantityStr = formats.format_value(round_di(this.quantity, decimals), { type: 'float', digits: [69, decimals]});
                } else {
                    this.quantity    = round_pr(quant, 1);
                    this.quantityStr = this.quantity.toFixed(0);
                }
            }else{
                this.quantity    = quant;
                this.quantityStr = '' + this.quantity;
            }
        }
        this.trigger('change',this);
    },
	
});

});
