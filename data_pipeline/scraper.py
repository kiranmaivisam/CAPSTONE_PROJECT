import requests
import pandas as pd
from bs4 import BeautifulSoup
from sql_queries import query1, query2, query3, query4, query5

all_books = []

for page in range(1, 4):

    url = f"https://books.toscrape.com/catalogue/page-{page}.html"

    response = requests.get(url)

    soup = BeautifulSoup(response.text, "html.parser")

    books = soup.select("article.product_pod")

    print("Page", page, ":", len(books), "books")

    for book in books:
        book_url = book.h3.a["href"]

        book_url = "https://books.toscrape.com/catalogue/" + book_url

        book_response = requests.get(book_url)

        book_soup = BeautifulSoup(book_response.text, "html.parser")

        category = book_soup.select("ul.breadcrumb li")[-2].text.strip()
        
        title = book.h3.a["title"]

        price = book.select_one(".price_color").text.strip()
        price = price.replace("Â£", "")
        price = float(price)

        availability = book.select_one(".availability").text.strip()
        if "In stock" in availability:
            in_stock = True
        else:
            in_stock = False

        rating_text = book.select_one("p.star-rating")["class"][1].lower()

        nums = ["zero", "one", "two", "three", "four", "five"]

        rating = nums.index(rating_text)

        all_books.append({
            "title": title,
            "price": price,
            "in_stock": in_stock,
            "rating": rating,
            "category" : category
        })

print("Total books:", len(all_books))
print(all_books[0])
book_url = "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"

response = requests.get(book_url)

soup = BeautifulSoup(response.text, "html.parser")

print(soup.select("ul.breadcrumb li")[-2].text.strip())
df = pd.DataFrame(all_books)
df = df.rename(columns = {"price":"price_gbp"})
print(df.isnull().sum())
df["price_inr"] = df["price_gbp"] * 105.50
df["price_inr"] = df["price_inr"].round(2)

print(df.head())

#Creating the SQLite database..
import sqlite3
import os
import sqlite3

if os.path.exists("zepto.db"):
    os.remove("zepto.db")

conn = sqlite3.connect("zepto.db")
print("Database connected successfully!")

conn.execute("""CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY,
    category_name TEXT UNIQUE)""")

conn.execute("""CREATE TABLE IF NOT EXISTS books (
    book_id INTEGER PRIMARY KEY,title TEXT,price_gbp REAL,price_inr REAL,rating INTEGER,in_stock INTEGER,category_id INTEGER,
    FOREIGN KEY (category_id) REFERENCES categories(category_id))""")
conn.commit()
print("Tables created successfully!")

categories = df["category"].unique()

for category in categories:
    conn.execute(
        "INSERT OR IGNORE INTO categories (category_name) VALUES (?)",
        (category,)
    )

conn.commit()

print("Categories inserted:", len(categories))
for _, row in df.iterrows():

    category_id = conn.execute(
        "SELECT category_id FROM categories WHERE category_name = ?",
        (row["category"],)
    ).fetchone()[0]

    conn.execute("""
        INSERT INTO books
        (title, price_gbp, price_inr, rating, in_stock, category_id)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        row["title"],
        row["price_gbp"],
        row["price_inr"],
        row["rating"],
        int(row["in_stock"]),
        category_id
    ))

conn.commit()

print("Books inserted:", len(df))
result = conn.execute("SELECT COUNT(*) FROM books").fetchone()

print("Books in database:", result[0])

result1 = pd.read_sql(query1, conn)
print(result1)

result2 = pd.read_sql(query2, conn)
print(result2)

result3 = pd.read_sql(query3, conn)
print(result3)

result4 = pd.read_sql(query4, conn)
print(result4)

result5 = pd.read_sql(query5, conn)
print(result5)

books_df = pd.read_sql("SELECT * FROM books", conn)

categories_df = pd.read_sql("SELECT * FROM categories", conn)

print(books_df.head())
print(categories_df.head())

merged_df = pd.merge(
    books_df,
    categories_df,
    on="category_id"
)

print(merged_df[["title", "price_gbp", "category_name"]].head(10))
results = {
    "query1_select_where": result1,
    "query2_order_limit": result2,
    "query3_distinct": result3,
    "query4_between": result4,
    "query5_join": result5
}

with open("sql_outputs.txt", "w", encoding="utf-8") as file:

    for name, result in results.items():

        file.write("\n")
        file.write("=" * 60 + "\n")
        file.write(name + "\n")
        file.write("=" * 60 + "\n")
        file.write(result.to_string(index=False))
        file.write("\n")

print("SQL outputs saved to sql_outputs.txt")
conn.close()
print("Database connection closed.")
