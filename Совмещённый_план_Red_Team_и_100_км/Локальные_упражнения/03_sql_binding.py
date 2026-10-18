"""compare SQL structure and bound values in an in-memory toy database."""
import sqlite3

db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE products(name TEXT, category TEXT)")
db.executemany("INSERT INTO products VALUES (?, ?)", [
    ("toy_book", "books"), ("toy_lamp", "home")
])

for value in ["books", "books' OR '1'='1"]:
    unsafe_query = "SELECT name FROM products WHERE category='" + value + "'"
    unsafe = db.execute(unsafe_query).fetchall()
    safe = db.execute("SELECT name FROM products WHERE category=?", (value,)).fetchall()
    print("Input:", repr(value))
    print("Concatenated SQL:", unsafe_query)
    print("Unsafe result:", unsafe)
    print("Bound result: ", safe)
    print()
db.close()
