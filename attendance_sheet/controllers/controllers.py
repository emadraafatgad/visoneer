# -*- coding: utf-8 -*-
# from odoo import http


# class AttendanceSheet(http.Controller):
#     @http.route('/attendance_sheet/attendance_sheet', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/attendance_sheet/attendance_sheet/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('attendance_sheet.listing', {
#             'root': '/attendance_sheet/attendance_sheet',
#             'objects': http.request.env['attendance_sheet.attendance_sheet'].search([]),
#         })

#     @http.route('/attendance_sheet/attendance_sheet/objects/<model("attendance_sheet.attendance_sheet"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('attendance_sheet.object', {
#             'object': obj
#         })
