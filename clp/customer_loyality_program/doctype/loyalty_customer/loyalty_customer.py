# Copyright (c) 2025, Aman Boora and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class LoyaltyCustomer(Document):
    
    def autoname(self):
        """Use scanned QR code as name if provided, else use naming_series"""
        if self.get("__qr_code"):
            # QR code was scanned - use it as the name
            self.name = self.get("__qr_code")
        else:
            # Manual entry - use naming_series
            from frappe.model.naming import make_autoname
            self.name = make_autoname(self.naming_series, doc=self)
            
    def before_insert(self):
        """Auto-set created_by_user"""
        if not self.created_by_user:
            self.created_by_user = frappe.session.user
        
        # Ensure vehicle number is uppercase
        if self.vehicle_number:
            self.vehicle_number = self.vehicle_number.upper()
    
    def validate(self):
        """Validate customer data"""
        # Ensure created_by is set
        if not self.created_by_user:
            self.created_by_user = frappe.session.user
        
        # Uppercase vehicle number
        if self.vehicle_number:
            self.vehicle_number = self.vehicle_number.upper()
        
        # Validate unique identifiers
        self.validate_unique_vehicle()
        self.validate_unique_mobile()
    
    def validate_unique_vehicle(self):
        """Ensure vehicle number is unique"""
        if self.vehicle_number:
            exists = frappe.db.exists("Loyalty Customer", {
                "vehicle_number": self.vehicle_number,
                "name": ["!=", self.name]
            })
            if exists:
                frappe.throw(f"Vehicle number {self.vehicle_number} is already registered with another customer")
    
    def validate_unique_mobile(self):
        """Ensure mobile number is unique"""
        if self.mobile_number:
            exists = frappe.db.exists("Loyalty Customer", {
                "mobile_number": self.mobile_number,
                "name": ["!=", self.name]
            })
            if exists:
                frappe.throw(f"Mobile number {self.mobile_number} is already registered with another customer")
