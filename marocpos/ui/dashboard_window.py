from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QScrollArea, QGridLayout
)
from PyQt5.QtCore import Qt, QDateTime
from models.category import Category
from ui.user_management_window import UserManagementWindow
from ui.store_management_windows import StoreManagementWindow
from ui.sales_management_windows import SalesManagementWindow
from ui.product_management_window import ProductManagementWindow
from ui.category_management_window import CategoryManagementWindow

class DashboardWindow(QMainWindow):
    def __init__(self, user=None):
        super().__init__()
        self.user = user
        self.current_datetime = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
        self.init_ui()

    def init_ui(self):
        # Set window properties
        self.setWindowTitle("MarocPOS")
        self.setGeometry(0, 0, 1200, 800)
        self.showMaximized()

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create sidebar
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)

        # Create content area
        content = self.create_content_area()
        main_layout.addWidget(content, stretch=1)

    def create_sidebar(self):
        sidebar = QFrame()
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #1a4c7c;
                min-width: 200px;
                max-width: 200px;
                padding: 10px;
            }
        """)

        layout = QVBoxLayout(sidebar)
        layout.setSpacing(5)

        # Add navigation buttons
        buttons = [
            ("🛒 Vente", self.open_sales_window),
            ("📦 Stock", self.open_product_management),
            ("🏷️ Catégories", self.open_category_management),
            ("👥 Clients", self.open_store_management),
            ("📊 Rapports", lambda: None),
            ("👤 Utilisateurs", self.open_user_management),
            ("⚙️ Paramètres", lambda: None),
            ("🚪 Déconnexion", self.logout)
        ]

        for text, handler in buttons:
            btn = QPushButton(text)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    color: #adb5bd;
                    border: none;
                    text-align: left;
                    padding: 12px;
                    font-size: 16px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: rgba(255,255,255,0.1);
                    color: white;
                }
            """)
            btn.clicked.connect(handler)
            layout.addWidget(btn)

        layout.addStretch()
        return sidebar

    def create_content_area(self):
        content = QWidget()
        content.setStyleSheet("background-color: white;")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header with user info and datetime
        header = QHBoxLayout()
        
        store_label = QLabel("Boutique Casablanca")
        store_label.setStyleSheet("color: #333; font-size: 14px; font-weight: bold;")
        
        username_label = QLabel("MAFPOS")
        username_label.setStyleSheet("color: #6c757d; font-size: 14px;")
        
        datetime_label = QLabel(self.current_datetime)
        datetime_label.setStyleSheet("color: #6c757d; font-size: 14px;")

        header.addWidget(store_label)
        header.addWidget(QLabel(" | "))
        header.addWidget(username_label)
        header.addWidget(QLabel(" | "))
        header.addWidget(datetime_label)
        header.addStretch()

        layout.addLayout(header)

        # Category buttons area
        category_scroll = QScrollArea()
        category_scroll.setWidgetResizable(True)
        category_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        category_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        category_widget = QWidget()
        self.category_layout = QGridLayout(category_widget)
        self.category_layout.setSpacing(10)
        
        category_scroll.setWidget(category_widget)
        layout.addWidget(category_scroll)

        # Setup category buttons
        self.setup_category_buttons()

        # Initially show sales management
        self.sales_mgmt_window = SalesManagementWindow()
        layout.addWidget(self.sales_mgmt_window)

        return content

    def setup_category_buttons(self):
        categories = Category.get_all_categories()
        
        # Clear existing buttons
        while self.category_layout.count():
            item = self.category_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Add "Tous" button
        all_btn = QPushButton("Tous")
        all_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        all_btn.clicked.connect(lambda: self.filter_by_category(None))
        self.category_layout.addWidget(all_btn, 0, 0)

        # Add category buttons in a grid
        row = 0
        col = 1
        for category in categories:
            if col > 5:  # Start new row after 6 buttons
                row += 1
                col = 0

            btn = QPushButton(category[1])  # category name
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #007bff;
                    color: white;
                    border: none;
                    padding: 10px;
                    border-radius: 5px;
                    min-width: 100px;
                }
                QPushButton:hover {
                    background-color: #0056b3;
                }
            """)
            btn.clicked.connect(lambda checked, cat_id=category[0]: self.filter_by_category(cat_id))
            self.category_layout.addWidget(btn, row, col)
            col += 1

    def filter_by_category(self, category_id):
        # TODO: Implement category filtering
        pass

    def open_sales_window(self):
        """Open the Sales window."""
        self.sales_window = SalesManagementWindow()
        self.sales_window.show()

    def open_product_management(self):
        """Open the Product Management window."""
        self.product_mgmt_window = ProductManagementWindow()
        self.product_mgmt_window.show()

    def open_category_management(self):
        """Open the Category Management window."""
        self.category_mgmt_window = CategoryManagementWindow()
        self.category_mgmt_window.show()

    def open_store_management(self):
        """Open the Store Management window."""
        self.store_mgmt_window = StoreManagementWindow()
        self.store_mgmt_window.show()

    def open_user_management(self):
        """Open the User Management window."""
        self.user_mgmt_window = UserManagementWindow()
        self.user_mgmt_window.show()

    def logout(self):
        """Logout the user and show login window."""
        from ui.login_window import LoginWindow  # Import here to avoid circular import
        self.close()
        self.login_window = LoginWindow()
        self.login_window.show()