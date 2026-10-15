# Copyright (c) 2025, Aman Boora and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class GiftStockRequest(Document):
    def validate(self):
        # Get stock availability
        if self.source_warehouse and self.gift_item:
            self.available_stock = frappe.db.get_value("Bin",
                {"item_code": self.gift_item, "warehouse": self.source_warehouse},
                "actual_qty"
            ) or 0
            
        if self.requesting_warehouse and self.gift_item:
            self.current_stock_requesting = frappe.db.get_value("Bin",
                {"item_code": self.gift_item, "warehouse": self.requesting_warehouse},
                "actual_qty"
            ) or 0
        
        # Validate quantity
        if self.quantity and self.available_stock and self.quantity > self.available_stock:
            frappe.throw(_("Requested quantity {0} exceeds available stock {1} at source pump").format(
                self.quantity, self.available_stock
            ))
    
    def on_submit(self):
        """Create Stock Entry on approval"""
        if self.status == "Approved" and not self.stock_entry:
            self.create_stock_entry()
    
    def create_stock_entry(self):
        """Create Material Transfer Stock Entry"""
        stock_entry = frappe.get_doc({
            "doctype": "Stock Entry",
            "stock_entry_type": "Material Transfer",
            "is_gift_transfer": 1,
            "from_pump": self.source_pump,
            "to_pump": self.requesting_pump,
            "transfer_notes": f"Gift Stock Request: {self.name}\n{self.notes or ''}",
            "items": [{
                "item_code": self.gift_item,
                "qty": self.quantity,
                "s_warehouse": self.source_warehouse,
                "t_warehouse": self.requesting_warehouse
            }]
        })
        
        stock_entry.insert()
        stock_entry.submit()
        
        # Update reference
        self.db_set("stock_entry", stock_entry.name)
        self.db_set("status", "Completed")
        
        frappe.msgprint(_("Stock Entry {0} created successfully").format(
            frappe.utils.get_link_to_form("Stock Entry", stock_entry.name)
        ))
