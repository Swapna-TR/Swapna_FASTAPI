from fastapi import FastAPI

app = FastAPI()

# Product data
products = [
    {
        "id": 1,
        "name": "Notebook",
        "price": 50,
        "category": "Stationery",
        "in_stock": True
    },
    {
        "id": 2,
        "name": "Pen",
        "price": 10,
        "category": "Stationery",
        "in_stock": True
    },
    {
        "id": 3,
        "name": "Mouse",
        "price": 599,
        "category": "Electronics",
        "in_stock": True
    },
    {
        "id": 4,
        "name": "Headphones",
        "price": 999,
        "category": "Electronics",
        "in_stock": False
    },
    {
        "id": 5,
        "name": "Laptop Stand",
        "price": 1299,
        "category": "Electronics",
        "in_stock": True
    },
    {
        "id": 6,
        "name": "Mechanical Keyboard",
        "price": 2499,
        "category": "Electronics",
        "in_stock": True
    },
    {
        "id": 7,
        "name": "Webcam",
        "price": 1899,
        "category": "Electronics",
        "in_stock": False
    }
]


# Q1 - Show all products
@app.get("/products")
def get_products():

    total = len(products)

    return {
        "products": products,
        "total": total
    }


# Q2 - Filter products by category
@app.get("/products/category/{category_name}")
def get_products_by_category(category_name: str):

    filtered_products = []

    for product in products:
        if product["category"] == category_name:
            filtered_products.append(product)

    if len(filtered_products) == 0:
        return {"error": "No products found in this category"}

    return {
        "category": category_name,
        "products": filtered_products,
        "total": len(filtered_products)
    }


# Q3 - Show only in-stock products
@app.get("/products/instock")
def get_instock_products():

    available_products = []

    for product in products:
        if product["in_stock"] == True:
            available_products.append(product)

    return {
        "in_stock_products": available_products,
        "count": len(available_products)
    }


# Q4 - Store summary
@app.get("/store/summary")
def store_summary():

    total_products = len(products)

    in_stock = 0
    out_stock = 0
    categories = []

    for product in products:

        if product["in_stock"] == True:
            in_stock += 1
        else:
            out_stock += 1

        if product["category"] not in categories:
            categories.append(product["category"])

    return {
        "store_name": "My Online Store",
        "total_products": total_products,
        "in_stock": in_stock,
        "out_of_stock": out_stock,
        "categories": categories
    }


# Q5 - Search products by name
@app.get("/products/search/{keyword}")
def search_products(keyword: str):

    results = []

    for product in products:
        product_name = product["name"].lower()
        search_word = keyword.lower()

        if search_word in product_name:
            results.append(product)

    if len(results) == 0:
        return {"message": "No products matched your search"}

    return {
        "keyword": keyword,
        "results": results,
        "total_matches": len(results)
    }
