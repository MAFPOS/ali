from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, 
    QPushButton, QLabel, QLineEdit, QComboBox, QMessageBox, QDialog,
    QFormLayout, QDialogButtonBox
)
from PyQt5.QtCore import Qt
from models.user import User

class AddEditUserDialog(QDialog):
    def __init__(self, parent=None, user=None):
        super().__init__(parent)
        self.user = user
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Add User" if not self.user else "Edit User")
        layout = QFormLayout()

        # Username field
        self.username_input = QLineEdit()
        if self.user:
            self.username_input.setText(self.user['username'])
        layout.addRow("Username:", self.username_input)

        # Password field (only for new users)
        if not self.user:
            self.password_input = QLineEdit()
            self.password_input.setEchoMode(QLineEdit.Password)
            layout.addRow("Password:", self.password_input)

        # Role selection
        self.role_combo = QComboBox()
        self.role_combo.addItems(["Admin", "Cashier", "Manager"])
        if self.user:
            self.role_combo.setCurrentText(self.user['role'])
        layout.addRow("Role:", self.role_combo)

        # Active status
        self.active_combo = QComboBox()
        self.active_combo.addItems(["Yes", "No"])
        if self.user:
            self.active_combo.setCurrentText("Yes" if self.user['active'] else "No")
        layout.addRow("Active:", self.active_combo)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        self.setLayout(layout)

    def get_data(self):
        return {
            'username': self.username_input.text(),
            'password': getattr(self, 'password_input', None) and self.password_input.text(),
            'role': self.role_combo.currentText(),
            'active': 1 if self.active_combo.currentText() == "Yes" else 0
        }

class UserManagementWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Set window properties
        self.setWindowTitle("User Management - MarocPOS")
        self.setGeometry(100, 100, 900, 600)

        # Main layout
        layout = QVBoxLayout()

        # Header with title and add button
        header_layout = QHBoxLayout()
        title = QLabel("User Management")
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
            }
        """)
        add_user_button = QPushButton("Add New User")
        add_user_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(add_user_button)
        layout.addLayout(header_layout)

        # Search box
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search users...")
        self.search_input.textChanged.connect(self.filter_users)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # Table
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(6)
        self.user_table.setHorizontalHeaderLabels([
            "ID", "Username", "Role", "Active", "Last Login", "Actions"
        ])
        self.user_table.horizontalHeader().setStretchLastSection(True)
        self.user_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #dcdde1;
                border-radius: 4px;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #f5f6fa;
                padding: 5px;
                border: none;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.user_table)

        # Connect buttons
        add_user_button.clicked.connect(self.add_user)

        self.setLayout(layout)
        self.load_users()

    def load_users(self):
        users = User.get_all_users()
        self.user_table.setRowCount(len(users))

        for row, user in enumerate(users):
            # ID
            id_item = QTableWidgetItem(str(user['id']))
            id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
            self.user_table.setItem(row, 0, id_item)

            # Username
            self.user_table.setItem(row, 1, QTableWidgetItem(user['username']))

            # Role
            self.user_table.setItem(row, 2, QTableWidgetItem(user['role']))

            # Active status
            self.user_table.setItem(row, 3, QTableWidgetItem("Yes" if user['active'] else "No"))

            # Last login (placeholder)
            self.user_table.setItem(row, 4, QTableWidgetItem("-"))

            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(4, 4, 4, 4)

            # Edit button
            edit_btn = QPushButton("✏️")
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    padding: 5px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            edit_btn.clicked.connect(lambda checked, u=user: self.edit_user(u))

            # Delete button
            delete_btn = QPushButton("🗑️")
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    padding: 5px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            delete_btn.clicked.connect(lambda checked, id=user['id']: self.delete_user(id))

            # Reset password button
            reset_btn = QPushButton("🔑")
            reset_btn.setStyleSheet("""
                QPushButton {
                    background-color: #f1c40f;
                    color: white;
                    border: none;
                    padding: 5px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #f39c12;
                }
            """)
            reset_btn.clicked.connect(lambda checked, id=user['id']: self.reset_password(id))

            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(reset_btn)
            actions_layout.addWidget(delete_btn)
            actions_layout.addStretch()

            self.user_table.setCellWidget(row, 5, actions_widget)

        self.user_table.resizeColumnsToContents()

    def add_user(self):
        dialog = AddEditUserDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            user = User(
                username=data['username'],
                password=data['password'],
                role=data['role'],
                active=data['active']
            )
            if User.add_user(user):
                QMessageBox.information(self, "Success", "User added successfully!")
                self.load_users()
            else:
                QMessageBox.warning(self, "Error", "Failed to add user!")

    def edit_user(self, user):
        dialog = AddEditUserDialog(self, user)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if User.update_user(user['id'], data['username'], data['role'], data['active']):
                QMessageBox.information(self, "Success", "User updated successfully!")
                self.load_users()
            else:
                QMessageBox.warning(self, "Error", "Failed to update user!")

    def delete_user(self, user_id):
        reply = QMessageBox.question(
            self, 'Confirmation',
            "Are you sure you want to delete this user?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            if User.delete_user(user_id):
                QMessageBox.information(self, "Success", "User deleted successfully!")
                self.load_users()
            else:
                QMessageBox.warning(self, "Error", "Failed to delete user!")

    def reset_password(self, user_id):
        dialog = QDialog(self)
        dialog.setWindowTitle("Reset Password")
        layout = QFormLayout()

        password_input = QLineEdit()
        password_input.setEchoMode(QLineEdit.Password)
        confirm_input = QLineEdit()
        confirm_input.setEchoMode(QLineEdit.Password)

        layout.addRow("New Password:", password_input)
        layout.addRow("Confirm Password:", confirm_input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, dialog
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)

        dialog.setLayout(layout)

        if dialog.exec_() == QDialog.Accepted:
            if password_input.text() != confirm_input.text():
                QMessageBox.warning(self, "Error", "Passwords do not match!")
                return
            if User.update_password(user_id, password_input.text()):
                QMessageBox.information(self, "Success", "Password reset successfully!")
            else:
                QMessageBox.warning(self, "Error", "Failed to reset password!")

    def filter_users(self):
        search_text = self.search_input.text().lower()
        for row in range(self.user_table.rowCount()):
            username = self.user_table.item(row, 1).text().lower()
            role = self.user_table.item(row, 2).text().lower()
            self.user_table.setRowHidden(
                row, 
                search_text not in username and search_text not in role
            )