# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
import odoo.addons.decimal_precision as dp

class nama_komponen(models.Model):
	_name = 'nama.komponen'

	name = fields.Char(string="Komponen")

class nama_item(models.Model):
	_name = 'nama.item'

	name = fields.Char(string="Item")

class progress_komponen(models.Model):
	_name = 'progress.komponen'

	@api.model
	def create(self, vals):
		if vals.get('name', 'New') == 'New':
			vals['name'] = self.env['ir.sequence'].next_by_code('progress.hari') or '/'
		return super(progress_komponen, self).create(vals)

	name = fields.Char(string="Reference", default='/', readonly=True, required=True)
	komponen_id = fields.Many2one('nama.komponen',string="Komponen")
	hari_pengerjaan = fields.Integer(string="Waktu Pengerjaan")
	progress_line = fields.One2many('progress.item', 'progress_id', string="Progress")
	total_amount = fields.Float(string="Total Hari Pengerjaan", store=True, readonly=True, compute='_amount_all', track_visibility='always')

class progress_item(models.Model):
	_name = 'progress.item'

	progress_id = fields.Many2one('progress.komponen', string="Progress")
	item_id = fields.Many2one('nama.item', string="Item")
	komponen_id = fields.Many2one('nama.komponen', string="Komponen")
	weight = fields.Float('Weight', readonly=True, compute='_compute_weight', digits=dp.get_precision('Discount'), default=0.0)
	mulai_pengerjaan = fields.Date(string="Mulai Pengerjaan")
	tanggal_ekspektasi = fields.Date(string="Tanggal Ekspektasi")
	hari_pengerjaan = fields.Integer(string="Hari Pengerjaan")

	@api.depends('weight','hari_pengerjaan')
	def _compute_weight(self):
		for record in self:
			if record.progress_id.total_amount != 0 and record.hari_pengerjaan != 0:
				record.weight = record.hari_pengerjaan / record.progress_id.total_amount * 100

	@api.onchange('tanggal_ekspektasi', 'mulai_pengerjaan','hari_pengerjaan')
	def calculate_date(self):
		if self.mulai_pengerjaan and self.tanggal_ekspektasi:
			d1=datetime.strptime(str(self.mulai_pengerjaan),'%Y-%m-%d') 
			d2=datetime.strptime(str(self.tanggal_ekspektasi),'%Y-%m-%d')
			d3=d2-d1
			self.hari_pengerjaan=str(d3.days)