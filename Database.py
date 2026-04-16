import psycopg2
import streamlit as st
import bcrypt
from datetime import datetime, timedelta


# Database ulanish
def get_connection():
    url = st.secrets["database"]["url"]
    conn = psycopg2.connect(url)
    return conn


# Jadvallarni yaratish
def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # Foydalanuvchilar jadvali
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            business_name TEXT,
            subscription_end DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Kategoriyalar jadvali
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            name TEXT NOT NULL
        )
    ''')

    # Tovarlar jadvali
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            name TEXT NOT NULL,
            price REAL NOT NULL,
            category TEXT
        )
    ''')

    # Sotuvlar jadvali
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            product_id INTEGER REFERENCES products(id),
            quantity INTEGER NOT NULL,
            total_price REAL NOT NULL,
            sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()
    print("Jadvallar yaratildi!")


# ============ FOYDALANUVCHILAR ============

# Yangi foydalanuvchi qo'shish
def add_user(username, password, business_name):
    conn = get_connection()
    cursor = conn.cursor()

    # Parolni shifrlash
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Default obuna muddati (30 kun)
    subscription_end = datetime.now().date() + timedelta(days=30)

    try:
        cursor.execute(
            "INSERT INTO users (username, password, business_name, subscription_end) VALUES (%s, %s, %s, %s)",
            (username, hashed.decode('utf-8'), business_name, subscription_end)
        )
        conn.commit()
        conn.close()
        return True
    except:
        conn.close()
        return False


# Foydalanuvchini tekshirish (login)
def check_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, business_name, password FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    conn.close()

    if user and bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
        return (user[0], user[1], user[2])
    return None


# ============ KATEGORIYALAR ============

def add_category(user_id, name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO categories (user_id, name) VALUES (%s, %s)", (user_id, name))
    conn.commit()
    conn.close()


def get_categories(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM categories WHERE user_id = %s", (user_id,))
    categories = cursor.fetchall()
    conn.close()
    return categories


def delete_category(category_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM categories WHERE id = %s", (category_id,))
    conn.commit()
    conn.close()


# ============ TOVARLAR ============

def add_product(user_id, name, price, category):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO products (user_id, name, price, category) VALUES (%s, %s, %s, %s)",
        (user_id, name, price, category)
    )
    conn.commit()
    conn.close()


def get_products(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price, category FROM products WHERE user_id = %s", (user_id,))
    products = cursor.fetchall()
    conn.close()
    return products


def get_product_by_id(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price, category FROM products WHERE id = %s", (product_id,))
    product = cursor.fetchone()
    conn.close()
    return product


def update_product(product_id, name, price, category):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE products SET name = %s, price = %s, category = %s WHERE id = %s",
        (name, price, category, product_id)
    )
    conn.commit()
    conn.close()
    return True


def delete_product(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
    conn.commit()
    conn.close()


# ============ SOTUVLAR ============

def add_sale(user_id, product_id, quantity, total_price):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO sales (user_id, product_id, quantity, total_price) VALUES (%s, %s, %s, %s)",
        (user_id, product_id, quantity, total_price)
    )
    conn.commit()
    conn.close()


def get_sales(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT sales.id, products.name, sales.quantity, sales.total_price, sales.sale_date
        FROM sales
        JOIN products ON sales.product_id = products.id
        WHERE sales.user_id = %s
        ORDER BY sales.sale_date DESC
        LIMIT 50
    ''', (user_id,))
    sales = cursor.fetchall()
    conn.close()
    return sales


def get_today_sales(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COALESCE(SUM(total_price), 0)
        FROM sales
        WHERE user_id = %s AND DATE(sale_date) = CURRENT_DATE
    ''', (user_id,))
    result = cursor.fetchone()[0]
    conn.close()
    return result


def get_monthly_sales(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COALESCE(SUM(total_price), 0)
        FROM sales
        WHERE user_id = %s 
        AND EXTRACT(MONTH FROM sale_date) = EXTRACT(MONTH FROM CURRENT_DATE)
        AND EXTRACT(YEAR FROM sale_date) = EXTRACT(YEAR FROM CURRENT_DATE)
    ''', (user_id,))
    result = cursor.fetchone()[0]
    conn.close()
    return result


def get_weekly_sales_chart(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT DATE(sale_date) as kun, SUM(total_price) as summa
        FROM sales
        WHERE user_id = %s AND sale_date >= CURRENT_DATE - INTERVAL '7 days'
        GROUP BY DATE(sale_date)
        ORDER BY kun
    ''', (user_id,))
    data = cursor.fetchall()
    conn.close()
    return data


def get_top_products(user_id, limit=5):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT products.name, SUM(sales.quantity) as soni
        FROM sales
        JOIN products ON sales.product_id = products.id
        WHERE sales.user_id = %s
        GROUP BY products.name
        ORDER BY soni DESC
        LIMIT %s
    ''', (user_id, limit))
    data = cursor.fetchall()
    conn.close()
    return data


def get_sales_by_category(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT products.category, SUM(sales.total_price) as summa
        FROM sales
        JOIN products ON sales.product_id = products.id
        WHERE sales.user_id = %s
        GROUP BY products.category
    ''', (user_id,))
    data = cursor.fetchall()
    conn.close()
    return data


def get_total_sales_count(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM sales WHERE user_id = %s", (user_id,))
    result = cursor.fetchone()[0]
    conn.close()
    return result


# ============ OBUNA ============

def check_subscription(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT subscription_end FROM users WHERE id = %s", (user_id,))
    result = cursor.fetchone()
    conn.close()
    if result and result[0]:
        return result[0]
    return None


def update_subscription(user_id, end_date):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET subscription_end = %s WHERE id = %s",
        (end_date, user_id)
    )
    conn.commit()
    conn.close()
    return True


# ============ PROGNOZ ============

def get_forecast(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT DATE(sale_date) as kun, SUM(total_price) as summa
        FROM sales
        WHERE user_id = %s AND sale_date >= CURRENT_DATE - INTERVAL '30 days'
        GROUP BY DATE(sale_date)
        ORDER BY kun
    ''', (user_id,))

    data = cursor.fetchall()
    conn.close()

    if not data:
        return 0

    today = datetime.now().date()
    total_weighted = 0
    total_weight = 0

    for row in data:
        kun = row[0]
        summa = row[1]

        days_ago = (today - kun).days

        if days_ago <= 7:
            weight = 3
        elif days_ago <= 14:
            weight = 2
        else:
            weight = 1

        total_weighted += summa * weight
        total_weight += weight

    if total_weight == 0:
        return 0

    daily_average = total_weighted / total_weight
    monthly_forecast = daily_average * 30

    return monthly_forecast


# ============ EXPORT ============

def get_all_sales_for_export(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT products.name, products.category, sales.quantity, 
               sales.total_price, sales.sale_date
        FROM sales
        JOIN products ON sales.product_id = products.id
        WHERE sales.user_id = %s
        ORDER BY sales.sale_date DESC
    ''', (user_id,))
    sales = cursor.fetchall()
    conn.close()
    return sales


# Jadvallarni yaratish
if __name__ == "__main__":
    create_tables()