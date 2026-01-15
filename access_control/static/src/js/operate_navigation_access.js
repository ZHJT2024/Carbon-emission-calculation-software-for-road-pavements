odoo.define('access_control.operate_navigation_access', function (require) {
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
    var OperateNavigationAccess = AbstractAction.extend({
        events: {
            'click .close-model': function (e) {
                $('.modal-backdrop').remove();
            },
            'click .add_navigation': function (event) {
                this.add_navigation(event);
            },
            'click .do_add_navigation': function (e) {
                this.do_add_navigation(e);
            },
            'click .ready_delete_navigation': function (event) {
                this.ready_delete_navigation(event);
            },
            'click .do_delete_navigation': function (event) {
                this.do_delete_navigation(event)
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
                model: 'role.access.navigation',
                method: 'get_roles_navigation_access',
                args: [this.odoo_context.active_id],
            })
            console.log(res)
            page.html(QWeb.render("operate_navigation_access_template", {'res': res}));
            $('.menu_title').click();
        },

        add_navigation: async function (e) {
            const roleId = e.currentTarget.dataset.roleId
            let args = {
                'role_id': roleId
            }
            let res = await rpc.query({
                model: 'role.access.navigation',
                method: 'get_selected_navigation',
                args: [args],
            })
            console.log(res)
            $('#add_navigation').html(QWeb.render("add_navigation", {'navigations': res, 'role_id': roleId}));
            $('#add_navigation_modal').click()


        },
        do_add_navigation: async function (e) {
            const roleId = e.currentTarget.dataset.roleId
            console.log($('#add_navigation_select').val())
            if (!$('#add_navigation_select').val()) {
                toastr.warning('Please select at least one item.')
                return
            }
            let args = {
                'navigation_ids': $('#add_navigation_select').val(),
                'role_id': roleId
            }
            let res = await rpc.query({
                model: 'role.access.navigation',
                method: 'add_navigation_to_role',
                args: [args],
            })
            this.show_page(this.$el);
            $('.modal-backdrop').remove()
        },

        ready_delete_navigation: function (event) {
            const navigationId = event.currentTarget.dataset.navigationId
            const navigationName = event.currentTarget.dataset.navigationName
            $('#confirm_delete_dialog').html(QWeb.render("access_control_confirm_delete_navigation_dialog", {
                id: navigationId,
                name: navigationName,
            }));
            $('#confirm_delete_btn').click()
        },
        do_delete_navigation: async function (event) {
            const navigationId = event.currentTarget.dataset.navigationId
            var args = {
                'navigation_id': navigationId
            }
            let res = await rpc.query({
                model: 'role.access.navigation',
                method: 'delete_navigation_from_role',
                args: [args],
            })
            this.show_page(this.$el);
            $('.modal-backdrop').remove()
        }
    });
    core.action_registry.add('operate_navigation_access', OperateNavigationAccess);
    return OperateNavigationAccess;
});
