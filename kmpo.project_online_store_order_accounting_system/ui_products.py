from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QLabel, QFormLayout, QDialogButtonBox

class ProductManager(QDialog):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setWindowTitle("Product Management")
        self.setGeometry(200, 200, 600, 400)

        self.layout = QVBoxLayout()

        # Table to display products
        self.product_table = QTableWidget()
        self.product_table.setColumnCount(3)
        self.product_table.setHorizontalHeaderLabels(["Name", "Price", "Stock"])

        # Button to add a product
        self.add_product_btn = QPushButton("Add Product")
        self.add_product_btn.clicked.connect(self.add_product)

        # Add widgets to layout
        self.layout.addWidget(self.product_table)
        self.layout.addWidget(self.add_product_btn)

        self.setLayout(self.layout)
        self.load_products()

    def load_products(self):
        products = self.db.fetch_all("SELECT name, price, stock FROM products")
        self.product_table.setRowCount(len(products))
        for row_idx, product in enumerate(products):
            for col_idx, value in enumerate(product):
                self.product_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

    def add_product(self):
        # Open the product adding dialog
        dialog = AddProductDialog(self.db)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_products()  # Reload the product list after adding a new product

class AddProductDialog(QDialog):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setWindowTitle("Add New Product")
        self.setGeometry(250, 250, 400, 300)

        self.layout = QFormLayout()

        # Fields for product details
        self.product_name_input = QLineEdit()
        self.product_price_input = QLineEdit()
        self.product_stock_input = QLineEdit()

        # Form layout to arrange the input fields
        self.layout.addRow("Product Name:", self.product_name_input)
        self.layout.addRow("Price:", self.product_price_input)
        self.layout.addRow("Stock Quantity:", self.product_stock_input)

        # Buttons for confirming or cancelling
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.layout.addWidget(self.buttons)
        self.setLayout(self.layout)

    def accept(self):
        # Get data from inputs
        name = self.product_name_input.text()
        price = self.product_price_input.text()
        stock = self.product_stock_input.text()

        if name and price and stock:
            # Insert new product into the database
            self.db.query("INSERT INTO products (name, price, stock) VALUES (?, ?, ?)", (name, float(price), int(stock)))
            super().accept()
        else:
            # If fields are empty, show an error message
            QMessageBox.warning(self, "Input Error", "Please fill in all fields.")
