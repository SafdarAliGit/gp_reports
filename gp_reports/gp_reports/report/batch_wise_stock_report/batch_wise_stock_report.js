

frappe.query_reports["Batch Wise Stock Report"] = {
	"filters": [
		{
			"fieldname": "company",
			"label": __("Company"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Company",
			"default": frappe.defaults.get_default("company")
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd": 1,
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "80",
			"reqd": 1,
			"default": frappe.datetime.get_today()
		},
		{
			"fieldname": "item_code",
			"label": __("Item"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Item",
			"get_query": function() {
				return {
					query: "erpnext.controllers.queries.item_query",
				};
			}
		},
		{
			"fieldname": "batch_no",
			"label": __("Batch No"),
			"fieldtype": "Link",
			"width": "80",
			"options": "Batch"
		}

	],

	// "formatter": function (value, row, column, data, default_formatter) {
	// 	value = default_formatter(value, row, column, data);

	// 	if (column.fieldname == "out_qty" && data && data.out_qty > 0) {
	// 		value = "<span style='color:red'>" + value + "</span>";
	// 	}
	// 	else if (column.fieldname == "in_qty" && data && data.in_qty > 0) {
	// 		value = "<span style='color:green'>" + value + "</span>";
	// 	}

	// 	return value;
	// }
};

