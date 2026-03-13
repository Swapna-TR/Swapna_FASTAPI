from fastapi import FastAPI, Response, status, Query
from pydantic import BaseModel

app = FastAPI()

# -----------------------------
# Product Data (Initial List)
# -----------------------------
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499,
        "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99,
        "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799,
        "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49,
        "category": "Stationery", "in_stock": True},
]


# -----------------------------
# Request Model
# -----------------------------
class NewProduct(BaseModel):
    name: str
    price: int
    category: str
    in_stock: bool = True


# -----------------------------
# Helper Function
# -----------------------------
def find_product(product_id: int):
    for product in products:
        if product["id"] == product_id:
            return product
    return None


# -----------------------------
# GET all products
# -----------------------------
@app.get("/products")
def get_products():
    return {
        "products": products,
        "total": len(products)
    }


# -----------------------------
# POST add new product
# -----------------------------
@app.post("/products", status_code=201)
def add_product(product: NewProduct, response: Response):

    # check duplicate name
    for p in products:
        if p["name"].lower() == product.name.lower():
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"error": "Product already exists"}

    next_id = max(p["id"] for p in products) + 1

    new_product = {
        "id": next_id,
        "name": product.name,
        "price": product.price,
        "category": product.category,
        "in_stock": product.in_stock
    }

    products.append(new_product)

    return {
        "message": "Product added",
        "product": new_product
    }


# -----------------------------
# PUT update product
# -----------------------------
@app.put("/products/{product_id}")
def update_product(
        product_id: int,
        price: int = None,
        in_stock: bool = None,
        response: Response = None
):

    product = find_product(product_id)

    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Product not found"}

    if price is not None:
        product["price"] = price

    if in_stock is not None:
        product["in_stock"] = in_stock

    return {
        "message": "Product updated",
        "product": product
    }


# -----------------------------
# DELETE product
# -----------------------------
@app.delete("/products/{product_id}")
def delete_product(product_id: int, response: Response):

    product = find_product(product_id)

    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Product not found"}

    products.remove(product)

    return {
        "message": f"Product '{product['name']}' deleted"
    }


# =====================================================
# Q5 — INVENTORY AUDIT ENDPOINT
# (Place ABOVE /products/{product_id} routes)
# =====================================================
@app.get("/products/audit")
def product_audit():

    in_stock_list = [p for p in products if p["in_stock"]]
    out_stock_list = [p for p in products if not p["in_stock"]]

    total_stock_value = sum(p["price"] * 10 for p in in_stock_list)

    most_expensive = max(products, key=lambda p: p["price"])

    return {
        "total_products": len(products),
        "in_stock_count": len(in_stock_list),
        "out_of_stock_names": [p["name"] for p in out_stock_list],
        "total_stock_value": total_stock_value,
        "most_expensive": {
            "name": most_expensive["name"],
            "price": most_expensive["price"]
        }
    }


# =====================================================
# BONUS — CATEGORY DISCOUNT
# =====================================================
@app.put("/products/discount")
def bulk_discount(
        category: str = Query(..., description="Category name"),
        discount_percent: int = Query(..., ge=1, le=99)
):

    updated_products = []

    for product in products:
        if product["category"].lower() == category.lower():

            new_price = int(product["price"] * (1 - discount_percent / 100))
            product["price"] = new_price

            updated_products.append(product)

    if not updated_products:
        return {
            "message": f"No products found in category: {category}"
        }

    return {
        "message": f"{discount_percent}% discount applied to {category}",
        "updated_count": len(updated_products),
        "updated_products": updated_products
    }


# -----------------------------
# GET single product
# -----------------------------
@app.get("/products/{product_id}")
def get_single_product(product_id: int, response: Response):

    product = find_product(product_id)

    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"error": "Product not found"}

    return product
