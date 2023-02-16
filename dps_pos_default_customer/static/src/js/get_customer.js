odoo.define('dps_pos_default_customer.GetCustomer', function(require) {
    "use strict";

    const { PosGlobalState, Order, Orderline, Payment } = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');
    
    const PosRestaurantOrder = (Order) => class PosRestaurantOrder extends Order {
        constructor(obj, options) {
            super(...arguments);
            if (this.pos.config.cstm_default_partner_id && !this.export_as_JSON().partner_id) {
                this.set_partner(this.pos.db.get_partner_by_id(this.pos.config.cstm_default_partner_id[0]));
            }
        }
       
    }
    Registries.Model.extend(Order, PosRestaurantOrder);

});