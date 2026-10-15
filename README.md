# Loyalty Rewards Program (CLP)

Customer Loyalty and Rewards Program built as a custom Frappe / ERPNext application for petrol pumps and retail stations.

---

## Features

- **Customer Loyalty Points Tracking**: Automatically records fuel purchases and accrues loyalty points (liters).
- **Public Customer Portal**: Allows customers to look up their loyalty points and transaction history using vehicle or mobile number (`/loyality/check.html`).
- **Gift Redemptions & Stock Management**: Redeem loyalty points for configured gift items with ERPNext warehouse stock entries.
- **QR Code Scanner**: Attendants can scan customer QR codes for instant lookup and quick fueling sales.
- **Automated QA & Security Audit Suite**: Built-in test automation suite (`test_clp_audit.py`) and formal audit report.

---

## Quick Local Test & Preview

To preview and test the customer loyalty portal locally without installing WSL, MariaDB, or Redis:

```bash
python run_preview.py
```

Then open **`http://localhost:8000`** in your browser.

---

## Running Automated QA Tests

Execute the automated test suite to run schema validations, security checks, and live endpoint tests:

```bash
python test_clp_audit.py
```

---

## Installation on Frappe / ERPNext

Install this app inside your existing Frappe bench environment:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app https://github.com/Anilbirada/-Loyalty-Rewards-Program.git --branch main
bench --site your-site.local install-app clp
bench --site your-site.local migrate
```

---

## Contributing

This app uses `pre-commit` for code formatting and linting:

```bash
cd apps/clp
pre-commit install
```

---

## License

MIT License
