import sqlite3

DB_NAME = "utapan.db"

def init_db():
    """Initializes the SQLite database tables with default values."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Categories Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    ''')

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
    # Saved Recipes Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            yield_kg REAL NOT NULL,
            labor_hours REAL NOT NULL,
            margin REAL NOT NULL,
            data_json TEXT NOT NULL
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

    # Aggiungi queste tabelle dentro init_db() in database.py
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            notes TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER,
            delivery_date TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            FOREIGN KEY (client_id) REFERENCES clients (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            recipe_id INTEGER,
            quantity REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders (id),
            FOREIGN KEY (recipe_id) REFERENCES recipes (id)
        )
    ''')
    conn.commit()
    conn.close()

# --- CATEGORY FUNCTIONS ---
def get_categories():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM categories ORDER BY name ASC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def add_category(name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()

def update_category(cat_id, new_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Update category name in ingredients table first to preserve consistency
    cursor.execute("SELECT name FROM categories WHERE id = ?", (cat_id,))
    old_name = cursor.fetchone()
    if old_name:
        cursor.execute("UPDATE ingredients SET category = ? WHERE category = ?", (new_name, old_name[0]))
    cursor.execute("UPDATE categories SET name = ? WHERE id = ?", (new_name, cat_id))
    conn.commit()
    conn.close()

def delete_category(cat_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM categories WHERE id = ?", (cat_id,))
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

def save_recipe(name, yield_kg, labor_hours, margin, items_list):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    data_json = json.dumps(items_list)
    cursor.execute('''
        INSERT OR REPLACE INTO recipes (name, yield_kg, labor_hours, margin, data_json)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, yield_kg, labor_hours, margin, data_json))
    conn.commit()
    conn.close()

def get_recipes():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, yield_kg, labor_hours, margin, data_json FROM recipes")
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_recipe(recipe_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
    conn.commit()
    conn.close()


# --- CLIENT FUNCTIONS ---
def get_clients():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, phone, email, notes FROM clients ORDER BY name ASC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def add_client(name, phone="", email="", notes=""):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO clients (name, phone, email, notes) VALUES (?, ?, ?, ?)", (name, phone, email, notes))
    conn.commit()
    conn.close()

def delete_client(client_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clients WHERE id = ?", (client_id,))
    conn.commit()
    conn.close()

# --- ORDER FUNCTIONS ---
def add_order(client_id, delivery_date, items):
    """
    items è una lista di dizionari: [{'recipe_id': int, 'quantity': float}]
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO orders (client_id, delivery_date) VALUES (?, ?)", (client_id, delivery_date))
    order_id = cursor.lastrowid
    
    for item in items:
        cursor.execute("INSERT INTO order_items (order_id, recipe_id, quantity) VALUES (?, ?, ?)", 
                       (order_id, item['recipe_id'], item['quantity']))
    
    conn.commit()
    conn.close()

def get_orders_by_date(start_date, end_date):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT o.id, c.name, o.delivery_date, o.status
        FROM orders o
        JOIN clients c ON o.client_id = c.id
        WHERE o.delivery_date BETWEEN ? AND ?
        ORDER BY o.delivery_date ASC
    ''', (start_date, end_date))
    orders = cursor.fetchall()
    
    detailed_orders = []
    for order in orders:
        order_id = order[0]
        cursor.execute('''
            SELECT r.name, oi.quantity 
            FROM order_items oi
            JOIN recipes r ON oi.recipe_id = r.id
            WHERE oi.order_id = ?
        ''', (order_id,))
        items = cursor.fetchall()
        detailed_orders.append({
            'id': order_id,
            'client': order[1],
            'date': order[2],
            'status': order[3],
            'items': items
        })
    conn.close()
    return detailed_orders

def calculate_ingredient_requirements(start_date, end_date):
    """
    Calcola la somma di tutti gli ingredienti necessari per gli ordini 
    compresi tra start_date ed end_date basandosi sulle dosi salvate nelle ricette.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Recupera tutti gli item ordinati nell'intervallo di date
    cursor.execute('''
        SELECT oi.recipe_id, oi.quantity, r.data_json, r.yield_kg
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.id
        JOIN recipes r ON oi.recipe_id = r.id
        WHERE o.delivery_date BETWEEN ? AND ?
    ''', (start_date, end_date))
    
    rows = cursor.fetchall()
    conn.close()
    
    ingredient_totals = {}
    
    for row in rows:
        ordered_qty = row[1]       # Quantità ordinate (es. numero di pani o kg)
        recipe_data = json.loads(row[2]) # Dosi della ricetta
        recipe_yield = row[3]      # Resa del lotto di ricetta (es. 10 kg)
        
        # Fattore di scala rispetto alla ricetta base
        scale_factor = ordered_qty / recipe_yield if recipe_yield > 0 else 1.0
        
        for item in recipe_data:
            ing_name = item['ingredient']
            dose = float(item['dose']) * scale_factor
            
            if ing_name in ingredient_totals:
                ingredient_totals[ing_name] += dose
            else:
                ingredient_totals[ing_name] = dose
                
    return ingredient_totals
