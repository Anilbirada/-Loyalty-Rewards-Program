"""
CLP Application QA Automated Test Suite
Executes comprehensive static, schema, business logic, security, and integration checks.
"""

import unittest
import json
import os
import re
import urllib.request
import urllib.error

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLP_DIR = os.path.join(BASE_DIR, "clp")


class TestDocTypeSchemaIntegrity(unittest.TestCase):
    """Phase 1 & 4: Schema and JSON configuration checks"""

    def test_no_duplicate_fields_in_fuel_purchase_entry(self):
        """Verify Fuel Purchase Entry DocType has no duplicate field definitions"""
        path = os.path.join(CLP_DIR, "customer_loyality_program", "doctype", "fuel_purchase_entry", "fuel_purchase_entry.json")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        fields = [f.get("fieldname") for f in data.get("fields", []) if f.get("fieldname")]
        duplicates = [x for x in set(fields) if fields.count(x) > 1]
        self.assertEqual(duplicates, [], f"Duplicate fields found in fuel_purchase_entry.json: {duplicates}")

    def test_no_duplicate_fields_in_gift_redemption(self):
        """Verify Gift Redemption DocType has no duplicate field definitions"""
        path = os.path.join(CLP_DIR, "customer_loyality_program", "doctype", "gift_redemption", "gift_redemption.json")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        fields = [f.get("fieldname") for f in data.get("fields", []) if f.get("fieldname")]
        duplicates = [x for x in set(fields) if fields.count(x) > 1]
        self.assertEqual(duplicates, [], f"Duplicate fields found in gift_redemption.json: {duplicates}")

    def test_naming_rule_consistency_fuel_purchase(self):
        """Verify autoname format matches naming_rule in Fuel Purchase Entry"""
        path = os.path.join(CLP_DIR, "customer_loyality_program", "doctype", "fuel_purchase_entry", "fuel_purchase_entry.json")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        autoname = data.get("autoname", "")
        naming_rule = data.get("naming_rule", "")
        if autoname.startswith("format:"):
            self.assertNotEqual(naming_rule, "By fieldname", "autoname is format-based but naming_rule is set to 'By fieldname'")

    def test_naming_rule_consistency_gift_redemption(self):
        """Verify autoname format matches naming_rule in Gift Redemption"""
        path = os.path.join(CLP_DIR, "customer_loyality_program", "doctype", "gift_redemption", "gift_redemption.json")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        autoname = data.get("autoname", "")
        naming_rule = data.get("naming_rule", "")
        if autoname.startswith("format:"):
            self.assertNotEqual(naming_rule, "By fieldname", "autoname is format-based but naming_rule is set to 'By fieldname'")


class TestSecurityVulnerabilities(unittest.TestCase):
    """Phase 3: Security & Code Safety Audit"""

    def test_no_sql_injection_in_get_gift_stock_data(self):
        """Check for unparameterized SQL string formatting in get_gift_stock_data"""
        api_path = os.path.join(CLP_DIR, "api.py")
        with open(api_path, "r", encoding="utf-8") as f:
            code = f.read()
        
        # Check if f-string interpolation is used with pump or item in get_gift_stock_data
        vuln_pattern = re.search(r"def get_gift_stock_data.*?conditions \+= f\".*?\{pump\}.*?\"", code, re.DOTALL)
        self.assertIsNone(vuln_pattern, "SQL Injection vulnerability detected in get_gift_stock_data: unparameterized pump filter")

    def test_no_dom_xss_in_qr_redirect(self):
        """Check for unescaped URL query parameter injection into DOM HTML in qr_redirect.js"""
        js_path = os.path.join(CLP_DIR, "customer_loyality_program", "page", "qr_redirect", "qr_redirect.js")
        with open(js_path, "r", encoding="utf-8") as f:
            js = f.read()
        
        vuln_xss = "${customer_id}" in js and "escape_html" not in js and "xss_sanitise" not in js
        self.assertFalse(vuln_xss, "DOM XSS vulnerability detected in qr_redirect.js: unescaped customer_id injected into HTML dialog")

    def test_public_loyalty_api_csrf_and_rate_limiting(self):
        """Verify check_loyalty_points has rate limiting or does not disable CSRF globally"""
        api_path = os.path.join(CLP_DIR, "api.py")
        with open(api_path, "r", encoding="utf-8") as f:
            code = f.read()
        
        has_csrf_disabled = "frappe.flags.ignore_csrf = True" in code
        self.assertFalse(has_csrf_disabled, "CSRF protection explicitly bypassed on public loyalty endpoint")


class TestDatabaseAndReportIntegrity(unittest.TestCase):
    """Phase 4 & 2G: Report & Database Schema Consistency"""

    def test_customer_loyalty_summary_report_columns_exist(self):
        """Verify all columns queried in customer_loyalty_summary exist in Loyalty Customer DocType"""
        customer_json_path = os.path.join(CLP_DIR, "customer_loyality_program", "doctype", "loyalty_customer", "loyalty_customer.json")
        with open(customer_json_path, "r", encoding="utf-8") as f:
            customer_doc = json.load(f)
        
        customer_fields = set(f.get("fieldname") for f in customer_doc.get("fields", []))
        # Standard fields in Frappe
        standard_fields = {"name", "owner", "creation", "modified", "modified_by", "docstatus", "idx"}
        valid_columns = customer_fields.union(standard_fields)

        report_py_path = os.path.join(CLP_DIR, "customer_loyality_program", "report", "customer_loyalty_summary", "customer_loyalty_summary.py")
        with open(report_py_path, "r", encoding="utf-8") as f:
            report_code = f.read()
        
        # Check query in get_data
        match = re.search(r"SELECT\s+(.*?)\s+FROM `tabLoyalty Customer`", report_code, re.DOTALL)
        self.assertIsNotNone(match, "Could not find SELECT query in customer_loyalty_summary.py")
        raw_cols = match.group(1).split(",")
        queried_cols = []
        for col in raw_cols:
            col = col.strip()
            if " as " in col:
                col = col.split(" as ")[0].strip()
            if col:
                queried_cols.append(col)

        missing_cols = [c for c in queried_cols if c not in valid_columns]
        self.assertEqual(missing_cols, [], f"Query references non-existent columns in tabLoyalty Customer: {missing_cols}")

    def test_no_duplicate_function_definitions_in_api(self):
        """Verify clp/api.py has no duplicate function names that overwrite each other"""
        api_path = os.path.join(CLP_DIR, "api.py")
        with open(api_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        functions = []
        for line in lines:
            m = re.match(r"^def\s+([a-zA-Z0-9_]+)\(", line)
            if m:
                functions.append(m.group(1))
        
        duplicates = [x for x in set(functions) if functions.count(x) > 1]
        self.assertEqual(duplicates, [], f"Duplicate function definitions found in clp/api.py: {duplicates}")


class TestBusinessLogicAndTransactionIntegrity(unittest.TestCase):
    """Phase 2 & 4: Controller and Lifecycle Hooks Audit"""

    def test_fuel_purchase_entry_lifecycle_hook_timing(self):
        """Fuel purchase points should only update on submit (docstatus=1), not on draft insertion (after_insert)"""
        ctrl_path = os.path.join(CLP_DIR, "customer_loyality_program", "doctype", "fuel_purchase_entry", "fuel_purchase_entry.py")
        with open(ctrl_path, "r", encoding="utf-8") as f:
            code = f.read()
        
        self.assertNotIn("def after_insert", code, 
                         "Points awarded on after_insert (draft). Unsubmitted draft deletion will corrupt customer balance!")

    def test_gift_redemption_atomicity_and_commit(self):
        """frappe.db.commit() must not be called before Stock Entry creation in gift_redemption"""
        ctrl_path = os.path.join(CLP_DIR, "customer_loyality_program", "doctype", "gift_redemption", "gift_redemption.py")
        with open(ctrl_path, "r", encoding="utf-8") as f:
            code = f.read()
        
        # Check order of frappe.db.commit() vs create_gift_stock_entry
        commit_pos = code.find("frappe.db.commit()")
        stock_entry_pos = code.find("self.create_gift_stock_entry()")
        
        if commit_pos != -1 and stock_entry_pos != -1:
            self.assertLess(stock_entry_pos, commit_pos, 
                            "Premature DB commit before Stock Entry creation. Failed stock creation will leave deducted points committed!")

    def test_gift_redemption_respects_allow_negative_balance_setting(self):
        """Gift redemption should respect the allow_negative_balance flag instead of unconditional negative balance"""
        ctrl_path = os.path.join(CLP_DIR, "customer_loyality_program", "doctype", "gift_redemption", "gift_redemption.py")
        with open(ctrl_path, "r", encoding="utf-8") as f:
            code = f.read()
        
        self.assertIn("self.allow_negative_balance", code, 
                      "gift_redemption.py does not check self.allow_negative_balance; negative balance is permitted unconditionally!")


class TestLiveApiEndpoint(unittest.TestCase):
    """Phase 2A & 2H: Live Verification against running local server"""

    SERVER_URL = "http://127.0.0.1:8000/api/method/clp.api.check_loyalty_points"

    def test_live_search_by_vehicle(self):
        payload = json.dumps({"vehicle": "MH12AB1234"}).encode("utf-8")
        req = urllib.request.Request(self.SERVER_URL, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req) as response:
            self.assertEqual(response.status, 200)
            data = json.loads(response.read().decode("utf-8"))
            self.assertTrue(data.get("message", {}).get("found"))
            self.assertEqual(data["message"]["customer"]["vehicle_number"], "MH12AB1234")
            self.assertEqual(data["message"]["customer"]["current_cycle_liters"], 145.5)

    def test_live_search_by_mobile(self):
        payload = json.dumps({"mobile": "9876543210"}).encode("utf-8")
        req = urllib.request.Request(self.SERVER_URL, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req) as response:
            self.assertEqual(response.status, 200)
            data = json.loads(response.read().decode("utf-8"))
            self.assertTrue(data.get("message", {}).get("found"))
            self.assertEqual(data["message"]["customer"]["mobile_number"], "9876543210")

    def test_live_search_empty_input(self):
        payload = json.dumps({}).encode("utf-8")
        req = urllib.request.Request(self.SERVER_URL, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req) as response:
            self.assertEqual(response.status, 200)
            data = json.loads(response.read().decode("utf-8"))
            self.assertFalse(data.get("message", {}).get("found"))
            self.assertIn("Please provide", data.get("message", {}).get("error", ""))


if __name__ == "__main__":
    unittest.main()
