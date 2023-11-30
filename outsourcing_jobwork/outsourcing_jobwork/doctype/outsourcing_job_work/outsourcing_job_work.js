// Copyright (c) 2023, Quantbit Technologies Pvt ltd and contributors
// For license information, please see license.txt

frappe.ui.form.on('Outsourcing Job Work', {
	// refresh: function(frm) {

	// }
});

frappe.ui.form.on('Outsourcing Job Work', {
    refresh: function(frm) {
        frm.fields_dict['supplier_id'].$input.css('background-color', '#8FC5FF');
        frm.fields_dict['supplier_name'].$input.css('background-color', '#8FC5FF');
        frm.fields_dict['in_or_out'].$input.css('background-color', '#8FC5FF');
        frm.fields_dict['outsourcing_job_work'].$input.css('background-color', '#8FC5FF');
        frm.fields_dict['naming_series'].$input.css('background-color', '#8FC5FF');
        frm.fields_dict['company'].$input.css('background-color', '#8FC5FF');
        frm.fields_dict['posting_date'].$input.css('background-color', '#8FC5FF');
        frm.fields_dict['posting_time'].$input.css('background-color', '#8FC5FF');
        frm.fields_dict['source_warehouse'].$input.css('background-color', '#8FC5FF');
        frm.fields_dict['target_warehouse'].$input.css('background-color', '#8FC5FF');
        frm.fields_dict['finished_item_code'].$input.css('background-color', '#8FC5FF');
        frm.fields_dict['finished_item_name'].$input.css('background-color', '#8FC5FF');
        frm.fields_dict['production_quantity'].$input.css('background-color', '#8FC5FF');
    }
});


// ============================================================= Outsourcing Job Work ================================================= 

frappe.ui.form.on('Outsourcing Job Work', {
    source_warehouse: function(frm) {
        frm.call({
			method:'set_source_warehouse',
			doc:frm.doc,
		})
    }
});

frappe.ui.form.on('Outsourcing Job Work', {
    target_warehouse: function(frm) {
        frm.call({
			method:'set_target_warehouse',
			doc:frm.doc,
		})
    }
});

frappe.ui.form.on('Outsourcing Job Work', {
    production_quantity: function(frm) {

        frm.clear_table("outsource_job_work_details");
		frm.refresh_field('outsource_job_work_details');

        frm.call({
			method:'set_data_in_ojwd',
			doc:frm.doc,
		})
    }
});


frappe.ui.form.on('Outsourcing Job Work', {
    finished_item_code: function(frm) {

		if (frm.doc.production_quantity) {

            frm.clear_table("outsource_job_work_details");
            frm.refresh_field('outsource_job_work_details');
    
            frm.call({
                method:'set_data_in_ojwd',
                doc:frm.doc,
            })
	}

    }
});

frappe.ui.form.on('Outsourcing Job Work', {
    outsourcing_job_work: function(frm) {

	

            frm.clear_table("outsource_job_work_details");
            frm.refresh_field('outsource_job_work_details');
    
            frm.call({
                method:'in_outsouring_data',
                doc:frm.doc,
            })
	
    }
});

frappe.ui.form.on('Outsourcing Job Work', {
    in_or_out: function(frm) {

            frm.clear_table("outsource_job_work_details");
            frm.refresh_field('outsource_job_work_details');
            frm.clear_table("outsourcing_job_work");
            frm.refresh_field('outsourcing_job_work');
    }
});


frappe.ui.form.on('Outsourcing Job Work', {
    setup: function(frm) {
        frm.fields_dict.outsourcing_job_work.get_query = function(doc, cdt, cdn) {
            return {
                filters: [
                    ['Outsourcing Job Work', 'docstatus', '=', 1]
                ]
            };
        };
    }
});


// ============================================================= Outsource Job Work Details ================================================= 

frappe.ui.form.on('Outsource Job Work Details', {
    item_code: function(frm) {
        frm.call({
			method:'set_warehouse_after_item',
			doc:frm.doc,
		})
    }
});

frappe.ui.form.on('Outsource Job Work Details', {
    is_finished_item: function(frm) {
        frm.call({
			method:'set_finished_item',
			doc:frm.doc,
		})
        

    }
});