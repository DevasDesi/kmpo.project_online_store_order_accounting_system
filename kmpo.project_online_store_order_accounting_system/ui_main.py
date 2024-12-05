from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QWidget, QMessageBox, QDialog, QLineEdit, QComboBox, QLabel, QDialogButtonBox, QTableWidget, QTableWidgetItem
from PyQt6.QtGui import QIntValidator
from database import Database

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Подключение базы данных
        self.db = Database('store.db')

        # Настройка интерфейса
        self.setWindowTitle("Order Management System")
        self.setGeometry(100, 100, 800, 600)

        container = QWidget()
        self.setCentralWidget(container)

        self.layout = QVBoxLayout()

        # Секция для отображения списка заказов
        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(5)  # 5 столбцов: Номер, Продукт, Количество, Цена, Статус
        self.orders_table.setHorizontalHeaderLabels(["Order Number", "Product", "Quantity", "Price(rubles)", "Status"])
        self.layout.addWidget(self.orders_table)

        # Обновляем список заказов
        self.update_orders_list()

        # Добавление кнопок
        self.add_order_button = QPushButton("Add Order")
        self.add_order_button.clicked.connect(self.add_order)
        self.layout.addWidget(self.add_order_button)

        self.edit_order_button = QPushButton("Edit Order")
        self.edit_order_button.clicked.connect(self.edit_order)
        self.layout.addWidget(self.edit_order_button)

        self.delete_order_button = QPushButton("Delete Order")
        self.delete_order_button.clicked.connect(self.delete_order)
        self.layout.addWidget(self.delete_order_button)

        self.manage_products_button = QPushButton("Manage Products")
        self.manage_products_button.clicked.connect(self.manage_products)
        self.layout.addWidget(self.manage_products_button)

        container.setLayout(self.layout)

    def update_orders_list(self):
        orders = self.db.fetch_all("SELECT order_number, product_name, quantity, price, status FROM orders")
        self.orders_table.setRowCount(len(orders))

        for row, order in enumerate(orders):
            for col, data in enumerate(order):
                # Округляем значение цены до 2 знаков после запятой
                if col == 3:  # Столбец с ценой
                    data = "{:.2f}".format(data)
                self.orders_table.setItem(row, col, QTableWidgetItem(str(data)))


    def add_order(self):
        dialog = AddOrderDialog(self.db)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            product_id = dialog.selected_product_id
            quantity = dialog.selected_quantity
            product_data = self.db.fetch_one("SELECT id, name, quantity FROM products WHERE id = ?", (product_id,))

            if product_data:
                available_quantity = product_data[2]
                if available_quantity < quantity:
                    QMessageBox.warning(self, "Insufficient Product", "Not enough product in stock to complete this order.")
                else:
                    # Процесс создания заказа
                    order_number = dialog.selected_order_number
                    product_name = product_data[1]
                    price = dialog.selected_price
                    total_price = price * quantity

                    self.db.query("INSERT INTO orders (order_number, product_name, quantity, price, status) VALUES (?, ?, ?, ?, ?)",
                                  (order_number, product_name, quantity, total_price, "Pending"))

                    # Обновляем количество продукта на складе
                    self.db.query("UPDATE products SET quantity = quantity - ? WHERE id = ?", (quantity, product_id))

                    # Обновляем список заказов
                    self.update_orders_list()

                    QMessageBox.information(self, "Order Added", "Order has been successfully added!")
            else:
                QMessageBox.warning(self, "Product Error", "The selected product does not exist.")

    def edit_order(self):
        dialog = EditOrderDialog(self.db)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            QMessageBox.information(self, "Order Edited", "Order has been successfully edited!")
            self.update_orders_list()

    def delete_order(self):
        dialog = DeleteOrderDialog(self.db)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            QMessageBox.information(self, "Order Deleted", "Order has been successfully deleted!")
            self.update_orders_list()

    def manage_products(self):
        dialog = ManageProductsDialog(self.db)
        dialog.exec()


class ManageProductsDialog(QDialog):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setWindowTitle("Manage Products")
        self.setGeometry(250, 250, 600, 400)

        self.layout = QVBoxLayout()

        # Таблица для отображения существующих продуктов
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(4)  # 4 столбца: ID, Название, Цена, Количество
        self.products_table.setHorizontalHeaderLabels(["ID", "Product Name", "Price(rubles)", "Quantity"])
        self.layout.addWidget(self.products_table)

        # Кнопки для управления продуктами
        self.add_product_button = QPushButton("Add Product")
        self.add_product_button.clicked.connect(self.add_product)
        self.layout.addWidget(self.add_product_button)

        self.edit_product_button = QPushButton("Edit Selected Product")
        self.edit_product_button.clicked.connect(self.edit_selected_product)
        self.layout.addWidget(self.edit_product_button)

        self.delete_product_button = QPushButton("Delete Selected Product")
        self.delete_product_button.clicked.connect(self.delete_selected_product)
        self.layout.addWidget(self.delete_product_button)

        self.load_products()
        self.setLayout(self.layout)

    def load_products(self):
        # Загружаем данные о товарах в таблицу
        products = self.db.fetch_all("SELECT id, name, price, quantity FROM products")
        self.products_table.setRowCount(len(products))

        for row, product in enumerate(products):
            for col, data in enumerate(product):
                self.products_table.setItem(row, col, QTableWidgetItem(str(data)))

    def edit_selected_product(self):
        # Редактирование выбранного продукта
        current_row = self.products_table.currentRow()
        if current_row != -1:
            product_id = int(self.products_table.item(current_row, 0).text())  # Получаем ID продукта
            dialog = EditProductDialog(self.db, product_id)  # Открываем диалог редактирования
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.load_products()  # Обновляем список продуктов
        else:
            QMessageBox.warning(self, "No Selection", "Please select a product to edit.")

    def add_product(self):
        dialog = AddProductDialog(self.db)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_products()  # Обновляем список продуктов

    def delete_selected_product(self):
        # Удаляем выделенный продукт
        current_row = self.products_table.currentRow()
        if current_row != -1:
            product_id = self.products_table.item(current_row, 0).text()  # Получаем ID продукта
            reply = QMessageBox.question(
                self,
                "Confirm Delete",
                f"Are you sure you want to delete the product with ID {product_id}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.db.query("DELETE FROM products WHERE id = ?", (product_id,))
                self.load_products()
        else:
            QMessageBox.warning(self, "No Selection", "Please select a product to delete.")



class AddProductDialog(QDialog):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setWindowTitle("Add Product")
        self.setGeometry(250, 250, 400, 300)

        self.layout = QVBoxLayout()

        self.product_name_input = QLineEdit()
        self.product_name_input.setPlaceholderText("Product Name")

        self.product_price_input = QLineEdit()
        self.product_price_input.setPlaceholderText("Price(rubles)")

        self.product_quantity_input = QLineEdit()
        self.product_quantity_input.setPlaceholderText("Quantity")
        self.product_quantity_input.setValidator(QIntValidator())

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.layout.addWidget(QLabel("Product Name:"))
        self.layout.addWidget(self.product_name_input)
        self.layout.addWidget(QLabel("Price(rubles):"))
        self.layout.addWidget(self.product_price_input)
        self.layout.addWidget(QLabel("Quantity:"))
        self.layout.addWidget(self.product_quantity_input)

        self.layout.addWidget(self.buttons)
        self.setLayout(self.layout)

    def accept(self):
        name = self.product_name_input.text()
        price = self.product_price_input.text()
        quantity = self.product_quantity_input.text()

        if name and price and quantity.isdigit():
            self.db.query("INSERT INTO products (name, price, quantity) VALUES (?, ?, ?)",
                          (name, float(price), int(quantity)))
            super().accept()
        else:
            QMessageBox.warning(self, "Input Error", "Please fill in all fields correctly.")

class EditProductDialog(QDialog):
    def __init__(self, db, product_id):
        super().__init__()
        self.db = db
        self.product_id = product_id
        self.setWindowTitle("Edit Product")
        self.setGeometry(250, 250, 400, 300)

        self.layout = QVBoxLayout()

        # Загружаем информацию о продукте для редактирования
        product = self.db.fetch_one("SELECT name, price, quantity FROM products WHERE id = ?", (self.product_id,))
        
        self.product_name_input = QLineEdit(product[0])
        self.product_price_input = QLineEdit(str(product[1]))
        self.product_quantity_input = QLineEdit(str(product[2]))
        self.product_quantity_input.setValidator(QIntValidator())

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.layout.addWidget(QLabel("Product Name:"))
        self.layout.addWidget(self.product_name_input)
        self.layout.addWidget(QLabel("Price(rubles):"))
        self.layout.addWidget(self.product_price_input)
        self.layout.addWidget(QLabel("Quantity:"))
        self.layout.addWidget(self.product_quantity_input)

        self.layout.addWidget(self.buttons)
        self.setLayout(self.layout)

    def accept(self):
        name = self.product_name_input.text()
        price = self.product_price_input.text()
        quantity = self.product_quantity_input.text()

        if name and price and quantity.isdigit():
            self.db.query("UPDATE products SET name = ?, price = ?, quantity = ? WHERE id = ?",
                          (name, float(price), int(quantity), self.product_id))
            super().accept()
        else:
            QMessageBox.warning(self, "Input Error", "Please fill in all fields correctly.")

class AddOrderDialog(QDialog):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.selected_product_id = None
        self.selected_quantity = None
        self.setWindowTitle("Add Order")
        self.setGeometry(250, 250, 400, 300)

        self.layout = QVBoxLayout()

        self.product_combobox = QComboBox()
        self.products = self.db.fetch_all("SELECT id, name, price FROM products")
        for product in self.products:
            self.product_combobox.addItem(product[1], product[0])

        self.quantity_input = QLineEdit()
        self.quantity_input.setValidator(QIntValidator())
        self.quantity_input.setPlaceholderText("Quantity")

        self.layout.addWidget(QLabel("Product:"))
        self.layout.addWidget(self.product_combobox)
        self.layout.addWidget(QLabel("Quantity:"))
        self.layout.addWidget(self.quantity_input)

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.layout.addWidget(self.buttons)
        self.setLayout(self.layout)

    def accept(self):
        selected_product = self.product_combobox.currentData()
        quantity = self.quantity_input.text()

        if selected_product and quantity.isdigit() and int(quantity) > 0:
            self.selected_product_id = selected_product
            self.selected_quantity = int(quantity)

            product = self.db.fetch_one("SELECT name, price FROM products WHERE id = ?", (self.selected_product_id,))
            if product:
                self.selected_price = product[1]
                self.selected_order_number = f"ORD-{self.db.fetch_one('SELECT COUNT(*) FROM orders')[0] + 1}"
                super().accept()
            else:
                QMessageBox.warning(self, "Product Error", "Product not found.")
        else:
            QMessageBox.warning(self, "Input Error", "Please enter a valid quantity.")

class EditOrderDialog(QDialog):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setWindowTitle("Edit Order")
        self.setGeometry(250, 250, 400, 300)

        self.layout = QVBoxLayout()

        self.order_number_input = QLineEdit()
        self.product_combobox = QComboBox()
        self.quantity_input = QLineEdit()
        self.status_combobox = QComboBox()

        self.products = self.db.fetch_all("SELECT id, name FROM products")
        for product in self.products:
            self.product_combobox.addItem(product[1], product[0])

        self.status_combobox.addItems(["Pending", "Completed", "Shipped", "Cancelled"])

        self.layout.addWidget(QLabel("Order Number:"))
        self.layout.addWidget(self.order_number_input)
        self.layout.addWidget(QLabel("Product:"))
        self.layout.addWidget(self.product_combobox)
        self.layout.addWidget(QLabel("Quantity:"))
        self.layout.addWidget(self.quantity_input)
        self.layout.addWidget(QLabel("Status:"))
        self.layout.addWidget(self.status_combobox)

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.layout.addWidget(self.buttons)
        self.setLayout(self.layout)

    def accept(self):
        order_number = self.order_number_input.text()
        product_id = self.product_combobox.currentData()
        quantity = self.quantity_input.text()
        status = self.status_combobox.currentText()

        if order_number and product_id and quantity and status:
            product = self.db.fetch_one("SELECT price FROM products WHERE id = ?", (product_id,))
            price = product[0] if product else 0.0
            self.db.query("UPDATE orders SET order_number = ?, product_name = ?, quantity = ?, price = ?, status = ? WHERE order_number = ?",
                          (order_number, self.product_combobox.currentText(), int(quantity), price * int(quantity), status, order_number))
            super().accept()
        else:
            QMessageBox.warning(self, "Input Error", "Please fill in all fields.")

class DeleteOrderDialog(QDialog):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setWindowTitle("Delete Order")
        self.setGeometry(250, 250, 300, 200)

        self.layout = QVBoxLayout()

        self.order_number_input = QLineEdit()
        self.layout.addWidget(QLabel("Order Number:"))
        self.layout.addWidget(self.order_number_input)

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.layout.addWidget(self.buttons)
        self.setLayout(self.layout)

    def accept(self):
        order_number = self.order_number_input.text()
        if order_number:
            self.db.query("DELETE FROM orders WHERE order_number = ?", (order_number,))
            super().accept()
        else:
            QMessageBox.warning(self, "Input Error", "Please enter a valid order number.")

if __name__ == '__main__':
    app = QApplication([])
    window = MainApp()
    window.show()
    app.exec()