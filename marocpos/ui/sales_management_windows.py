from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QFrame, QHeaderView, QScrollArea, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QCursor
from models.category import Category
from models.product import Product
from database import get_connection
from datetime import datetime
import pytz

class ProductFrame(QFrame):
    def __init__(self, product, parent=None):
        super().__init__(parent)
        self.product = product
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
            ProductFrame {
                background-color: white;
                border-radius: 10px;
                padding: 10px;
            }
            ProductFrame:hover {
                background-color: #f8f9fa;
            }
        """)
        self.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout(self)
        
        # Product name
        name_label = QLabel(self.product['name'])
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        # Product price
        price_label = QLabel(f"{self.product['unit_price']:.2f} MAD")
        price_label.setAlignment(Qt.AlignCenter)
        price_label.setStyleSheet("color: #28a745; font-weight: bold;")
        
        # Stock info
        stock_label = QLabel(f"Stock: {self.product['stock']}")
        stock_label.setAlignment(Qt.AlignCenter)
        stock_label.setStyleSheet("color: #6c757d; font-size: 12px;")
        
        layout.addWidget(name_label)
        layout.addWidget(price_label)
        layout.addWidget(stock_label)
     ######
class SalesManagementWindow(QWidget):
    def __init__(self, username="MAFPOS"):
        super().__init__()
        self.username = username
        self.current_datetime = datetime.now(pytz.UTC)
        self.current_amount = 0.0  # Add this line to track the current amount
        self.selected_product = None  # Add this to track selected product
        self.init_ui()
        
        # Setup timer for datetime updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_datetime)
        self.timer.start(1000)

    def clear_cart(self):
        """Clear all items from the cart"""
        reply = QMessageBox.question(
            self, 'Confirmation',
            'Voulez-vous vraiment vider le panier ?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.cart_table.setRowCount(0)
            self.update_total()
            self.current_amount = 0.0
            self.selected_product = None

    def keypad_pressed(self, text):
        """Handle keypad button presses"""
        if self.selected_product:
            current_qty = self.cart_table.item(self.selected_row, 1).text()
            
            if text == 'C':
                new_qty = ''
            elif text == '.' and '.' in current_qty:
                return
            else:
                new_qty = current_qty + text
                
            try:
                qty = float(new_qty) if new_qty else 0
                if qty > 0:
                    self.cart_table.setItem(self.selected_row, 1, QTableWidgetItem(str(qty)))
                    self.update_total()
            except ValueError:
                pass

    def remove_from_cart(self, row):
        """Remove an item from the cart"""
        reply = QMessageBox.question(
            self, 'Confirmation',
            'Voulez-vous retirer cet article du panier ?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.cart_table.removeRow(row)
            self.update_total()
            if row == getattr(self, 'selected_row', None):
                self.selected_product = None

    def update_total(self):
        """Update the total amount in the cart"""
        total = 0.0
        for row in range(self.cart_table.rowCount()):
            try:
                qty = float(self.cart_table.item(row, 1).text())
                price = float(self.cart_table.item(row, 2).text())
                total += qty * price
            except (ValueError, AttributeError):
                continue
        
        self.total_amount.setText(f"{total:.2f} MAD")
        self.current_amount = total

    def process_sale(self):
        """Process the sale and save to database"""
        if self.cart_table.rowCount() == 0:
            QMessageBox.warning(self, "Erreur", "Le panier est vide!")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Start transaction
            cursor.execute("BEGIN TRANSACTION")
            
            try:
                # Create sale record
                cursor.execute("""
                    INSERT INTO Sales (
                        date, 
                        total_amount, 
                        user_id
                    ) VALUES (?, ?, ?)
                """, (
                    self.current_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                    self.current_amount,
                    1  # Replace with actual user_id
                ))
                
                sale_id = cursor.lastrowid
                
                # Add sale items
                for row in range(self.cart_table.rowCount()):
                    product_name = self.cart_table.item(row, 0).text()
                    quantity = float(self.cart_table.item(row, 1).text())
                    price = float(self.cart_table.item(row, 2).text())
                    
                    # Get product ID
                    cursor.execute("SELECT id FROM Products WHERE name = ?", (product_name,))
                    product_id = cursor.fetchone()[0]
                    
                    # Add sale item
                    cursor.execute("""
                        INSERT INTO SaleItems (
                            sale_id,
                            product_id,
                            quantity,
                            unit_price
                        ) VALUES (?, ?, ?, ?)
                    """, (sale_id, product_id, quantity, price))
                    
                    # Update product stock
                    cursor.execute("""
                        UPDATE Products 
                        SET stock = stock - ? 
                        WHERE id = ?
                    """, (quantity, product_id))
                
                cursor.execute("COMMIT")
                QMessageBox.information(self, "Succès", "Vente enregistrée avec succès!")
                self.clear_cart()
                
            except Exception as e:
                cursor.execute("ROLLBACK")
                QMessageBox.warning(self, "Erreur", f"Erreur lors de l'enregistrement de la vente: {str(e)}")
                
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Erreur de connexion à la base de données: {str(e)}")
        finally:
            if conn:
                conn.close()

    def update_datetime(self):
        """Update the datetime display"""
        self.current_datetime = datetime.now(pytz.UTC)
        formatted_date = self.current_datetime.strftime("%Y-%m-%d %H:%M:%S")
        self.datetime_label.setText(f"Date: {formatted_date}")
################################################
    def init_ui(self):
        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create left and right sections
        left_section = self.create_left_section()
        right_section = self.create_right_section()

        main_layout.addWidget(left_section, 1)  # 1 for stretch factor
        main_layout.addWidget(right_section, 2)  # 2 for stretch factor

    def create_left_section(self):
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(20, 20, 20, 20)
        left_layout.setSpacing(20)

        # Header with user info and datetime
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        
        # User info
        user_label = QLabel(f"Utilisateur: {self.username}")
        user_label.setStyleSheet("font-weight: bold; color: #495057;")
        header_layout.addWidget(user_label)
        
        # Datetime
        self.datetime_label = QLabel()
        self.datetime_label.setStyleSheet("color: #6c757d;")
        header_layout.addWidget(self.datetime_label)
        
        left_layout.addWidget(header_frame)

        # Cart section
        cart_frame = QFrame()
        cart_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        cart_layout = QVBoxLayout(cart_frame)

        # Cart header
        cart_header = QHBoxLayout()
        cart_title = QLabel("Panier")
        cart_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #212529;")
        cart_header.addWidget(cart_title)
        cart_layout.addLayout(cart_header)

        # Cart table
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(4)
        self.cart_table.setHorizontalHeaderLabels(["Produit", "Quantité", "Prix", ""])
        self.cart_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.cart_table.setStyleSheet("""
            QTableWidget {
                border: none;
                background-color: white;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 8px;
                border: none;
                font-weight: bold;
                color: #495057;
            }
        """)
        cart_layout.addWidget(self.cart_table)

        # Total section
        total_layout = QHBoxLayout()
        total_label = QLabel("Total à payer:")
        total_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        self.total_amount = QLabel("0.00 MAD")
        self.total_amount.setStyleSheet("font-weight: bold; font-size: 18px; color: #28a745;")
        total_layout.addWidget(total_label)
        total_layout.addWidget(self.total_amount, alignment=Qt.AlignRight)
        cart_layout.addLayout(total_layout)

        left_layout.addWidget(cart_frame)

        # Keypad section
        keypad_frame = self.create_keypad()
        left_layout.addWidget(keypad_frame)

        return left_widget

    def create_keypad(self):
        keypad_frame = QFrame()
        keypad_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        keypad_layout = QGridLayout(keypad_frame)
        keypad_layout.setSpacing(10)

        buttons = [
            ('7', 0, 0), ('8', 0, 1), ('9', 0, 2), ('C', 0, 3),
            ('4', 1, 0), ('5', 1, 1), ('6', 1, 2), ('×', 1, 3),
            ('1', 2, 0), ('2', 2, 1), ('3', 2, 2), ('Annuler', 2, 3),
            ('0', 3, 0), ('.', 3, 1), ('00', 3, 2), ('Valider', 3, 3),
        ]

        for text, row, col in buttons:
            btn = QPushButton(text)
            btn.setFixedSize(80, 80)
            btn.setCursor(Qt.PointingHandCursor)
            
            if text == 'Valider':
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #28a745;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        font-size: 14px;
                    }
                    QPushButton:hover {
                        background-color: #218838;
                    }
                """)
                btn.clicked.connect(self.process_sale)
            elif text == 'Annuler':
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #dc3545;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        font-size: 14px;
                    }
                    QPushButton:hover {
                        background-color: #c82333;
                    }
                """)
                btn.clicked.connect(self.clear_cart)
            elif text == 'C':
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #ffc107;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        font-size: 18px;
                    }
                    QPushButton:hover {
                        background-color: #e0a800;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #24786d;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        font-size: 18px;
                    }
                    QPushButton:hover {
                        background-color: #1b5a52;
                    }
                """)
                btn.clicked.connect(lambda checked, t=text: self.keypad_pressed(t))
            
            keypad_layout.addWidget(btn, row, col)

        return keypad_frame

    def create_right_section(self):
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(20, 20, 20, 20)
        right_layout.setSpacing(20)

        # Categories section
        categories_scroll = QScrollArea()
        categories_scroll.setWidgetResizable(True)
        categories_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        categories_scroll.setMaximumHeight(150)

        categories_widget = QWidget()
        self.categories_layout = QGridLayout(categories_widget)
        self.categories_layout.setSpacing(10)
        categories_scroll.setWidget(categories_widget)
        
        self.setup_categories()
        right_layout.addWidget(categories_scroll)

        # Products section
        products_scroll = QScrollArea()
        products_scroll.setWidgetResizable(True)
        products_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        self.products_widget = QWidget()
        self.products_layout = QGridLayout(self.products_widget)
        self.products_layout.setSpacing(10)
        products_scroll.setWidget(self.products_widget)
        
        right_layout.addWidget(products_scroll)

        # Initial load of products
        self.load_products()

        return right_widget

    def setup_categories(self):
        # Clear existing categories
        while self.categories_layout.count():
            item = self.categories_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Add "Tous" button
        tous_btn = QPushButton("Tous")
        tous_btn.setCursor(Qt.PointingHandCursor)
        tous_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                min-width: 150px;
                min-height: 35px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        tous_btn.clicked.connect(lambda: self.filter_by_category(None))
        self.categories_layout.addWidget(tous_btn, 0, 0)

        # Get categories from database
        categories = Category.get_all_categories()
        
        # Add category buttons
        row = 0
        col = 1
        for category in categories:
            if col > 5:  # 6 buttons per row
                row += 1
                col = 0
            
            btn = QPushButton(category[1])
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #007bff;
                    color: white;
                    border: none;
                    padding: 10px;
                    border-radius: 5px;
                    min-width: 150px;
                    min-height: 35px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #0056b3;
                }
            """)
            btn.clicked.connect(lambda checked, id=category[0]: self.filter_by_category(id))
            self.categories_layout.addWidget(btn, row, col)
            col += 1

    def load_products(self, category_id=None):
        # Clear existing products
        while self.products_layout.count():
            item = self.products_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Get products
        products = Product.get_products_by_category(category_id)

        # Add products to grid
        row = 0
        col = 0
        for product in products:
            product_frame = ProductFrame(product)
            product_frame.mousePressEvent = lambda e, p=product: self.add_to_cart(p)
            
            self.products_layout.addWidget(product_frame, row, col)
            
            col += 1
            if col > 2:  # 3 products per row
                col = 0
                row += 1

    def filter_by_category(self, category_id):
        self.load_products(category_id)

    def add_to_cart(self, product):
        # Check if product is already in cart
        for row in range(self.cart_table.rowCount()):
            if self.cart_table.item(row, 0).text() == product['name']:
                # Update quantity
                current_qty = int(self.cart_table.item(row, 1).text())
                self.cart_table.setItem(row, 1, QTableWidgetItem(str(current_qty + 1)))
                self.update_total()
                return

        # Add new product to cart
        row = self.cart_table.rowCount()
        self.cart_table.insertRow(row)
        
        self.cart_table.setItem(row, 0, QTableWidgetItem(product['name']))
        self.cart_table.setItem(row, 1, QTableWidgetItem("1"))
        self.cart_table.setItem(row, 2, QTableWidgetItem(f"{product['unit_price']:.2f}"))
        
        delete_btn = QPushButton("🗑")
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.setStyleSheet("""
            QPushButton {
                border: none;
                color: #6c757d;
            }
            QPushButton:hover {
                color: #dc3545;
            }
        """)
        delete_btn.clicked.connect(lambda: self.remove_from_cart)