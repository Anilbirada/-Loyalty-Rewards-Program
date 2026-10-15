# Copyright (c) 2025, Aman Boora and contributors
# For license information, please see license.txt

import frappe
import qrcode
from io import BytesIO
import base64
from frappe import _
from urllib.parse import quote

@frappe.whitelist()
def get_customers_for_search(doctype, txt, searchfield, start, page_len, filters):
    """Enhanced search showing ID, name, vehicle, mobile"""
    return frappe.db.sql("""
        SELECT 
            name,
            CONCAT(name, ' - ', customer_name, ' - ', vehicle_number) as label
        FROM `tabLoyalty Customer`
        WHERE 
            status = 'Active'
            AND (
                name LIKE %(txt)s
                OR customer_name LIKE %(txt)s
                OR vehicle_number LIKE %(txt)s
                OR mobile_number LIKE %(txt)s
            )
        ORDER BY name DESC
        LIMIT %(page_len)s OFFSET %(start)s
    """, {
        'txt': f'%{txt}%',
        'start': start,
        'page_len': page_len
    })

@frappe.whitelist()
def check_customer_exists(customer_id):
    """Check if customer exists - SERVER SIDE"""
    if frappe.db.exists("Loyalty Customer", customer_id):
        customer = frappe.get_doc("Loyalty Customer", customer_id)
        return {
            "exists": True,
            "customer_id": customer.name,
            "customer_name": customer.customer_name,
            "vehicle_number": customer.vehicle_number,
            "mobile_number": customer.mobile_number,
            "current_cycle_liters": customer.current_cycle_liters,
            "total_gifts_received": customer.total_gifts_received
        }
    else:
        return {
            "exists": False,
            "customer_id": customer_id
        }

@frappe.whitelist()
def scan_and_process_qr(qr_data):
    """Process scanned QR code"""
    # Extract customer ID from URL
    if '?id=' in qr_data:
        customer_id = qr_data.split('?id=')[1]
    else:
        customer_id = qr_data.split('/')[-1]
    
    # Use check_customer_exists function
    return check_customer_exists(customer_id)

@frappe.whitelist()
def generate_qr_image(customer_id):
    """Generate QR code for customer"""
    site_url = frappe.utils.get_url()
    qr_data = f"{site_url}/app/qr-redirect?id={customer_id}"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return {"image": f"data:image/png;base64,{img_str}"}

@frappe.whitelist()
def bulk_generate_qr_codes(start_num, count, output_dir="/tmp/qr_codes"):
    """Generate multiple QR codes"""
    import os
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    site_url = frappe.utils.get_url()
    generated = []
    
    for i in range(int(count)):
        customer_id = str(int(start_num) + i)
        qr_data = f"{site_url}/app/qr-redirect?id={customer_id}"
        
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        file_path = os.path.join(output_dir, f"qr_{customer_id}.png")
        img.save(file_path)
        generated.append(file_path)
    
    return {
        "success": True,
        "count": len(generated),
        "directory": output_dir
    }

@frappe.whitelist()
def get_pump_gift_stock(petrol_pump):
    """Get total actual gift stock at pump from Bin table"""
    pump = frappe.get_doc("Petrol Pump Location", petrol_pump)
    
    if not pump.warehouse:
        return {
            "pump_name": pump.pump_name,
            "qty": 0
        }
    
    if not pump.gift_items or len(pump.gift_items) == 0:
        return {
            "pump_name": pump.pump_name,
            "qty": 0
        }
    
    # Get actual stock from Bin table for all gift items
    total_stock = 0
    
    for gift_item in pump.gift_items:
        stock = frappe.db.get_value("Bin", {
            "item_code": gift_item.gift_item,
            "warehouse": pump.warehouse
        }, "actual_qty") or 0
        
        total_stock += float(stock)
    
    return {
        "pump_name": pump.pump_name,
        "qty": total_stock
    }

@frappe.whitelist()
def get_item_stock_at_warehouse(item_code, warehouse):
    """Get actual stock quantity of an item at a warehouse"""
    stock = frappe.db.get_value("Bin", 
        {
            "item_code": item_code, 
            "warehouse": warehouse
        }, 
        "actual_qty"
    )
    
    return float(stock) if stock else 0.0

@frappe.whitelist()
def get_top_customers_chart(limit=10):
    """Get top customers by loyalty points for chart"""
    data = frappe.db.sql("""
        SELECT 
            customer_name as name,
            current_cycle_liters as value
        FROM `tabLoyalty Customer`
        WHERE status = 'Active'
        ORDER BY current_cycle_liters DESC
        LIMIT %s
    """, (int(limit),), as_dict=1)
    
    labels = [d.name for d in data]
    values = [d.value for d in data]
    
    return {
        "labels": labels,
        "datasets": [
            {
                "name": "Loyalty Points (L)",
                "values": values
            }
        ],
        "type": "bar"
    }

@frappe.whitelist()
def get_monthly_fuel_sales(months=6):
    """Get monthly fuel sales for chart"""
    from frappe.utils import add_months, today, formatdate
    
    start_date = add_months(today(), -int(months))
    
    data = frappe.db.sql("""
        SELECT 
            DATE_FORMAT(purchase_date, '%%Y-%%m') as month,
            SUM(liters) as total_liters,
            COUNT(*) as total_purchases
        FROM `tabFuel Purchase Entry`
        WHERE docstatus = 1
        AND purchase_date >= %s
        GROUP BY DATE_FORMAT(purchase_date, '%%Y-%%m')
        ORDER BY month
    """, (start_date,), as_dict=1)
    
    labels = [d.month for d in data]
    liters = [d.total_liters for d in data]
    purchases = [d.total_purchases for d in data]
    
    return {
        "labels": labels,
        "datasets": [
            {
                "name": "Liters Sold",
                "values": liters
            },
            {
                "name": "Number of Purchases",
                "values": purchases
            }
        ],
        "type": "line"
    }

@frappe.whitelist()
def get_customer_with_highest_points():
    """Get customer with highest loyalty points"""
    customer = frappe.db.sql("""
        SELECT 
            name as customer_id,
            customer_name,
            current_cycle_liters,
            vehicle_number,
            mobile_number
        FROM `tabLoyalty Customer`
        WHERE status = 'Active'
        ORDER BY current_cycle_liters DESC
        LIMIT 1
    """, as_dict=1)
    
    if customer:
        return customer[0]
    return {}
@frappe.whitelist()
def search_customer_for_scanner(search_text):
    """Enhanced search for QR scanner - ID, name, vehicle, mobile with partial matching"""
    if not search_text:
        frappe.throw(_("Please enter search text"))
    
    # Clean and prepare search text
    search_text = search_text.strip()
    search_pattern = f"%{search_text}%"
    
    customers = frappe.db.sql("""
        SELECT 
            name,
            customer_name,
            vehicle_number,
            mobile_number,
            current_cycle_liters,
            total_gifts_received
        FROM `tabLoyalty Customer`
        WHERE status = 'Active'
        AND (
            LOWER(name) LIKE LOWER(%(search)s)
            OR LOWER(customer_name) LIKE LOWER(%(search)s)
            OR LOWER(vehicle_number) LIKE LOWER(%(search)s)
            OR mobile_number LIKE %(search)s
        )
        ORDER BY 
            CASE 
                WHEN LOWER(name) = LOWER(%(exact)s) THEN 1
                WHEN LOWER(name) LIKE LOWER(%(search)s) THEN 2
                WHEN LOWER(customer_name) LIKE LOWER(%(search)s) THEN 3
                WHEN LOWER(vehicle_number) LIKE LOWER(%(search)s) THEN 4
                ELSE 5
            END,
            modified DESC
        LIMIT 20
    """, {"search": search_pattern, "exact": search_text}, as_dict=1)
    
    return customers


@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_pump_gift_items(doctype, txt, searchfield, start, page_len, filters):
    """Get gift items for selected pump - used in Link query"""
    petrol_pump = filters.get('petrol_pump')
    if not petrol_pump:
        return []
    
    return frappe.db.sql("""
        SELECT DISTINCT i.name, i.item_name
        FROM `tabItem` i
        INNER JOIN `tabPump Gift Item` pgi ON pgi.gift_item = i.name
        WHERE pgi.parent = %(pump)s
        AND (i.item_name LIKE %(txt)s OR i.name LIKE %(txt)s)
        ORDER BY i.item_name
        LIMIT %(start)s, %(page_len)s
    """, {
        'pump': petrol_pump,
        'txt': f'%{txt}%',
        'start': start,
        'page_len': page_len
    })


@frappe.whitelist()
def get_gift_item_points(petrol_pump, gift_item):
    """Get points required and available stock for gift item"""
    if not petrol_pump or not gift_item:
        return {"points_required": 0, "available_stock": 0}
    
    # Get points from Pump Gift Item
    points = frappe.db.get_value("Pump Gift Item", {
        "parent": petrol_pump,
        "gift_item": gift_item
    }, "points_required") or 0
    
    # Get warehouse from pump
    warehouse = frappe.db.get_value("Petrol Pump Location", petrol_pump, "warehouse")
    
    # Get stock from Bin
    stock = 0
    if warehouse:
        stock = frappe.db.get_value("Bin", {
            "item_code": gift_item,
            "warehouse": warehouse
        }, "actual_qty") or 0
    
    return {
        "points_required": points,
        "available_stock": stock
    }


@frappe.whitelist()
def get_available_gifts(petrol_pump):
    """Get all available gifts with stock for selected pump"""
    if not petrol_pump:
        return []
    
    warehouse = frappe.db.get_value("Petrol Pump Location", petrol_pump, "warehouse")
    
    gifts = frappe.db.sql("""
        SELECT 
            pgi.gift_item,
            i.item_name,
            pgi.points_required,
            COALESCE(b.actual_qty, 0) as available_stock
        FROM `tabPump Gift Item` pgi
        INNER JOIN `tabItem` i ON i.name = pgi.gift_item
        LEFT JOIN `tabBin` b ON b.item_code = pgi.gift_item AND b.warehouse = %(warehouse)s
        WHERE pgi.parent = %(pump)s
        ORDER BY i.item_name
    """, {
        'pump': petrol_pump,
        'warehouse': warehouse
    }, as_dict=1)
    
    return gifts
    
@frappe.whitelist()
def export_report_to_pdf(report_name, filters=None):
    """Export report to PDF"""
    from frappe.utils.pdf import get_pdf
    from frappe.desk.query_report import run
    
    if isinstance(filters, str):
        import json
        filters = json.loads(filters)
    
    # Get report data
    report = frappe.get_doc("Report", report_name)
    result = run(report_name, filters=filters)
    
    columns = result.get("columns", [])
    data = result.get("result", [])
    
    # Generate HTML
    html = frappe.render_template(
        "frappe/www/printview.html",
        {
            "title": report_name,
            "columns": columns,
            "data": data,
            "report_name": report_name,
            "filters": filters
        }
    )
    
    # Generate PDF
    pdf = get_pdf(html, {"orientation": "Landscape"})
    
    # Create file
    file_name = f"{report_name.replace(' ', '_')}.pdf"
    file_doc = frappe.get_doc({
        "doctype": "File",
        "file_name": file_name,
        "is_private": 1,
        "content": pdf
    })
    file_doc.save()
    
    return file_doc.file_url

@frappe.whitelist()
def get_gift_stock_data(pump=None, item=None, status=None):
    """Get gift stock data for management page"""
    conditions = ""
    
    if pump:
        conditions += f" AND ppl.name = '{pump}'"
    if item:
        conditions += f" AND pgi.gift_item = '{item}'"
    
    data = frappe.db.sql(f"""
        SELECT
            ppl.name as pump,
            ppl.pump_name,
            ppl.warehouse,
            pgi.gift_item as item_code,
            i.item_name,
            pgi.points_required,
            COALESCE(b.actual_qty, 0) as actual_qty
        FROM `tabPetrol Pump Location` ppl
        INNER JOIN `tabPump Gift Item` pgi ON pgi.parent = ppl.name
        INNER JOIN `tabItem` i ON i.name = pgi.gift_item
        LEFT JOIN `tabBin` b ON b.item_code = pgi.gift_item AND b.warehouse = ppl.warehouse
        WHERE ppl.is_active = 1 {conditions}
        ORDER BY ppl.pump_name, i.item_name
    """, as_dict=1)
    
    # Filter by status if specified
    if status:
        if status == 'in_stock':
            data = [d for d in data if d.actual_qty > 10]
        elif status == 'low_stock':
            data = [d for d in data if 0 < d.actual_qty <= 10]
        elif status == 'out_of_stock':
            data = [d for d in data if d.actual_qty <= 0]
    
    return data


@frappe.whitelist()
def adjust_gift_stock(item_code, warehouse, qty, action, reason):
    """Adjust gift stock - add or remove"""
    qty = float(qty)
    
    # Create Stock Entry
    stock_entry = frappe.get_doc({
        "doctype": "Stock Entry",
        "stock_entry_type": "Material Receipt" if action == "add" else "Material Issue",
        "company": frappe.defaults.get_defaults().company,
        "remarks": f"Gift Stock Adjustment: {reason}",
        "items": [{
            "item_code": item_code,
            "qty": qty,
            "t_warehouse": warehouse if action == "add" else None,
            "s_warehouse": warehouse if action == "remove" else None,
            "cost_center": frappe.db.get_value("Company", frappe.defaults.get_defaults().company, "cost_center")
        }]
    })
    
    stock_entry.insert()
    stock_entry.submit()
    
    return {
        "success": True,
        "stock_entry": stock_entry.name
    }


@frappe.whitelist()
def get_loyalty_dashboard_stats():
    """Get dashboard statistics"""
    from frappe.utils import today, add_days

    today_date = today()
    tomorrow = add_days(today_date, 1)

    total_customers = frappe.db.count("Loyalty Customer")
    active_customers = frappe.db.count("Loyalty Customer", {"status": "Active"})

    total_points = frappe.db.sql("""
        SELECT COALESCE(SUM(current_cycle_liters), 0) as total
        FROM `tabLoyalty Customer`
        WHERE status = 'Active'
    """)[0][0] or 0

    total_gifts = frappe.db.sql("""
        SELECT COALESCE(SUM(total_gifts_received), 0) as total
        FROM `tabLoyalty Customer`
    """)[0][0] or 0

    today_purchases = frappe.db.count("Fuel Purchase Entry", [
        ["purchase_date", ">=", today_date],
        ["purchase_date", "<", tomorrow],
        ["docstatus", "=", 1],
    ])

    today_redemptions = frappe.db.count("Gift Redemption", [
        ["redemption_date", ">=", today_date],
        ["redemption_date", "<", tomorrow],
        ["docstatus", "=", 1],
    ])
    
    return {
        "total_customers": total_customers,
        "active_customers": active_customers,
        "total_points": round(total_points, 2),
        "total_gifts": total_gifts,
        "today_purchases": today_purchases,
        "today_redemptions": today_redemptions
    }

@frappe.whitelist()
def create_quick_sale(customer_name, mobile_number, vehicle_number, petrol_pump, fuel_type, liters, amount):
    """Create quick sale for walk-in customer"""
    
    # Check if customer already exists
    existing = frappe.db.exists("Loyalty Customer", {
        "vehicle_number": vehicle_number.upper(),
        "mobile_number": mobile_number
    })
    
    if existing:
        customer_id = existing
        customer_doc = frappe.get_doc("Loyalty Customer", customer_id)
    else:
        # Create new customer
        customer_doc = frappe.get_doc({
            "doctype": "Loyalty Customer",
            "customer_name": customer_name,
            "mobile_number": mobile_number,
            "vehicle_number": vehicle_number.upper(),
            "status": "Active"
        })
        customer_doc.insert()
        customer_id = customer_doc.name
    
    # Create fuel purchase entry
    purchase = frappe.get_doc({
        "doctype": "Fuel Purchase Entry",
        "customer": customer_id,
        "petrol_pump": petrol_pump,
        "fuel_type": fuel_type,
        "liters": float(liters),
        "amount": float(amount),
        "purchase_date": frappe.utils.now()
    })
    purchase.insert()
    purchase.submit()
    
    # Reload customer to get updated points
    customer_doc.reload()
    
    return {
        "success": True,
        "customer_id": customer_id,
        "customer_name": customer_doc.customer_name,
        "vehicle_number": customer_doc.vehicle_number,
        "fuel_type": fuel_type,
        "liters": liters,
        "amount": amount,
        "points_earned": liters,
        "total_points": customer_doc.current_cycle_liters
    }
    
@frappe.whitelist()
def register_customer_with_qr(qr_code, customer_name, mobile_number, vehicle_number):
    """Register a new customer with a scanned QR code"""
    doc = frappe.new_doc('Loyalty Customer')
    doc.__qr_code = qr_code  # Set the special attribute for autoname
    doc.customer_name = customer_name
    doc.mobile_number = mobile_number
    doc.vehicle_number = vehicle_number
    doc.status = 'Active'
    doc.naming_series = 'QR-.####.'
    doc.insert()
    
    return doc

# ============================================================================
# User Pump Settings APIs
# ============================================================================

@frappe.whitelist()
def get_user_default_pump():
    """Get current user's default pump settings"""
    user = frappe.session.user
    
    # REMOVED: Don't skip Administrator - let it return settings
    settings = frappe.db.get_value("User Pump Settings", 
        {"user": user, "is_active": 1},
        ["default_pump", "default_warehouse"],
        as_dict=True
    )
    
    return settings or {}



@frappe.whitelist()
def set_my_pump_settings(pump):
    """Set or update current user's default pump"""
    user = frappe.session.user
    
    if user in ["Administrator", "Guest"]:
        frappe.throw("Cannot set settings for system users")
    
    existing = frappe.db.exists("User Pump Settings", {"user": user})
    
    if existing:
        doc = frappe.get_doc("User Pump Settings", existing)
        doc.default_pump = pump
        doc.is_active = 1
        doc.save()
    else:
        warehouse = frappe.db.get_value("Petrol Pump Location", pump, "warehouse")
        doc = frappe.get_doc({
            "doctype": "User Pump Settings",
            "user": user,
            "default_pump": pump,
            "default_warehouse": warehouse,
            "is_active": 1
        })
        doc.insert()
    
    frappe.db.commit()
    return doc


# ============================================================================
# Gift Redemption - Multiple Items Support
# ============================================================================

@frappe.whitelist()
def get_available_gifts(petrol_pump):
    """Get available gift items for a pump with stock"""
    pump = frappe.get_doc("Petrol Pump Location", petrol_pump)
    
    if not pump.warehouse:
        return []
    
    gifts = []
    for item in pump.gift_items:
        stock = frappe.db.get_value("Bin", {
            "item_code": item.gift_item,
            "warehouse": pump.warehouse
        }, "actual_qty") or 0
        
        gifts.append({
            "gift_item": item.gift_item,
            "item_name": item.item_name,
            "points_required": item.points_required,
            "available_stock": stock
        })
    
    return gifts


@frappe.whitelist()
def get_gift_item_details(petrol_pump, gift_item):
    """Get single gift item details with stock"""
    from frappe import _
    
    pump = frappe.get_doc("Petrol Pump Location", petrol_pump)
    
    # Find gift in pump settings
    gift_config = None
    for item in pump.gift_items:
        if item.gift_item == gift_item:
            gift_config = item
            break
    
    if not gift_config:
        frappe.throw(_("Gift item {0} is not configured for {1}").format(gift_item, petrol_pump))
    
    # Get stock
    stock = frappe.db.get_value("Bin", {
        "item_code": gift_item,
        "warehouse": pump.warehouse
    }, "actual_qty") or 0
    
    return {
        "gift_item": gift_item,
        "item_name": gift_config.item_name,
        "points_required": gift_config.points_required,
        "available_stock": stock
    }



# ============================================================================
# WhatsApp Integration
# ============================================================================

@frappe.whitelist()
def get_whatsapp_link(customer_id, pump_name=None):
    """Generate WhatsApp link with customer loyalty info"""
    from urllib.parse import quote  # Import here too for safety
    
    customer = frappe.get_doc("Loyalty Customer", customer_id)
    
    # Format phone number - remove spaces, add 91
    phone = customer.mobile_number.replace(" ", "").replace("-", "").replace("+", "")
    if not phone.startswith("91"):
        phone = "91" + phone
    
    # Use provided pump name or generic
    if not pump_name:
        pump_name = "our pump"
    
    # Build message
    message = f"""Hello {customer.customer_name}! 🎉

Your Loyalty Program Status:
━━━━━━━━━━━━━━━━━━
✅ Current Points: {customer.current_cycle_liters} Liters
🎁 Total Gifts Redeemed: {customer.total_gifts_received}
📊 Total Fuel Purchased: {customer.total_liters_purchased}L

Check your points anytime here:
https://clm.abmtech.in/loyality/check

Thank you for choosing {pump_name}!

Keep fueling with us! ⛽"""
    
    # URL encode using quote instead of urllib.parse.quote
    encoded_message = quote(message)
    
    whatsapp_url = f"https://wa.me/{phone}?text={encoded_message}"
    
    return {
        "url": whatsapp_url,
        "phone": phone,
        "customer_name": customer.customer_name
    }

    
@frappe.whitelist()
@frappe.validate_and_sanitize_search_inputs
def get_pump_gift_items(doctype, txt, searchfield, start, page_len, filters):
    """Get gift items configured for a specific pump (for Link field query)"""
    petrol_pump = filters.get('petrol_pump')
    
    if not petrol_pump:
        return []
    
    # Get gift items from Pump Gift Item child table
    gift_items = frappe.db.sql("""
        SELECT 
            pgi.gift_item,
            i.item_name,
            pgi.points_required
        FROM 
            `tabPump Gift Item` pgi
        INNER JOIN 
            `tabItem` i ON i.name = pgi.gift_item
        WHERE 
            pgi.parent = %(pump)s
            AND pgi.parenttype = 'Petrol Pump Location'
            AND (pgi.gift_item LIKE %(txt)s OR i.item_name LIKE %(txt)s)
        ORDER BY 
            i.item_name
        LIMIT %(start)s, %(page_len)s
    """, {
        'pump': petrol_pump,
        'txt': f'%{txt}%',
        'start': start,
        'page_len': page_len
    }, as_dict=False)
    
    return gift_items
    
import frappe

@frappe.whitelist(allow_guest=True)
def check_loyalty_points(vehicle=None, mobile=None):
    """Public API to check loyalty points - accepts either vehicle or mobile number"""
    
    # Bypass CSRF for this public API
    frappe.flags.ignore_csrf = True
    
    # Clean inputs if provided
    if vehicle:
        vehicle = vehicle.strip().upper()
    if mobile:
        mobile = mobile.strip()
    
    result = {
        'found': False,
        'error': '',
        'customer': None,
        'purchases': [],
        'redemptions': []
    }
    
    try:
        # Validate that at least one parameter is provided
        if not vehicle and not mobile:
            result['error'] = "Please provide either vehicle number or mobile number"
            return result
        
        # Build SQL query dynamically based on provided parameters
        conditions = []
        params = []
        
        if vehicle and mobile:
            # Both provided - search with OR condition
            conditions.append("(UPPER(vehicle_number) = %s OR mobile_number = %s)")
            params.extend([vehicle, mobile])
        elif vehicle:
            # Only vehicle provided
            conditions.append("UPPER(vehicle_number) = %s")
            params.append(vehicle)
        else:
            # Only mobile provided
            conditions.append("mobile_number = %s")
            params.append(mobile)
        
        where_clause = " AND ".join(conditions)
        
        customers = frappe.db.sql(f"""
            SELECT name, customer_name, vehicle_number, mobile_number,
                   current_cycle_liters, total_liters_purchased, total_gifts_received,
                   registration_date
            FROM `tabLoyalty Customer`
            WHERE {where_clause}
            LIMIT 1
        """, tuple(params), as_dict=1)
        
        if not customers:
            if vehicle and mobile:
                result['error'] = f"Customer not found with vehicle {vehicle} or mobile {mobile}"
            elif vehicle:
                result['error'] = f"Customer not found with vehicle number {vehicle}"
            else:
                result['error'] = f"Customer not found with mobile number {mobile}"
            return result
        
        customer = customers[0]
        result['found'] = True
        result['customer'] = {
            'name': customer['name'],
            'customer_name': customer['customer_name'],
            'vehicle_number': customer['vehicle_number'],
            'mobile_number': customer['mobile_number'],
            'current_cycle_liters': customer['current_cycle_liters'],
            'total_liters_purchased': customer['total_liters_purchased'],
            'total_gifts_received': customer['total_gifts_received'],
            'registration_date': str(customer['registration_date'])
        }
        
        # Fetch purchases
        purchases = frappe.db.sql("""
            SELECT purchase_date, liters, amount, fuel_type, petrol_pump
            FROM `tabFuel Purchase Entry`
            WHERE customer = %s AND docstatus = 1
            ORDER BY purchase_date DESC
            LIMIT 5
        """, customer['name'], as_dict=1)
        
        result['purchases'] = [
            {
                'purchase_date': str(p['purchase_date']),
                'liters': p['liters'],
                'amount': p['amount'],
                'fuel_type': p['fuel_type'],
                'petrol_pump': p['petrol_pump']
            }
            for p in purchases
        ] if purchases else []
        
        # Fetch redemptions
        redemptions = frappe.db.sql("""
            SELECT DISTINCT name, redemption_date, petrol_pump, total_points
            FROM `tabGift Redemption`
            WHERE customer = %s AND docstatus = 1
            ORDER BY redemption_date DESC
            LIMIT 5
        """, customer['name'], as_dict=1)
        
        redemptions_with_items = []
        for red in redemptions:
            items = frappe.db.sql("""
                SELECT gift_item, item_name, points_required
                FROM `tabGift Redemption Item`
                WHERE parent = %s
                ORDER BY idx
            """, red['name'], as_dict=1)
            
            redemptions_with_items.append({
                'name': red['name'],
                'redemption_date': str(red['redemption_date']),
                'petrol_pump': red['petrol_pump'],
                'total_points': red['total_points'],
                'items': [
                    {
                        'gift_item': i['gift_item'],
                        'item_name': i['item_name'],
                        'points_required': i['points_required']
                    }
                    for i in items
                ] if items else []
            })
        
        result['redemptions'] = redemptions_with_items
        
    except Exception as e:
        frappe.log_error(str(e), "Loyalty Check API Error")
        result['error'] = "An error occurred while fetching data"
    
    return result
