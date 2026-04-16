import sqlite3

conn = sqlite3.connect('foresell.db')
cursor = conn.cursor()

try:
    cursor.execute('ALTER TABLE users ADD COLUMN subscription_end DATE')
    conn.commit()
    print("Ustun qo'shildi!")
except Exception as e:
    print(f"Xato yoki allaqachon bor: {e}")

conn.close()