# Billing System - FastAPI

A billing system application built with FastAPI, SQLAlchemy, and Jinja2 templates.

## Features

- **Product Management**: CRUD operations for products (name, product ID, stock, price, tax %)
- **Billing Page**: Generate bills with dynamic product rows, denomination tracking, and balance calculation
- **Invoice Email**: Sends invoice to customer email asynchronously (when SMTP is configured)
- **Purchase History**: View past purchases by customer email and drill into invoice details
- **Denomination Management**: Tracks shop denominations and calculates optimal change

## Setup & Run

### 1. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment (optional)

Edit `.env` file to configure SMTP settings for email functionality. Email sending is optional - the app works without it.

### 4. Seed the database

```bash
python seed.py
```

This creates sample products and initializes denominations.

### 5. Run the application

```bash
uvicorn app.main:app --reload
```

Visit http://127.0.0.1:8000 in your browser.

## Pages

| URL | Description |
|-----|-------------|
| `/billing` | Billing form (Page 1) - enter email, add products, denominations, cash paid |
| `/billing/generate` | Bill result (Page 2) - shows calculated bill with balance denominations |
| `/products` | Product management - view, add, delete products |
| `/history` | Purchase history - search by email, view invoice details |

## API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/products/api` | List all products (JSON) |
| POST | `/products/api` | Create a product |
| PUT | `/products/api/{product_id}` | Update a product |
| DELETE | `/products/api/{product_id}` | Delete a product |

## Assumptions

1. Denominations are Indian currency: 500, 200, 100, 50, 20, 10, 5, 2, 1
2. Net price is rounded up (ceiling) to nearest integer for balance calculation
3. Balance denomination uses a greedy algorithm limited by shop's available denominations
4. SQLite is used as the database for simplicity (can be swapped via DATABASE_URL)
5. Email sending is optional - works without SMTP configuration (logs a warning instead)

## Project Structure

```
mallow_tech_task1/
├── app/
│   ├── core/           # Config, database setup
│   ├── models/         # SQLAlchemy models & Pydantic schemas
│   ├── routers/        # FastAPI route handlers
│   ├── services/       # Business logic layer
│   ├── templates/      # Jinja2 HTML templates
│   ├── utils/          # Email utility
│   └── main.py         # FastAPI app entry point
├── seed.py             # Database seeder
├── requirements.txt
├── .env
└── README.md
```
