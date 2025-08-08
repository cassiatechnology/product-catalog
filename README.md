# 🛍️ Product Catalog API

A **FastAPI** application for managing products, categories, and departments, built with **PostgreSQL** and **Async SQLAlchemy**.  
Includes advanced filtering, pagination, sorting, and analytics endpoints for business insights.

---

## ✨ Features

- Full CRUD for **Departments**, **Categories**, and **Products**
- Advanced filtering (`name`, `min_price`, `max_price`, `category_id`, `department_id`)
- Pagination and sorting
- List products by **category** or **department**
- **Analytics endpoints**:
  - Average price by department
  - Total stock by category
  - Product count by department
  - Total inventory value by department
- Database integrity validations (FKs, unique constraints)
- Automated tests with **Pytest** (isolated test DB)

---

## 🏗 Tech Stack

- **Language**: Python 3.11
- **Framework**: FastAPI
- **Database**: PostgreSQL 15
- **ORM**: SQLAlchemy 2.0 (async)
- **Migrations**: Alembic
- **Tests**: Pytest + HTTPX
- **Typing & Validation**: Pydantic v2

---

## 📦 Prerequisites

- [Python 3.11+](https://www.python.org/downloads/)
- [PostgreSQL 15+](https://www.postgresql.org/download/)
- [Poetry](https://python-poetry.org/) **or** `pip` (optional but recommended)
- [Alembic](https://alembic.sqlalchemy.org/) for database migrations

---

## ⚙️ Environment Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/YOUR-USERNAME/product-catalog.git
   cd product-catalog
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Create the `.env` file**

   ```env
   DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/product_catalog
   TEST_DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/product_catalog_test
   ```

5. **Run migrations**
   ```bash
   alembic upgrade head
   ```

---

## 🚀 Running the API

```bash
uvicorn app.main:app --reload
```

Interactive documentation:

- Swagger UI → [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc → [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🧪 Running Tests

Run all tests:

```bash
pytest -v
```

Run without warnings:

```bash
pytest -v --disable-warnings
```

---

## 📌 Endpoints Reference

| Method     | Endpoint                                      | Description                  | Request Body Example                                                       | Response Example                                                                    |
| ---------- | --------------------------------------------- | ---------------------------- | -------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| **POST**   | `/departments`                                | Create a new department      | `{ "name": "Men" }`                                                        | `{ "id": 1, "name": "Men" }`                                                        |
| **GET**    | `/departments`                                | List all departments         | –                                                                          | `[{"id": 1, "name": "Men"}]`                                                        |
| **GET**    | `/departments/{id}`                           | Get a department by ID       | –                                                                          | `{ "id": 1, "name": "Men" }`                                                        |
| **PUT**    | `/departments/{id}`                           | Update a department          | `{ "name": "Women" }`                                                      | `{ "id": 1, "name": "Women" }`                                                      |
| **DELETE** | `/departments/{id}`                           | Delete a department          | –                                                                          | _204 No Content_                                                                    |
| **POST**   | `/categories`                                 | Create a category            | `{ "name": "Shirts", "department_id": 1 }`                                 | `{ "id": 1, "name": "Shirts", "department_id": 1 }`                                 |
| **GET**    | `/categories`                                 | List categories              | –                                                                          | `[{"id": 1, "name": "Shirts", "department_id": 1}]`                                 |
| **GET**    | `/categories/{id}`                            | Get category by ID           | –                                                                          | `{ "id": 1, "name": "Shirts", "department_id": 1 }`                                 |
| **PUT**    | `/categories/{id}`                            | Update category              | `{ "name": "Pants" }`                                                      | `{ "id": 1, "name": "Pants", "department_id": 1 }`                                  |
| **DELETE** | `/categories/{id}`                            | Delete category              | –                                                                          | _204 No Content_                                                                    |
| **POST**   | `/products`                                   | Create a product             | `{ "name": "Cotton Shirt", "price": 59.9, "stock": 20, "category_id": 1 }` | `{ "id": 1, "name": "Cotton Shirt", "price": 59.9, "stock": 20, "category_id": 1 }` |
| **GET**    | `/products`                                   | List products with filters   | –                                                                          | `[{"id": 1, "name": "Cotton Shirt", "price": 59.9, "stock": 20}]`                   |
| **GET**    | `/products/{id}`                              | Get product by ID            | –                                                                          | `{ "id": 1, "name": "Cotton Shirt", "price": 59.9, "stock": 20 }`                   |
| **PUT**    | `/products/{id}`                              | Update a product             | `{ "price": 49.9 }`                                                        | `{ "id": 1, "name": "Cotton Shirt", "price": 49.9, "stock": 20 }`                   |
| **DELETE** | `/products/{id}`                              | Delete a product             | –                                                                          | _204 No Content_                                                                    |
| **GET**    | `/products/by-category/{category_id}`         | List products by category    | –                                                                          | `[{"id": 1, "name": "Cotton Shirt"}]`                                               |
| **GET**    | `/products/by-department/{department_id}`     | List products by department  | –                                                                          | `[{"id": 1, "name": "Cotton Shirt"}]`                                               |
| **GET**    | `/products/summary/avg-price-by-department`   | Avg price per department     | –                                                                          | `[{"department_id":1,"department_name":"Men","avg_price":104.95}]`                  |
| **GET**    | `/products/summary/total-stock-by-category`   | Total stock per category     | –                                                                          | `[{"category_id":1,"category_name":"Shirts","total_stock":85}]`                     |
| **GET**    | `/products/summary/count-by-department`       | Product count per department | –                                                                          | `[{"department_id":1,"product_count":10}]`                                          |
| **GET**    | `/products/summary/total-value-by-department` | Total value per department   | –                                                                          | `[{"department_id":1,"total_value":11234.10}]`                                      |

---

## 🗄 Project Structure

```
product-catalog/
│
├── app/
│   ├── api/               # Route definitions
│   ├── db/                # Database config & Base class
│   ├── models/            # SQLAlchemy models
│   ├── schemas/           # Pydantic schemas
│   ├── services/          # Business logic
│   └── main.py            # FastAPI entry point
│
├── tests/                 # Automated tests
├── alembic/               # Database migrations
├── .env                   # Local environment variables
├── requirements.txt
└── README.md
```

---

## 📊 Usage Examples

**Create a department**

```bash
curl -X POST http://localhost:8000/departments/      -H "Content-Type: application/json"      -d '{"name": "Men"}'
```

**Create a category**

```bash
curl -X POST http://localhost:8000/categories/      -H "Content-Type: application/json"      -d '{"name": "Shirts", "department_id": 1}'
```

**Create a product**

```bash
curl -X POST http://localhost:8000/products/      -H "Content-Type: application/json"      -d '{"name": "Cotton Shirt", "price": 59.9, "stock": 20, "category_id": 1}'
```
