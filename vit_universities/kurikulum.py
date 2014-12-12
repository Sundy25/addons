from openerp.osv import fields, osv
import time
from dateutil.relativedelta import relativedelta
import openerp
from datetime import datetime
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, image_colorize, image_resize_image_big


class master_kurikulum (osv.Model):
	_name = 'master.kurikulum'

	def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
		if not args:
			args = []
		if context is None:
			context = {}
		ids = []
		if name:
			ids = self.search(cr, user, [('name','=',name)] + args, limit=limit, context=context)
		if not ids:
			ids = self.search(cr, user, [('name',operator,name)] + args, limit=limit, context=context)
		return self.name_get(cr, user, ids, context)

	def _get_total_sks(self,cr,uid,ids,field,args,context=None):
		#import pdb;pdb.set_trace()
		result = {}
		sult = 0
		for res in self.browse(cr,uid,ids[0],context=context).kurikulum_detail_ids:
			sks = res.sks
			sult += int(sks)
		result[ids[0]] = sult
		return result
 
	_columns = {
		'name' :fields.char('Kode Kurikulum', size=28,required = True,ondelete="cascade"),
		'fakultas_id':fields.many2one('master.fakultas','Fakultas',required = True),         
		'jurusan_id':fields.many2one('master.jurusan',string='Jurusan',required = True),           
		'prodi_id':fields.many2one('master.prodi',string='Program Studi',required = True),
		'semester_id':fields.many2one('master.semester','Semester',required = True),
		'tahun_ajaran_id': fields.many2one('academic.year','Tahun Ajaran',required = True),
		'state':fields.selection([('draft','Draft'),('confirm','Konfirmasi')],string="Status",required = True),
		'kurikulum_detail_ids':fields.many2many(
			'master.matakuliah',   	# 'other.object.name' dengan siapa dia many2many
			'kurikulum_mahasiswa_rel',       # 'relation object'
			'kurikulum_id',               # 'actual.object.id' in relation table
			'matakuliah_id',           # 'other.object.id' in relation table
			'Daftar Mata Kuliah',		# 'Field Name'  
			domain="['|',('prodi_id','=',prodi_id),\
			('jenis','=','mk_umum')]",),	   
		'total_sks':fields.function(_get_total_sks,type="integer",string="Total SKS"),         			
		#'kurikulum_detail_ids':fields.one2many('master.kurikulum_detail','kurikulum_id','Daftar Mata Kuliah',),
			}
			
	_sql_constraints = [('name_uniq', 'unique(name)','Kode kurikulum tidak boleh sama')]

	_defaults = {
		'state' : 'draft',
	}

	def confirm(self,cr,uid,ids,context=None):		
		return self.write(cr,uid,ids,{'state':'confirm'},context=context)

	def cancel(self,cr,uid,ids,context=None):		
		return self.write(cr,uid,ids,{'state':'draft'},context=context)			

	def unlink(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		"""Allows to delete in draft state"""
		for rec in self.browse(cr, uid, ids, context=context):
			if rec.state != 'draft':
				raise osv.except_osv(_('Error!'), _('Data yang dapat dihapus hanya yang berstatus draft'))
		return super(spmb_mahasiswa, self).unlink(cr, uid, ids, context=context)					
			
master_kurikulum()