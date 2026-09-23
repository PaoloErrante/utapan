import sqlite3

DB_NAME = "utapan.db"

def init_db():
    """Initializes the SQLite database tables with default values."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Ingredients Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            category TEXT NOT NULL,
            purchase_price REAL NOT NULL,
            purchase_qty REAL NOT NULL,
            unit TEXT NOT NULL,
            unit_cost REAL NOT NULL
        )
    ''')
    
    # Fixed Costs Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fixed_costs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item TEXT UNIQUE NOT NULL,
            monthly_amount REAL NOT NULL
        )
    ''')
    
    # Populate default ingredients if empty
    cursor.execute("SELECT COUNT(*) FROM ingredients")
    if cursor.fetchone()[0] == 0:
        default_ingredients = [
        ]
        cursor.executemany('''
            INSERT INTO ingredients (name, category, purchase_price, purchase_qty, unit, unit_cost)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', default_ingredients)

    # Populate default fixed overheads if empty
    cursor.execute("SELECT COUNT(*) FROM fixed_costs")
    if cursor.fetchone()[0] == 0:
        default_costs = [
        ]
        cursor.executemany('''
            INSERT INTO fixed_costs (item, monthly_amount)
            VALUES (?, ?)
        ''', default_costs)

    conn.commit()
    conn.close()

def get_ingredients():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, category, purchase_price, purchase_qty, unit, unit_cost FROM ingredients")
    rows = cursor.fetchall()
    conn.close()
    return rows

def add_ingredient(name, category, price, qty, unit):
    unit_c = price / qty if qty > 0 else 0
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO ingredients (name, category, purchase_price, purchase_qty, unit, unit_cost)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, category, price, qty, unit, unit_c))
    conn.commit()
    conn.close()

def delete_ingredient(ing_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ingredients WHERE id = ?", (ing_id,))
    conn.commit()
    conn.close()

def get_fixed_costs():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, item, monthly_amount FROM fixed_costs")
    rows = cursor.fetchall()
    conn.close()
    return rows

def add_fixed_cost(item, amount):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO fixed_costs (item, monthly_amount)
        VALUES (?, ?)
    ''', (item, amount))
    conn.commit()
    conn.close()

def delete_fixed_cost(cost_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM fixed_costs WHERE id = ?", (cost_id,))
    conn.commit()
    conn.close()
