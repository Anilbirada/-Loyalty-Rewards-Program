"""
CLP - Customer Loyalty Program (Lightweight Local Preview Server)
Runs natively with standard Python on Windows.
Requires 0 extra disk space, 0 BIOS changes, and ~25 MB RAM.
"""

import http.server
import socketserver
import json
import os
import sys
import webbrowser
from datetime import datetime

PORT = int(os.environ.get("PORT", 8000))
HOST = os.environ.get("HOST", "0.0.0.0")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHECK_HTML_PATH = os.path.join(BASE_DIR, "clp", "www", "loyality", "check.html")

# Mock database for instant testing
MOCK_CUSTOMERS = {
    "MH12AB1234": {
        "name": "CUST-0001",
        "customer_name": "Rahul Sharma",
        "vehicle_number": "MH12AB1234",
        "mobile_number": "9876543210",
        "current_cycle_liters": 145.5,
        "total_liters_purchased": 650.0,
        "total_gifts_received": 3,
        "registration_date": "2025-01-15",
        "purchases": [
            {
                "purchase_date": "2026-10-10 14:30:00",
                "liters": 45.0,
                "amount": 4725.0,
                "fuel_type": "Petrol",
                "petrol_pump": "N.K Sindol Petroleum - Highway Station"
            },
            {
                "purchase_date": "2026-09-28 10:15:00",
                "liters": 50.5,
                "amount": 5302.5,
                "fuel_type": "Petrol",
                "petrol_pump": "N.K Sindol Petroleum - Highway Station"
            },
            {
                "purchase_date": "2026-09-12 18:45:00",
                "liters": 50.0,
                "amount": 5250.0,
                "fuel_type": "Petrol",
                "petrol_pump": "N.K Sindol Petroleum - City Center"
            }
        ],
        "redemptions": [
            {
                "name": "RED-2026-001",
                "redemption_date": "2026-09-15 16:20:00",
                "petrol_pump": "N.K Sindol Petroleum - Highway Station",
                "total_points": 200,
                "items": [
                    {
                        "gift_item": "GIFT-01",
                        "item_name": "Stainless Steel Thermos Flask",
                        "points_required": 200
                    }
                ]
            }
        ]
    },
    "KA01CD5678": {
        "name": "CUST-0002",
        "customer_name": "Priya Patel",
        "vehicle_number": "KA01CD5678",
        "mobile_number": "9811223344",
        "current_cycle_liters": 82.0,
        "total_liters_purchased": 320.0,
        "total_gifts_received": 1,
        "registration_date": "2025-06-20",
        "purchases": [
            {
                "purchase_date": "2026-10-12 11:10:00",
                "liters": 35.0,
                "amount": 3675.0,
                "fuel_type": "Diesel",
                "petrol_pump": "N.K Sindol Petroleum - City Center"
            },
            {
                "purchase_date": "2026-09-30 16:40:00",
                "liters": 47.0,
                "amount": 4935.0,
                "fuel_type": "Diesel",
                "petrol_pump": "N.K Sindol Petroleum - Highway Station"
            }
        ],
        "redemptions": [
            {
                "name": "RED-2026-002",
                "redemption_date": "2026-08-10 12:00:00",
                "petrol_pump": "N.K Sindol Petroleum - City Center",
                "total_points": 100,
                "items": [
                    {
                        "gift_item": "GIFT-02",
                        "item_name": "Car Emergency Toolkit",
                        "points_required": 100
                    }
                ]
            }
        ]
    }
}


class MockFrappeHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        # Route root or check path to check.html
        path = self.path.split('?')[0]
        if path in ['/', '/check', '/loyality', '/loyality/check.html', '/index.html']:
            self.serve_check_page()
            return
        
        super().do_GET()

    def serve_check_page(self):
        if not os.path.exists(CHECK_HTML_PATH):
            self.send_error(404, "check.html not found")
            return

        with open(CHECK_HTML_PATH, "r", encoding="utf-8") as f:
            html = f.read()

        # Inject a handy test helper banner at the top of the card
        helper_banner = """
        <div style="background: #e8f4fd; border: 1px solid #b6d4fe; border-radius: 8px; padding: 12px 16px; margin-bottom: 20px; font-size: 14px; color: #084298;">
            <strong><i class="fas fa-info-circle"></i> Demo Mode Active:</strong> You can test with:
            <ul style="margin: 6px 0 0 20px; padding: 0;">
                <li>Vehicle: <code style="background: #fff; padding: 2px 6px; border-radius: 4px; cursor: pointer; border: 1px solid #ccc;" onclick="document.getElementById('vehicleNumber').value='MH12AB1234'; document.getElementById('vehicleRadio').click();">MH12AB1234</code> or Mobile: <code style="background: #fff; padding: 2px 6px; border-radius: 4px; cursor: pointer; border: 1px solid #ccc;" onclick="document.getElementById('mobileNumber').value='9876543210'; document.getElementById('mobileRadio').click();">9876543210</code> (Rahul Sharma - 145.5L)</li>
                <li>Vehicle: <code style="background: #fff; padding: 2px 6px; border-radius: 4px; cursor: pointer; border: 1px solid #ccc;" onclick="document.getElementById('vehicleNumber').value='KA01CD5678'; document.getElementById('vehicleRadio').click();">KA01CD5678</code> or Mobile: <code style="background: #fff; padding: 2px 6px; border-radius: 4px; cursor: pointer; border: 1px solid #ccc;" onclick="document.getElementById('mobileNumber').value='9811223344'; document.getElementById('mobileRadio').click();">9811223344</code> (Priya Patel - 82L)</li>
                <li><em>Or enter any other vehicle/mobile number to see a newly registered customer test profile!</em></li>
            </ul>
        </div>
        """
        # Inject right after <div class="search-card">
        if '<div class="search-card">' in html:
            html = html.replace('<div class="search-card">', '<div class="search-card">\n' + helper_banner)

        content = html.encode('utf-8')
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_POST(self):
        # Handle the Frappe API endpoint
        if self.path.startswith('/api/method/clp.api.check_loyalty_points'):
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                payload = json.loads(post_data.decode('utf-8'))
            except Exception:
                payload = {}

            vehicle = payload.get('vehicle', '').strip().upper()
            mobile = payload.get('mobile', '').strip()

            result = {
                'found': False,
                'error': '',
                'customer': None,
                'purchases': [],
                'redemptions': []
            }

            matched = None
            for key, cust in MOCK_CUSTOMERS.items():
                if vehicle and (cust['vehicle_number'].upper() == vehicle):
                    matched = cust
                    break
                if mobile and (cust['mobile_number'] == mobile):
                    matched = cust
                    break

            if matched:
                result['found'] = True
                result['customer'] = {
                    'name': matched['name'],
                    'customer_name': matched['customer_name'],
                    'vehicle_number': matched['vehicle_number'],
                    'mobile_number': matched['mobile_number'],
                    'current_cycle_liters': matched['current_cycle_liters'],
                    'total_liters_purchased': matched['total_liters_purchased'],
                    'total_gifts_received': matched['total_gifts_received'],
                    'registration_date': matched['registration_date']
                }
                result['purchases'] = matched.get('purchases', [])
                result['redemptions'] = matched.get('redemptions', [])
            else:
                # If searching for another number, dynamically generate a customer so user can see it works!
                if vehicle or mobile:
                    clean_v = vehicle if vehicle else "KA05XY9999"
                    clean_m = mobile if mobile else "9900112233"
                    result['found'] = True
                    result['customer'] = {
                        'name': "CUST-DEMO",
                        'customer_name': "Demo Loyalty Customer",
                        'vehicle_number': clean_v,
                        'mobile_number': clean_m,
                        'current_cycle_liters': 95.0,
                        'total_liters_purchased': 450.0,
                        'total_gifts_received': 2,
                        'registration_date': "2026-03-01"
                    }
                    result['purchases'] = [
                        {
                            "purchase_date": "2026-10-14 09:30:00",
                            "liters": 40.0,
                            "amount": 4200.0,
                            "fuel_type": "Petrol",
                            "petrol_pump": "N.K Sindol Petroleum"
                        }
                    ]
                    result['redemptions'] = [
                        {
                            "name": "RED-DEMO-01",
                            "redemption_date": "2026-09-01 15:00:00",
                            "petrol_pump": "N.K Sindol Petroleum",
                            "total_points": 100,
                            "items": [
                                {
                                    "gift_item": "GIFT-DEMO",
                                    "item_name": "Air Pump & Gauge",
                                    "points_required": 100
                                }
                            ]
                        }
                    ]
                else:
                    result['error'] = "Please provide either vehicle number or mobile number."

            response_payload = json.dumps({'message': result}).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(response_payload)))
            self.end_headers()
            self.wfile.write(response_payload)
            return

        self.send_error(404, "Endpoint Not Found")


def run_server():
    socketserver.TCPServer.allow_reuse_address = True
    server_address = (HOST, PORT)
    with socketserver.TCPServer(server_address, MockFrappeHandler) as httpd:
        print(f"===========================================================")
        print(f" Customer Loyalty Program (CLP) - Running on {HOST}:{PORT}")
        print(f" Running at: http://localhost:{PORT}")
        print(f" Memory usage: ~25 MB | Zero installation needed!")
        print(f" Press Ctrl+C to stop.")
        print(f"===========================================================")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")


if __name__ == '__main__':
    run_server()
