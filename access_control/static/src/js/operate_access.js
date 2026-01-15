odoo.define('access_control.operate_access', function (require) {
    var core = require('web.core');
    var rpc = require('web.rpc');
    var Widget = require('web.Widget');
    var AbstractAction = require('web.AbstractAction');

    var QWeb = core.qweb;


    var _t = core._t;
    toastr.options = {
        closeButton: true,
        debug: false,
        progressBar: true,
        positionClass: "toast-top-center",
        onclick: null,
        showDuration: "300",
        hideDuration: "1000",
        timeOut: "5000",
        extendedTimeOut: "1000",
        showEasing: "swing",
        hideEasing: "linear",
        showMethod: "fadeIn",
        hideMethod: "fadeOut"
    };
    var OperateAccess = AbstractAction.extend({
        events: {
            'click .close-model': function (e) {
                $('.modal-backdrop').remove();
            },
            'click .button_name': function (e) {
                // this.set_button(e);
            },
            'change .button_select': function (e) {
                this.set_button_state(e);
            },
            'click .add_route': function (event) {
                this.add_route(event);
            },
            'click .do_add_route': function (e) {
                this.do_add_route(e);
            },
            'click .ready_delete_route': function (event) {
                this.ready_delete_route(event);
            },
            'click .do_delete_route': function (event) {
                this.do_delete_route(event)
            }
        },
        init: function (parent, action) {
            this.odoo_context = action.context;
            this._super.apply(this, arguments);
        },
        start: function () {
            var sup = this._super();
            var page = this.$el;
            this.show_page(page);
            return sup
        },
        show_page: async function (page) {
            var self = this
            let res = await rpc.query({
                model: 'role.access.route',
                method: 'get_roles_access',
                args: [this.odoo_context.active_id],
            })
            console.log(res)
            page.html(QWeb.render("operate_access_template", {'res': res}));
            $('.menu_title').click();
        },
        set_button: async function (e) {
            console.log(e.currentTarget.dataset)
            const buttonId = e.currentTarget.dataset.buttonId
            const routeId = e.currentTarget.dataset.routeId
            console.log($('#select' + routeId + buttonId).val())
            var args = {
                'button_id': buttonId,
                'route_id': routeId,
                'state': $('#select' + routeId + buttonId).val(),
            }
            let res = await rpc.query({
                model: 'role.access.route',
                method: 'set_button_access',
                args: [args],
            })
            console.log(res)
            if (res) {
                $('#button' + routeId + buttonId).addClass('selected')
            } else {
                $('#button' + routeId + buttonId).removeClass('selected')
            }
        },
        set_button_state: async function (e) {
            const buttonId = e.currentTarget.dataset.buttonId
            const routeId = e.currentTarget.dataset.routeId
            var args = {
                'button_id': buttonId,
                'route_id': routeId,
                'state': $('#select' + routeId + buttonId).val(),
            }
            let res = await rpc.query({
                model: 'role.access.route',
                method: 'set_button_access_state',
                args: [args],
            })
        },
        add_route: async function (e) {
            const roleId = e.currentTarget.dataset.roleId
            let args = {
                'role_id': roleId
            }
            let res = await rpc.query({
                model: 'role.access.route',
                method: 'get_selected_route',
                args: [args],
            })
            $('#add_route').html(QWeb.render("add_route", {'routes': res, 'role_id': roleId}));
            $('#add_route_modal').click()


        },
        do_add_route: async function (e) {
            const roleId = e.currentTarget.dataset.roleId
            console.log($('#add_route_select').val())
            if (!$('#add_route_select').val()) {
                toastr.warning('Please select at least one item.')
                return
            }
            let args = {
                'route_ids': $('#add_route_select').val(),
                'role_id': roleId
            }
            let res = await rpc.query({
                model: 'role.access.route',
                method: 'add_route_to_role',
                args: [args],
            })
            this.show_page(this.$el);
            $('.modal-backdrop').remove()
        },
        do_mouseover: function (event) {
            const routeId = event.currentTarget.dataset.routeId
            $('#delete_route' + routeId).removeClass('hidden')
        },
        do_mouseout: function (event) {
            const routeId = event.currentTarget.dataset.routeId
            $('#delete_route' + routeId).addClass('hidden')
        },
        ready_delete_route: function (event) {
            const routeId = event.currentTarget.dataset.routeId
            const routeName = event.currentTarget.dataset.routeName
            $('#confirm_delete_dialog').html(QWeb.render("access_control_confirm_delete_dialog", {
                id: routeId,
                name: routeName,
            }));
            $('#confirm_delete_btn').click()
        },
        do_delete_route: async function (event) {
            const routeId = event.currentTarget.dataset.routeId
            var args = {
                'route_id':routeId
            }
            let res = await rpc.query({
                model: 'role.access.route',
                method: 'delete_route_from_role',
                args: [args],
            })
            this.show_page(this.$el);
            $('.modal-backdrop').remove()
        }
    });
    core.action_registry.add('operate_access', OperateAccess);
    return OperateAccess;
});
