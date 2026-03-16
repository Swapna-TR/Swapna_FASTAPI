from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="FastAPI Shopping Cart System")

# --- 1. Data Models ---


class CheckoutRequest(BaseModel):
    customer_name: str
    delivery_address: str

# --- 2. In-Memory Database ---


# Product catalog
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499,
     "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 899, "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "in_stock": True},
]

# State management (Resets when server restarts)
cart = []
orders = []
order_id_counter = 1

# --- 3. Helper Functions ---


def calculate_total(product, quantity):
    return product["price"] * quantity

# --- 4. Cart Endpoints ---


@app.get("/cart")
def view_cart():
    if not cart:
        return {"message": "Cart is empty", "items": [],
                "item_count": 0, "grand_total": 0}

    grand_total = sum(item["subtotal"] for item in cart)
    return {
        "items": cart,
        "item_count": len(cart),
        "grand_total": grand_total
    }


@app.post("/cart/add")
def add_to_cart(product_id: int, quantity: int = 1):
    # Find product
    product = next((p for p in products if p["id"] == product_id), None)

    # Q3: Check if product exists (404)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Q3: Check if in stock (400)
    if not product["in_stock"]:
        raise HTTPException(
            status_code=400, detail=f"{product['name']} is out of stock")

    # Q4: Check if item already exists in cart (Duplicate logic)
    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            item["subtotal"] = calculate_total(product, item["quantity"])
            return {"message": "Cart updated", "cart_item": item}

    # If new item, add to cart
    new_item = {
        "product_id": product["id"],
        "product_name": product["name"],
        "quantity": quantity,
        "unit_price": product["price"],
        "subtotal": calculate_total(product, quantity)
    }
    cart.append(new_item)
    return {"message": "Added to cart", "cart_item": new_item}


@app.delete("/cart/{product_id}")
def remove_from_cart(product_id: int):
    global cart
    initial_len = len(cart)
    cart = [item for item in cart if item["product_id"] != product_id]

    if len(cart) == initial_len:
        raise HTTPException(status_code=404, detail="Item not in cart")

    return {"message": f"Product {product_id} removed from cart"}


@app.post("/cart/checkout")
def checkout(request: CheckoutRequest):
    global order_id_counter, cart

    # Bonus: Empty cart check
    if not cart:
        raise HTTPException(
            status_code=400, detail="Cart is empty — add items first")

    new_orders_summary = []

    # Process each cart item as an order
    for item in cart:
        order_entry = {
            "order_id": order_id_counter,
            "customer_name": request.customer_name,
            "delivery_address": request.delivery_address,
            "product": item["product_name"],
            "quantity": item["quantity"],
            "total_price": item["subtotal"]
        }
        orders.append(order_entry)
        new_orders_summary.append(order_entry)
        order_id_counter += 1

    # Calculate grand total for the checkout response
    checkout_total = sum(item["total_price"] for item in new_orders_summary)

    # Clear the cart after checkout
    cart = []

    return {
        "message": "Checkout successful",
        "orders_placed": len(new_orders_summary),
        "grand_total": checkout_total,
        "summary": new_orders_summary
    }

# --- 5. Order Endpoints ---


@app.get("/orders")
def get_orders():
    return {
        "orders": orders,
        "total_orders": len(orders)
    }
