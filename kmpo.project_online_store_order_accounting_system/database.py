import sqlite3

class Database:
    def __init__(self, db_name="orders.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        with self.conn:
            # Создание таблицы заказов
            self.conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY,
                order_number TEXT,
                product_name TEXT,
                quantity INTEGER,
                price REAL,
                status TEXT
            )
            """)

            # Создание таблицы продуктов с проверкой наличия колонки 'quantity'
            self.conn.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY,
                name TEXT,
                price REAL,
                quantity INTEGER DEFAULT 0
            )
            """)

            # Проверка, есть ли колонка 'quantity' в таблице 'products'
            self.check_and_add_quantity_column()

    def check_and_add_quantity_column(self):
        cursor = self.conn.cursor()
        cursor.execute("PRAGMA table_info(products);")
        columns = cursor.fetchall()

        # Проверяем, есть ли колонка 'quantity'
        column_names = [column[1] for column in columns]
        if 'quantity' not in column_names:
            print("Adding 'quantity' column to 'products' table.")
            self.conn.execute("ALTER TABLE products ADD COLUMN quantity INTEGER DEFAULT 0;")
            self.conn.commit()

    def query(self, query, params=()):
        with self.conn:
            cursor = self.conn.execute(query, params)
            self.conn.commit()
            return cursor

    def fetch_all(self, query, params=()):
        cursor = self.query(query, params)
        return cursor.fetchall()

    def fetch_one(self, query, params=()):
        cursor = self.query(query, params)
        return cursor.fetchone()
