# Mocazzo Fashion (Django)

This project is a modified version of the original paintings e-commerce site, updated into a **clothing/fashion e-commerce** site with:
- Size & color selection per product
- Mobile-first responsive templates (Bootstrap)
- Checkout flow + **Razorpay payment gateway** integration

## 1) Setup

```bash
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
```

## 2) Configure Razorpay

Create a Razorpay account and get your keys.

Set environment variables:

**Windows (PowerShell):**
```powershell
$env:RAZORPAY_KEY_ID = "your_key_id"
$env:RAZORPAY_KEY_SECRET = "your_key_secret"
```

**Linux/Mac:**
```bash
export RAZORPAY_KEY_ID="your_key_id"
export RAZORPAY_KEY_SECRET="your_key_secret"
```

> If keys are not set, the checkout page will still load but payment will be disabled.

## 3) Migrate DB

Because new models/fields were added (sizes/colors + Order tables), run:

```bash
python manage.py migrate
```

## 4) Run

```bash
python manage.py runserver
```

Open: `http://127.0.0.1:8000/`

## Notes
- Product sizes/colors are stored as comma-separated strings in the Product model (e.g. `S,M,L,XL` and `Black,Blue`).
- Cart lines are stored separately for each size/color selection.
- After successful payment verification, the cart is cleared and a success page is shown.
