# Copyright (c) 2025, Aman Boora and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class GiftRedemption(Document):
    def before_insert(self):
        """Auto-set gift_given_by"""
        if not self.gift_given_by:
            self.gift_given_by = frappe.session.user
    
    def before_validate(self):
        """Prevent validation on cancel/update after submit"""
        if self.docstatus == 1 and self.flags.ignore_validate:
            return
    
    def validate(self):
        """Validate redemption - ALLOW NEGATIVE BALANCE"""
        # Skip validation if document is being cancelled
        if self.docstatus == 2:
            return
            
        if not self.gift_given_by:
            self.gift_given_by = frappe.session.user
        
        # Validate we have items
        if not self.items or len(self.items) == 0:
            frappe.throw(_("Please add at least one gift item"))
        
        # Customer validation
        if self.customer:
            customer = frappe.get_doc("Loyalty Customer", self.customer)
            self.liters_accumulated = customer.current_cycle_liters
            
            # Calculate total points
            total_points = 0
            for item in self.items:
                if not item.points_required or item.points_required <= 0:
                    frappe.throw(_("Points required must be greater than 0 for {0}").format(item.gift_item))
                
                total_points += item.points_required
                
                # Validate stock for each item
                if self.warehouse and item.gift_item:
                    stock = frappe.db.get_value("Bin", {
                        "item_code": item.gift_item,
                        "warehouse": self.warehouse
                    }, "actual_qty") or 0
                    
                    item.available_stock = stock
                    item.stock_after_redeem = stock - 1
                    
                    if stock < 1:
                        frappe.throw(
                            _("Gift item <strong>{0}</strong> is out of stock<br>Available: {1} units").format(
                                item.item_name or item.gift_item, stock
                            )
                        )
            
            self.total_points = total_points
    
    def on_submit(self):
        """Update customer and create stock entry - ALLOW NEGATIVE"""
        if not self.customer or not self.total_points or self.total_points <= 0:
            frappe.throw(_("Customer and items required"))
        
        # Update customer using db_set to avoid validation issues
        customer = frappe.get_doc("Loyalty Customer", self.customer)
        old_points = customer.current_cycle_liters
        
        new_points = customer.current_cycle_liters - self.total_points
        new_gifts = customer.total_gifts_received + len(self.items)
        
        # Direct database update - bypasses validation
        frappe.db.set_value("Loyalty Customer", self.customer, {
            "current_cycle_liters": new_points,
            "total_gifts_received": new_gifts,
            "last_gift_date": frappe.utils.today()
        }, update_modified=True)
        
        frappe.db.commit()
        
        # Create stock entry for all items
        self.create_gift_stock_entry()
        
        # Success message
        new_balance = new_points
        balance_display = f"{new_balance}L" if new_balance >= 0 else f"<span style='color:red;font-weight:bold;'>{new_balance}L (Negative)</span>"
        
        frappe.msgprint(
            _("🎁 {0} gift(s) redeemed successfully!<br><br>Customer: <strong>{1}</strong><br>Previous Points: {2}L<br>New Balance: {3}").format(
                len(self.items), 
                customer.customer_name,
                old_points, 
                balance_display
            ),
            title=_("Redemption Complete"),
            indicator='green'
        )
    
    def on_cancel(self):
        """Reverse redemption - Use direct DB update"""
        if self.customer and self.total_points:
            # Get current customer values
            customer = frappe.get_doc("Loyalty Customer", self.customer)
            
            # Calculate new values
            new_points = customer.current_cycle_liters + self.total_points
            new_gifts = max(0, customer.total_gifts_received - len(self.items))
            
            # Direct database update - bypasses "Cannot Update After Submit"
            frappe.db.set_value("Loyalty Customer", self.customer, {
                "current_cycle_liters": new_points,
                "total_gifts_received": new_gifts
            }, update_modified=False)
            
            frappe.db.commit()
            
            frappe.msgprint(
                _("✅ Gift redemption cancelled<br><br>Customer balance restored to: <strong>{0}L</strong>").format(new_points),
                title=_("Cancellation Complete"),
                indicator='blue'
            )
        
        # Cancel stock entry
        if self.stock_entry:
            try:
                se = frappe.get_doc("Stock Entry", self.stock_entry)
                if se.docstatus == 1:
                    se.cancel()
                    frappe.msgprint(_("Stock entry cancelled"), indicator='blue')
            except Exception as e:
                frappe.log_error(f"Failed to cancel stock entry: {e}", "Gift Redemption Cancel")
    
    def on_trash(self):
        """Prevent deletion if submitted"""
        if self.docstatus == 1:
            frappe.throw(_("Cannot delete submitted Gift Redemption. Please cancel it first."))
    
    def create_gift_stock_entry(self):
        """Create Material Issue stock entry for all gift items"""
        try:
            stock_items = []
            for item in self.items:
                stock_items.append({
                    "item_code": item.gift_item,
                    "qty": 1,
                    "s_warehouse": self.warehouse,
                    "cost_center": frappe.defaults.get_defaults().get("cost_center")
                })
            
            se = frappe.get_doc({
                "doctype": "Stock Entry",
                "stock_entry_type": "Material Issue",
                "company": frappe.defaults.get_defaults().get("company"),
                "posting_date": self.redemption_date or frappe.utils.today(),
                "remarks": f"Gift Redemption {self.name} - {self.customer} - {len(self.items)} items",
                "items": stock_items
            })
            
            se.flags.ignore_permissions = True
            se.insert()
            se.submit()
            self.db_set("stock_entry", se.name, update_modified=False)
            
        except Exception as e:
            frappe.log_error(f"Stock Entry error: {str(e)}", "Gift Redemption")
            frappe.throw(_("Failed to create stock entry: {0}").format(str(e)))
