import bcrypt
import sqlite3


# Ma'lumotlar bazasiga ulanish
def get_connection():
    conn = sqlite3.connect('foresell.db')
    return conn


# Jadvallarni yaratish
def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # Foydalanuvchilar jadvali
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                business_name TEXT,
                subscription_end DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

    # Tovarlar jadvali
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS products
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       user_id
                       INTEGER,
                       name
                       TEXT
                       NOT
                       NULL,
                       price
                       REAL,
                       category
                       TEXT,
                       FOREIGN
                       KEY
                   (
                       user_id
                   ) REFERENCES users
                   (
                       id
                   )
                       )
                   ''')

    # Sotuvlar jadvali
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS sales
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       user_id
                       INTEGER,
                       product_id
                       INTEGER,
                       quantity
                       INTEGER,
                       total_price
                       REAL,
                       sale_date
                       TIMESTAMP
                       DEFAULT
                       CURRENT_TIMESTAMP,
                       FOREIGN
                       KEY
                   (
                       user_id
                   ) REFERENCES users
                   (
                       id
                   ),
                       FOREIGN KEY
                   (
                       product_id
                   ) REFERENCES products
                   (
                       id
                   )
                       )
                   ''')
    # Kategoriyalar jadvali
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

    conn.commit()
    conn.close()
    print("Jadvallar yaratildi!")

# Yangi foydalanuvchi qo'shish (shifrlangan parol)
def add_user(username, password, business_name):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Parolni shifrlash
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        cursor.execute(
            "INSERT INTO users (username, password, business_name) VALUES (?, ?, ?)",
            (username, hashed.decode('utf-8'), business_name)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# Login tekshirish
# Login tekshirish (shifrlangan parol)
def check_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, username, business_name, password FROM users WHERE username = ?",
        (username,)
    )
    user = cursor.fetchone()
    conn.close()

    if user:
        # Parolni tekshirish
        stored_password = user[3]
        if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
            return (user[0], user[1], user[2])  # id, username, business_name
    return None
# ============ TOVARLAR ============

# Yangi tovar qo'shish
def add_product(user_id, name, price, category):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO products (user_id, name, price, category) VALUES (?, ?, ?, ?)",
        (user_id, name, price, category)
    )
    conn.commit()
    conn.close()
    return True

# Foydalanuvchining tovarlarini olish
def get_products(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, price, category FROM products WHERE user_id = ?",
        (user_id,)
    )
    products = cursor.fetchall()
    conn.close()
    return products

# Tovarni o'chirish
def delete_product(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()
    return True
# Tovarni tahrirlash
def update_product(product_id, name, price, category):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE products SET name = ?, price = ?, category = ? WHERE id = ?",
        (name, price, category, product_id)
    )
    conn.commit()
    conn.close()
    return True

# Bitta tovarni olish (tahrirlash uchun)
def get_product_by_id(product_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, price, category FROM products WHERE id = ?",
        (product_id,)
    )
    product = cursor.fetchone()
    conn.close()
    return product

# ============ KATEGORIYALAR ============

# Yangi kategoriya qo'shish
def add_category(user_id, name):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO categories (user_id, name) VALUES (?, ?)",
            (user_id, name)
        )
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

# Foydalanuvchining kategoriyalarini olish
def get_categories(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name FROM categories WHERE user_id = ?",
        (user_id,)
    )
    categories = cursor.fetchall()
    conn.close()
    return categories

# Kategoriyani o'chirish
def delete_category(category_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
    conn.commit()
    conn.close()
    return True
# ============ SOTUVLAR ============

# Yangi sotuv qo'shish
def add_sale(user_id, product_id, quantity, total_price):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO sales (user_id, product_id, quantity, total_price) VALUES (?, ?, ?, ?)",
        (user_id, product_id, quantity, total_price)
    )
    conn.commit()
    conn.close()
    return True

# Foydalanuvchining sotuvlarini olish
def get_sales(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT sales.id, products.name, sales.quantity, sales.total_price, sales.sale_date
        FROM sales
        JOIN products ON sales.product_id = products.id
        WHERE sales.user_id = ?
        ORDER BY sales.sale_date DESC
    ''', (user_id,))
    sales = cursor.fetchall()
    conn.close()
    return sales

# Bugungi sotuvlar summasini olish
def get_today_sales(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COALESCE(SUM(total_price), 0)
        FROM sales
        WHERE user_id = ? AND DATE(sale_date) = DATE('now')
    ''', (user_id,))
    total = cursor.fetchone()[0]
    conn.close()
    return total

# Oylik sotuvlar summasini olish
def get_monthly_sales(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COALESCE(SUM(total_price), 0)
        FROM sales
        WHERE user_id = ? 
        AND strftime('%Y-%m', sale_date) = strftime('%Y-%m', 'now')
    ''', (user_id,))
    total = cursor.fetchone()[0]
    conn.close()
    return total
# ============ HISOBOTLAR ============

# Oxirgi 7 kunlik sotuvlar (grafik uchun)
def get_weekly_sales_chart(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT DATE(sale_date) as kun, SUM(total_price) as jami
        FROM sales
        WHERE user_id = ? AND sale_date >= DATE('now', '-7 days')
        GROUP BY DATE(sale_date)
        ORDER BY kun
    ''', (user_id,))
    data = cursor.fetchall()
    conn.close()
    return data

# Top sotilgan tovarlar
def get_top_products(user_id, limit=5):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT products.name, SUM(sales.quantity) as soni, SUM(sales.total_price) as jami
        FROM sales
        JOIN products ON sales.product_id = products.id
        WHERE sales.user_id = ?
        GROUP BY products.id
        ORDER BY jami DESC
        LIMIT ?
    ''', (user_id, limit))
    data = cursor.fetchall()
    conn.close()
    return data

# Kategoriya bo'yicha sotuvlar
def get_sales_by_category(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT products.category, SUM(sales.total_price) as jami
        FROM sales
        JOIN products ON sales.product_id = products.id
        WHERE sales.user_id = ?
        GROUP BY products.category
        ORDER BY jami DESC
    ''', (user_id,))
    data = cursor.fetchall()
    conn.close()
    return data

# Umumiy sotuvlar soni
def get_total_sales_count(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COUNT(*) FROM sales WHERE user_id = ?
    ''', (user_id,))
    count = cursor.fetchone()[0]
    conn.close()
    return count
# Test foydalanuvchi yaratish
# ============ OBUNA VA PROGNOZ ============
# Obuna muddatini tekshirish
def check_subscription(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT subscription_end FROM users WHERE id = ?",
        (user_id,)
    )
    result = cursor.fetchone()
    conn.close()
    if result and result[0]:
        return result[0]
    return None


# Obuna muddatini yangilash
def update_subscription(user_id, end_date):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET subscription_end = ? WHERE id = ?",
        (end_date, user_id)
    )
    conn.commit()
    conn.close()
    return True

# Keyingi oy prognozi (vaznli o'rtacha)
def get_forecast(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    # Oxirgi 7 kun (vazn: 3)
    cursor.execute('''
        SELECT COALESCE(SUM(total_price), 0)
        FROM sales
        WHERE user_id = ? AND sale_date >= DATE('now', '-7 days')
    ''', (user_id,))
    week1 = cursor.fetchone()[0]

    # 8-14 kun oldin (vazn: 2)
    cursor.execute('''
        SELECT COALESCE(SUM(total_price), 0)
        FROM sales
        WHERE user_id = ? 
        AND sale_date >= DATE('now', '-14 days')
        AND sale_date < DATE('now', '-7 days')
    ''', (user_id,))
    week2 = cursor.fetchone()[0]

    # 15-30 kun oldin (vazn: 1)
    cursor.execute('''
        SELECT COALESCE(SUM(total_price), 0)
        FROM sales
        WHERE user_id = ? 
        AND sale_date >= DATE('now', '-30 days')
        AND sale_date < DATE('now', '-14 days')
    ''', (user_id,))
    week3_4 = cursor.fetchone()[0]

    conn.close()

    # Vaznli o'rtacha hisoblash
    # week1 × 3 + week2 × 2 + week3_4 × 1
    total_weighted = (week1 * 3) + (week2 * 2) + (week3_4 * 1)

    # Agar ma'lumot bo'lsa
    if total_weighted > 0:
        # Vaznli kunlik o'rtacha: total / (7×3 + 7×2 + 16×1) = total / 51
        daily_avg = total_weighted / 51
        return daily_avg * 30  # 30 kunga ko'paytirish

    return 0
# ============ EXPORT ============

# Barcha sotuvlarni olish (Excel uchun)
def get_all_sales_for_export(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT products.name, products.category, sales.quantity, 
               sales.total_price, sales.sale_date
        FROM sales
        JOIN products ON sales.product_id = products.id
        WHERE sales.user_id = ?
        ORDER BY sales.sale_date DESC
    ''', (user_id,))
    sales = cursor.fetchall()
    conn.close()
    return sales

if __name__ == "__main__":
    create_tables()
    # Admin foydalanuvchi qo'shish
    if add_user("admin", "1234", "Test Do'kon"):
        print("Admin yaratildi!")
    else:
        print("Admin allaqachon bor")