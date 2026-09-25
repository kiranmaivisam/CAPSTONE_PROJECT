query1 = """
SELECT title, rating
FROM books
WHERE rating = 5
"""
query2 = """
SELECT title, price_gbp
FROM books
ORDER BY price_gbp DESC
LIMIT 5
"""
query3 = """
SELECT DISTINCT category_id
FROM books
"""
query4 = """
SELECT title, price_gbp
FROM books
WHERE price_gbp BETWEEN 40 AND 50
"""
query5 = """
SELECT books.title, books.price_gbp, categories.category_name
FROM books
JOIN categories
ON books.category_id = categories.category_id
"""