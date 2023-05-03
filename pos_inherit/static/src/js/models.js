odoo.define('pos_inherit.models', function (require) {
    'use strict';

    const {PosGlobalState, Order} = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');
    var field_utils = require('web.field_utils');
    var rpc = require('web.rpc');

    const PosGlobalStateInherit
    = (PosGlobalState) => class PosGlobalStateInherit extends PosGlobalState {

        _save_to_server (orders, options) {
            if (!orders || !orders.length) {
                return Promise.resolve([]);
            }
            this.set_synch('connecting', orders.length);
            options = options || {};

            var self = this;
            var timeout = typeof options.timeout === 'number' ? options.timeout : 30000 * orders.length;

            // Keep the order ids that are about to be sent to the
            // backend. In between create_from_ui and the success callback
            // new orders may have been added to it.
            var order_ids_to_sync = _.pluck(orders, 'id');

            // we try to send the order. shadow prevents a spinner if it takes too long. (unless we are sending an invoice,
            // then we want to notify the user that we are waiting on something )
            var args = [_.map(orders, function (order) {
                    order.to_invoice = options.to_invoice || false;
                    order.to_boleta = options.to_boleta || false;
                    return order;
                })];
            args.push(options.draft || false);
            return this.env.services.rpc({
                    model: 'pos.order',
                    method: 'create_from_ui',
                    args: args,
                    kwargs: {context: this.env.session.user_context},
                }, {
                    timeout: timeout,
                    shadow: !options.to_invoice || !options.to_boleta
                })
                .then(function (server_ids) {
                    _.each(order_ids_to_sync, function (order_id) {
                        self.db.remove_order(order_id);
                    });
                    self.failed = false;
                    self.set_synch('connected');
                    self.get_order().invoice_id = server_ids;
                    return server_ids;
                }).catch(function (error){
                    console.warn('Failed to send orders:', orders);
                    if(error.code === 200 ){    // Business Logic Error, not a connection problem
                        // Hide error if already shown before ...
                        if ((!self.failed || options.show_error) && !options.to_invoice || !options.to_boleta) {
                            self.failed = error;
                            self.set_synch('error');
                            throw error;
                        }
                    }
                    self.set_synch('disconnected');
                    throw error;
                });
        }

        // _flush_orders(orders, options) {
        //     console.log('in flush order');
        //     var self = this;
        //     var result, data
        //     result = data = super._flush_orders(...arguments)
        //     _.each(orders, function (order) {
        //         if (self.get_order() && (order["data"].name === self.get_order().name)) {
        //             if (order["data"].to_invoice || order["data"].to_boleta) {
        //                 data.then(function (order_server_id) {
        //                     console.log("order_erver_id", order_server_id)
        //                     _.each(order_server_id, function (server_id) {
        //                         rpc.query({
        //                             model: 'pos.order',
        //                             method: 'get_invoice_info',
        //                             args: [server_id.id, ['account_move']],
        //                             kwargs: {pos_reference: posmodel.get_order()['name']},
        //                         }).then(function (result_dict) {
        //                             if (result_dict) {
        //                                 let invoice = result_dict;//result_dict[0].account_move;
        //                                 console.log('then invoice', invoice);
        //                                 self.get_order().invoice_id = invoice
        //                             }
        //                         }).catch(function (error) {
        //                             console.log('catch result', result);
        //                             return result

        //                         })

        //                     });

        //                 })
        //             }
        //         }

        //     })
        //     console.log('flush order result', result);
        //     return result


        // }
    }

    const L10N_CL_SII_REGIONAL_OFFICE = {
        "ur_Anc": "Ancud", 
        "ur_Ang": "Angol", 
        "ur_Ant": "Antofagasta", 
        "ur_Ari": "Arica y Parinacota", 
        "ur_Ays": "Aysén", 
        "ur_Buin": "Buin", 
        "ur_Cal": "Calama", 
        "ur_Cas": "Castro", 
        "ur_Cau": "Cauquenes", 
        "ur_Cha": "Chaitén", 
        "ur_Chn": "Chañaral", 
        "ur_ChC": "Chile Chico", 
        "ur_Chi": "Chillán", 
        "ur_Coc": "Cochrane", 
        "ur_Cop": "Concepción ", 
        "ur_Cos": "Constitución", 
        "ur_Coo": "Copiapo", 
        "ur_Coq": "Coquimbo", 
        "ur_Coy": "Coyhaique", 
        "ur_Cur": "Curicó", 
        "ur_Ill": "Illapel", 
        "ur_Iqu": "Iquique", 
        "ur_LaF": "La Florida", 
        "ur_LaL": "La Ligua", 
        "ur_LaS": "La Serena", 
        "ur_LaU": "La Unión", 
        "ur_Lan": "Lanco", 
        "ur_Leb": "Lebu", 
        "ur_Lin": "Linares", 
        "ur_Lod": "Los Andes", 
        "ur_Log": "Los Ángeles", 
        "ur_LosRios": "Los Ríos", 
        "ur_Nunoa": "Ñuñoa", 
        "ur_Maipu": "Maipu", 
        "ur_Melipilla": "Melipilla", 
        "ur_Oso": "Osorno", 
        "ur_Ova": "Ovalle", 
        "ur_Pan": "Panguipulli", 
        "ur_Par": "Parral", 
        "ur_Pic": "Pichilemu", 
        "ur_Por": "Porvenir", 
        "ur_PuM": "Puerto Montt", 
        "ur_PuN": "Puerto Natales", 
        "ur_PuV": "Puerto Varas", 
        "ur_PuA": "Punta Arenas", 
        "ur_Qui": "Quillota", 
        "ur_Ran": "Rancagua", 
        "ur_SaA": "San Antonio", 
        "ur_SanBernardo": "San Bernardo", 
        "ur_Sar": "San Carlos", 
        "ur_SaF": "San Felipe", 
        "ur_SaD": "San Fernando", 
        "ur_SaV": "San Vicente de Tagua Tagua", 
        "ur_SaZ": "Santa Cruz", 
        "ur_SaC": "Santiago Centro", 
        "ur_SaN": "Santiago Norte", 
        "ur_SaO": "Santiago Oriente", 
        "ur_SaP": "Santiago Poniente", 
        "ur_SaS": "Santiago Sur", 
        "ur_TaT": "Tal-Tal", 
        "ur_Tac": "Talca", 
        "ur_Tah": "Talcahuano", 
        "ur_Tem": "Temuco", 
        "ur_Toc": "Tocopilla", 
        "ur_Vld": "Valdivia", 
        "ur_Val": "Vallenar", 
        "ur_Vlp": "Valparaíso", 
        "ur_Vic": "Victoria", 
        "ur_ViA": "Villa Alemana", 
        "ur_ViR": "Villarrica", 
        "ur_ViM": "Viña del Mar"
    }


    Registries.Model.extend(PosGlobalState, PosGlobalStateInherit);

    const PosOrderInherit

    = (Order) => class PosOrderInherit extends Order {
        constructor(obj, options) {
            super(...arguments);
            this.to_boleta = false;
            this.to_venta_ciggraos = false;
        }

        init_from_JSON(json) {
            super.init_from_JSON(...arguments);
            this.to_boleta = true;
            this.to_venta_ciggraos = true;
        }

        export_as_JSON() {
            const json = super.export_as_JSON(...arguments);
            json.to_boleta = this.to_boleta ? this.to_boleta : false;
            json.to_venta_ciggraos = this.to_venta_ciggraos ? this.to_venta_ciggraos : false;
            return json;
        }

        /* ---- Boleta --- */
        set_to_boleta(to_boleta) {
            this.assert_editable();
            this.to_boleta = to_boleta;
        }

        is_to_boleta() {
            return this.to_boleta;
        }


        // Venta Ciggaros 
        set_to_venta_ciggaros(to_venta_ciggraos){
            this.assert_editable();
            this.to_venta_ciggraos = to_venta_ciggraos;
        }

        is_to_venta_ciggaros() {
            return this.to_venta_ciggraos;
        }

        _format_dotted_vat_cl(vat){
            var vat_l = vat.split('-');
            var n_vat = vat_l[0];
            var n_dv = vat_l[1];
            return parseInt(n_vat).toLocaleString().replace(/,/g, '.') + '-' + n_dv;
        }

        export_for_printing() {
            var data = super.export_for_printing(...arguments);
            var self = this;

            if (self.invoice_id){
                data['invoice_id'] = self.invoice_id[0];
                data['l10n_latam_document_name'] = self.invoice_id[0].l10n_latam_document_name;
                data['l10n_latam_document_code'] = self.invoice_id[0].l10n_latam_document_code;
                data['l10n_latam_document_number'] = self.invoice_id[0].l10n_latam_document_number;
                data['invoice_barcode_stamp'] = self.invoice_id[0].invoice_barcode_stamp;
                data['journal_id'] = self.invoice_id[0].journal_id;                
            }

            data['is_to_invoice'] = self.is_to_invoice();
            data['is_to_boleta'] = self.is_to_boleta();
            data['is_to_venta_ciggaros'] = self.is_to_venta_ciggaros();
            data['dotted_vat'] = self._format_dotted_vat_cl(data.company.vat);
            data.company['primary_color'] = self.pos.company.primary_color;
            data['l10n_cl_sii_regional_office'] = L10N_CL_SII_REGIONAL_OFFICE[self.pos.company.l10n_cl_sii_regional_office];
            data['date'] = field_utils.format.date(moment(data.date), {}, {timezone: false});
            return data;
        }

        // load_server_data(){

        // }

    }
    Registries.Model.extend(Order, PosOrderInherit);

});
