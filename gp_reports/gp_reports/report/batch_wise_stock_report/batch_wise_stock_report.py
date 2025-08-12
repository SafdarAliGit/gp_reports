
import frappe
from frappe import _


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data


def get_columns():
    columns = [
        {
            "label": _("Item"),
            "fieldname": "item_code",
            "fieldtype": "Data",
            "width": 100,
        },
        
        {"label": _("Warehouse"),
         "fieldname": "warehouse",
         "fieldtype": "Link",
         "options": "Warehouse",
         "width": 100
         },
         {
            "label": _("Batch"),
            "fieldname": "batch_no",
            "fieldtype": "Data",
            "width": 100
        },
        {
            "label": _("OPEN Qty"),
            "fieldname": "opening_qty",
            "fieldtype": "Float",
            "width": 100
        },
        {
            "label": _("OPEN Rate"),
            "fieldname": "valuation_rate",
            "fieldtype": "Currency",
            "options": "currency",
            "width": 100
        },
        {
            "label": _("OPEN AMT."),
            "fieldname": "opening_amount",
            "fieldtype": "Currency",
            "options": "currency",
            "width": 120
        },

        {
            "label": _("PURC. Qty"),
            "fieldname": "in_qty",
            "fieldtype": "Float",
            "width": 100
        },
        {
            "label": _("PURC. Rate"),
            "fieldname": "incoming_rate",
            "fieldtype": "Currency",
            "options": "currency",
            "width": 120
        },
        {
            "label": _("PURC. AMT."),
            "fieldname": "in_amount",
            "fieldtype": "Currency",
            "options": "currency",
            "width": 120
        },
        {
            "label": _("DN Qty"),
            "fieldname": "out_qty",
            "fieldtype": "Float",
            "width": 80

        },
        {
            "label": _("DN Rate"),
            "fieldname": "valuation_rate",
            "fieldtype": "Currency",
            "options": "currency",
            "width": 120
        },
        {
            "label": _("DN AMT."),
            "fieldname": "out_amount",
            "fieldtype": "Currency",
            "options": "currency",
            "width": 120
        },
   
        {
            "label": _("Balance Qty"),
            "fieldname": "balance_qty",
            "fieldtype": "Float",
            "width": 100
        },
        {
            "label": _("Balance AMT."),
            "fieldname": "balance_value",
            "fieldtype": "Currency",
            "width": 120

        },
        {
            "label": _("Stock Shortage"),
            "fieldname": "stock_shortage",
            "fieldtype": "Float",
            "width": 100

        },
        {
            "label": _("Shortage AMT."),
            "fieldname": "shortage_amount",
            "fieldtype": "Currency",
            "options": "currency",
            "width": 120
        }
    ]

    return columns


def get_conditions_first(filters):
    conditions = []
    if filters.get("item_code"):
        conditions.append(f"AND sii.item_code = %(item_code)s")
    return " ".join(conditions)


def get_conditions_second(filters):
    conditions = []
    if filters.get("item_code"):
        conditions.append(f"AND sle.item_code = %(item_code)s")
    return " ".join(conditions)


def get_data(filters):
    data = []
    conditions_first = get_conditions_first(filters)
    conditions_second = get_conditions_second(filters)

    bonus_query = f"""
        SELECT 
            sii.item_code
        FROM `tabSales Invoice` AS si, `tabSales Invoice Item` AS sii
        WHERE
            si.docstatus = 1
            AND si.is_return = 0
            AND si.posting_date >= '{filters.get('from_date')}'
            AND si.posting_date <= '{filters.get('to_date')}'
            AND si.name = sii.parent
            AND sii.rate = 0
           {conditions_first}
        GROUP BY sii.item_code
        """
    bonus_result = frappe.db.sql(bonus_query, filters, as_dict=1)

    stock_balance_query = f"""
    SELECT 
        sle.item_code,
        sle.warehouse,
        sle.batch_no,
        sle.valuation_rate,
        sle.incoming_rate,
        SUM(CASE WHEN sle.posting_date >= '{filters.get('from_date')}' AND  sle.posting_date <= '{filters.get('to_date')}' AND sle.voucher_type = 'Purchase Receipt' AND sle.actual_qty > 0 THEN sle.actual_qty ELSE 0 END) AS in_qty,
        SUM(CASE WHEN sle.posting_date < '{filters.get('from_date')}' THEN sle.actual_qty ELSE 0 END) AS opening_qty,
        SUM(CASE WHEN sle.posting_date < '{filters.get('from_date')}' AND sle.voucher_type = "Stock Entry" AND sle.actual_qty < 0 THEN sle.actual_qty ELSE 0 END) AS stock_shortage,
        ABS(SUM(CASE WHEN sle.posting_date < '{filters.get('from_date')}' AND sle.voucher_type = "Stock Entry" AND sle.actual_qty < 0 THEN sle.actual_qty ELSE 0 END)*sle.valuation_rate) AS shortage_amount,
        SUM(CASE WHEN sle.posting_date >= '{filters.get('from_date')}' AND  sle.posting_date <= '{filters.get('to_date')}' AND sle.voucher_type = 'Purchase Receipt' AND sle.actual_qty > 0 THEN sle.actual_qty ELSE 0 END)*sle.incoming_rate AS in_amount,
        SUM(CASE WHEN sle.posting_date < '{filters.get('from_date')}' THEN sle.actual_qty ELSE 0 END)*sle.valuation_rate AS opening_amount,
        ABS(SUM(CASE WHEN sle.posting_date >= '{filters.get('from_date')}' AND  sle.posting_date <= '{filters.get('to_date')}' AND sle.voucher_type = 'Delivery Note' AND sle.actual_qty < 0 THEN sle.actual_qty ELSE 0 END)) AS out_qty,
        ABS(SUM(CASE WHEN sle.posting_date >= '{filters.get('from_date')}' AND  sle.posting_date <= '{filters.get('to_date')}' AND sle.voucher_type = 'Delivery Note' AND sle.actual_qty < 0 THEN sle.actual_qty ELSE 0 END)) * sle.valuation_rate AS out_amount,
         (((SUM(CASE WHEN sle.posting_date >= '{filters.get('from_date')}' AND  sle.posting_date <= '{filters.get('to_date')}' AND sle.voucher_type = 'Purchase Receipt' AND sle.actual_qty > 0 THEN sle.actual_qty ELSE 0 END) + SUM(CASE WHEN sle.posting_date < '{filters.get('from_date')}' THEN sle.actual_qty ELSE 0 END)) + SUM(CASE WHEN sle.posting_date >= '{filters.get('from_date')}' AND  sle.posting_date <= '{filters.get('to_date')}' AND sle.voucher_type = 'Delivery Note' AND sle.actual_qty > 0 THEN sle.actual_qty ELSE 0 END))-ABS(SUM(CASE WHEN sle.posting_date >= '{filters.get('from_date')}' AND  sle.posting_date <= '{filters.get('to_date')}' AND sle.voucher_type = 'Delivery Note' AND sle.actual_qty < 0 THEN sle.actual_qty ELSE 0 END)))  AS balance_qty,
         ((((SUM(CASE WHEN sle.posting_date >= '{filters.get('from_date')}' AND  sle.posting_date <= '{filters.get('to_date')}' AND sle.voucher_type = 'Purchase Receipt' AND sle.actual_qty > 0 THEN sle.actual_qty ELSE 0 END) + SUM(CASE WHEN sle.posting_date < '{filters.get('from_date')}' THEN sle.actual_qty ELSE 0 END)) + SUM(CASE WHEN sle.posting_date >= '{filters.get('from_date')}' AND  sle.posting_date <= '{filters.get('to_date')}' AND sle.voucher_type = 'Delivery Note' AND sle.actual_qty > 0 THEN sle.actual_qty ELSE 0 END))-ABS(SUM(CASE WHEN sle.posting_date >= '{filters.get('from_date')}' AND  sle.posting_date <= '{filters.get('to_date')}' AND sle.voucher_type = 'Delivery Note' AND sle.actual_qty < 0 THEN sle.actual_qty ELSE 0 END)))*sle.valuation_rate) AS balance_value
        
         
    FROM `tabStock Ledger Entry` AS sle
    WHERE
        sle.is_cancelled = 0
        {conditions_second}
    GROUP BY sle.batch_no
    """

    stock_balance_result = frappe.db.sql(stock_balance_query, filters, as_dict=1)
    data.extend(stock_balance_result)
    return data
