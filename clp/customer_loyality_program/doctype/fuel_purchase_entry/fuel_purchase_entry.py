# Copyright (c) 2025, Aman Boora and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class FuelPurchaseEntry(Document):
    def validate(self):
        """Validate petrol pump is selected"""
        if not self.petrol_pump:
            frappe.throw(_("Please select Petrol Pump Location"))
        
        if not self.customer:
            frappe.throw(_("Please select Customer"))
        
        if not self.liters or self.liters <= 0:
            frappe.throw(_("Liters must be greater than 0"))
    
    def after_insert(self):
        """Update customer liters immediately after insertion"""
        self.update_customer_liters()
    
    def on_submit(self):
        """Show customer status after submission"""
        self.show_customer_status()
    
    def on_cancel(self):
        """Reverse customer liters on cancellation"""
        self.reverse_customer_liters()
    
    def update_customer_liters(self):
        """Add purchased liters to customer record - ALLOW NEGATIVE"""
        if not self.customer or not self.liters:
            return
        
        customer = frappe.get_doc("Loyalty Customer", self.customer)
        
        # Add liters - no restriction on negative
        customer.total_liters_purchased += self.liters
        customer.current_cycle_liters += self.liters
        
        customer.flags.ignore_permissions = True
        customer.save()
        frappe.db.commit()
        
        frappe.msgprint(
            _("✅ Fuel purchase recorded!<br><br>Customer: <strong>{0}</strong><br>Liters Added: <strong>{1}L</strong><br>New Balance: <strong>{2}L</strong>").format(
                customer.customer_name,
                self.liters,
                customer.current_cycle_liters
            ),
            title=_("Purchase Updated"),
            indicator='green'
        )
    
    def reverse_customer_liters(self):
        """Subtract liters when entry is cancelled"""
        if not self.customer or not self.liters:
            return
        
        customer = frappe.get_doc("Loyalty Customer", self.customer)
        
        # Reverse the addition
        customer.total_liters_purchased -= self.liters
        customer.current_cycle_liters -= self.liters
        
        customer.flags.ignore_permissions = True
        customer.save()
        frappe.db.commit()
        
        frappe.msgprint(
            _("Purchase cancelled and customer balance reversed"),
            indicator='blue'
        )
    
    def show_customer_status(self):
        """Show customer loyalty status after purchase"""
        customer = frappe.get_doc("Loyalty Customer", self.customer)
        
        frappe.msgprint(
            _("Purchase confirmed for <strong>{0}</strong><br><br>Current Loyalty: <strong>{1}L</strong><br>Total Purchases: <strong>{2}L</strong>").format(
                customer.customer_name,
                customer.current_cycle_liters,
                customer.total_liters_purchased
            ),
            title=_("Customer Status"),
            indicator='blue'
        )
