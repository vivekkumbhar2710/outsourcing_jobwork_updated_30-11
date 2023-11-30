# Copyright (c) 2023, Quantbit Technologies Pvt ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class OutsourcingJobWork(Document):
	def before_save(self):
		self.validate_ojwd()
		self.total_quantity = self.calculating_total('outsource_job_work_details','quantity')
		self.total_amount = self.calculating_total('outsource_job_work_details','total_amount')

	def before_submit(self):
		if self.in_or_out == "OUT":
			self.stock_transfer_stock_entry()
		elif self.in_or_out == "IN":
			self.manifacturing_stock_entry()

	@frappe.whitelist()
	def in_outsouring_data(self):
		# frappe.msgprint("Hi.......!")s
		for d in self.get("outsourcing_job_work"):
			OJWD = frappe.get_all('Outsource Job Work Details',
				  								filters = {'parent':d.outsourcing_job_work},
												fields = ['item_code','item_name','rate','quantity','target_warehouse','return_quantity']) 
			production_quantity = frappe.get_value("Outsourcing Job Work", d.outsourcing_job_work ,"production_quantity")
			production_done_quantity = frappe.get_value("Outsourcing Job Work", d.outsourcing_job_work ,"production_done_quantity")
			multiplication_factor = (production_quantity - production_done_quantity)
			for i in OJWD:
				self.append("outsource_job_work_details",{
							'item_code': i.item_code ,
							'item_name': i.item_name,
							'rate': i.rate,
							'source_warehouse': i.target_warehouse ,
							'actual_required_quantity':i.quantity ,
							'quantity': (i.quantity -i.return_quantity) ,
							'reference_id': d.outsourcing_job_work,
						},),
	
			OW = frappe.get_all('Outsourcing Job Work',
				  								filters = {'name':d.outsourcing_job_work},
												fields = ['finished_item_code','finished_item_name','production_quantity','production_done_quantity','target_warehouse'])
			for j in OW:
				self.append("outsource_job_work_details",{
							'item_code': j.finished_item_code ,
							'item_name': j.finished_item_name,
							'source_warehouse': j.target_warehouse ,
							'actual_required_quantity':j.production_quantity,
							'quantity': j.production_quantity - j.production_done_quantity,
							'reference_id': d.outsourcing_job_work,
							'is_finished_item': True,
						},),


	@frappe.whitelist()
	def set_source_warehouse(self):
		for i in self.get("outsource_job_work_details"):
			if self.source_warehouse:
				i.source_warehouse = self.source_warehouse


	@frappe.whitelist()
	def set_target_warehouse(self):
		for i in self.get("outsource_job_work_details"):
			if self.target_warehouse:
				i.target_warehouse = self.target_warehouse

	
	@frappe.whitelist()
	def set_warehouse_after_item(self):
		for i in self.get("outsource_job_work_details"):
			if not i.source_warehouse:
				i.source_warehouse = self.source_warehouse

			if not i.target_warehouse:
				i.target_warehouse = self.target_warehouse



	@frappe.whitelist()
	def validate_is_finish(self):
		for l in self.get("outsourcing_job_work"):
			doc = self.get('outsource_job_work_details' , filters={'is_finished_item':True ,})
			if len(doc) == 0:
				frappe.throw('There must be atleast 1 Finished Good in this Stock Entry')  
			elif len(doc) != 1:
				frappe.throw('Multiple items cannot be marked as finished item')



	@frappe.whitelist()
	def calculating_total(self,child_table ,total_field):
		casting_details = self.get(child_table)
		total_pouring_weight = 0
		for i in casting_details:
			field_data = i.get(total_field)
			total_pouring_weight = total_pouring_weight + field_data
		return total_pouring_weight
			


	@frappe.whitelist()
	def set_data_in_ojwd (self):
		if self.finished_item_code and self.production_quantity:
			doc = frappe.get_all("Outsourcing BOM Details",
									filters = {'parent':self.finished_item_code},
									fields = ['item_code','item_name','required_quantity',])
			for d in doc:
				self.append("outsource_job_work_details",{
							'item_code': d.item_code ,
							'item_name': d.item_name,
							'source_warehouse': self.source_warehouse ,
							'target_warehouse': self.target_warehouse,
							'quantity': d.required_quantity * self.production_quantity,
							'actual_required_quantity':d.required_quantity * self.production_quantity,
						},),
	
	@frappe.whitelist()
	def validate_ojwd(self):
		if self.in_or_out == 'OUT':
			poc = (self.get('outsource_job_work_details'))

			moc = frappe.get_all("Outsourcing BOM Details",
										filters = {'parent':self.finished_item_code},
										fields = ['item_code','item_name','required_quantity',])
			if len(moc) != len(poc) :
				frappe.throw("You can not add or remove rows in table 'Outsource Job Work Details'")

			for p in poc:
				count = 0
				for m in moc:
					if p.item_code == m.item_code:
						count = count + 1

				if count == 0:
					frappe.throw(f"Item Code is not matches with Item code from 'Outsourcing BOM'")

			poc_target_warehouse = set(p.target_warehouse for p in poc)
			if len(poc_target_warehouse) != 1:
				frappe.throw('The "Target Warehose" should be same for all item')
			else:
				self.target_warehouse = list(poc_target_warehouse)[0] 

		elif self.in_or_out == 'IN':
			for m in self.get("outsourcing_job_work"):
				shit = self.get("outsource_job_work_details" , filters= {"reference_id" : m.outsourcing_job_work})
				poc_source_warehouse = set(b.target_warehouse for b in shit)
				if len(poc_source_warehouse) != 1:
					frappe.throw('The "Source Warehose" should be same for all item')


	@frappe.whitelist()
	def stock_transfer_stock_entry(self):
		if self.in_or_out == "OUT":
			count = 0
			se = frappe.new_doc("Stock Entry")
			se.stock_entry_type = "Material Transfer"
			se.company = self.company
			se.posting_date = self.posting_date
			for d in self.get('outsource_job_work_details' ,filters= {"is_supply_by_supplier" : False }):
				count = count + 1
				se.append(
								"items",
								{
									"item_code": d.item_code,
									"qty": d.quantity,
									"s_warehouse": d.source_warehouse,
									"t_warehouse": d.target_warehouse,
								},)

						
			se.custom_outsourcing_job_work = self.name	
			if count !=0:
				se.insert()
				se.save()
				se.submit()	

	@frappe.whitelist()
	def manifacturing_stock_entry(self):
		if self.in_or_out == 'IN':
			for cd in self.get("outsourcing_job_work"):      
				se = frappe.new_doc("Stock Entry")
				se.stock_entry_type = "Manufacture"
				se.company = self.company
				se.posting_date = self.posting_date
				
				all_core = self.get("outsource_job_work_details" ,  filters={"reference_id": cd.outsourcing_job_work ,})
				for core in all_core:
					if core.is_finished_item:
						se.append(
							"items",
							{
								"item_code": core.item_code,
								"qty": core.quantity,
								"t_warehouse": core.target_warehouse,
								"is_finished_item": True
							},)
					else:
						se.append(
								"items",
								{
									"item_code": core.item_code,
									"qty":  core.quantity,
									"s_warehouse": core.source_warehouse,
								},)
					

				se.custom_outsourcing_job_work = self.name	
				if all_core:
					se.insert()
					se.save()
					se.submit()

