from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFormLayout, QSpinBox, QDoubleSpinBox,
    QComboBox, QTextEdit, QFileDialog, QMessageBox,
    QCheckBox, QGroupBox, QScrollArea, QFrame, QWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from models.category import Category
from datetime import datetime
import os
import shutil
import json

class AddProductDialog(QDialog):
    def __init__(self, parent=None, product=None):
        super().__init__(parent)
        self.product = product
        self.image_path = None
        self.variant_widgets = []
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Ajouter un produit" if not self.product else "Modifier le produit")
        self.setMinimumWidth(600)
        
        # Main Layout with ScrollArea
        main_layout = QVBoxLayout()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        form_layout = QFormLayout()

        # Basic Information Group
        basic_group = QGroupBox("Informations de base")
        basic_layout = QFormLayout()
        
        # Code barre
        self.barcode_input = QLineEdit()
        basic_layout.addRow("Code barre:", self.barcode_input)
        
        # Nom
        self.name_input = QLineEdit()
        basic_layout.addRow("Nom:", self.name_input)
        
        # Description
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(60)
        basic_layout.addRow("Description:", self.description_input)
        
        # Prix
        price_layout = QHBoxLayout()
        
        self.selling_price = QDoubleSpinBox()
        self.selling_price.setMaximum(999999.99)
        self.selling_price.setSuffix(" MAD")
        price_layout.addWidget(QLabel("Prix de vente:"))
        price_layout.addWidget(self.selling_price)
        
        self.purchase_price = QDoubleSpinBox()
        self.purchase_price.setMaximum(999999.99)
        self.purchase_price.setSuffix(" MAD")
        price_layout.addWidget(QLabel("Prix d'achat:"))
        price_layout.addWidget(self.purchase_price)
        
        self.margin_label = QLabel("0%")
        price_layout.addWidget(QLabel("Marge:"))
        price_layout.addWidget(self.margin_label)
        
        basic_layout.addRow(price_layout)
        
        # Stock
        stock_layout = QHBoxLayout()
        
        self.stock_input = QSpinBox()
        self.stock_input.setMaximum(999999)
        stock_layout.addWidget(QLabel("Stock:"))
        stock_layout.addWidget(self.stock_input)
        
        self.min_stock = QSpinBox()
        self.min_stock.setMaximum(999999)
        stock_layout.addWidget(QLabel("Stock minimum:"))
        stock_layout.addWidget(self.min_stock)
        
        basic_layout.addRow(stock_layout)
        
        basic_group.setLayout(basic_layout)
        form_layout.addRow(basic_group)

        # Variants Group
        variant_group = QGroupBox("Variantes")
        variant_layout = QVBoxLayout()
        
        # Has variants checkbox
        self.has_variants = QCheckBox("Article avec variantes")
        self.has_variants.stateChanged.connect(self.toggle_variant_options)
        variant_layout.addWidget(self.has_variants)
        
        # Variant options frame
        self.variant_frame = QFrame()
        variant_frame_layout = QVBoxLayout()
        
        # Predefined attributes
        self.variant_attributes = []
        predefined_attributes = ["Taille", "Couleur", "Matériau", "Style"]
        
        # Attribute checkbox group
        attr_group = QGroupBox("Attributs disponibles")
        attr_layout = QVBoxLayout()
        
        for attr in predefined_attributes:
            cb = QCheckBox(attr)
            self.variant_attributes.append((attr, cb))
            attr_layout.addWidget(cb)
        
        # Custom attribute
        custom_attr_layout = QHBoxLayout()
        self.custom_attr_input = QLineEdit()
        self.custom_attr_input.setPlaceholderText("Autre attribut...")
        add_attr_btn = QPushButton("+")
        add_attr_btn.clicked.connect(self.add_custom_attribute)
        custom_attr_layout.addWidget(self.custom_attr_input)
        custom_attr_layout.addWidget(add_attr_btn)
        attr_layout.addLayout(custom_attr_layout)
        
        # Manage attributes button
        manage_attr_btn = QPushButton("Gérer tous les attributs")
        manage_attr_btn.clicked.connect(self.manage_attributes)
        attr_layout.addWidget(manage_attr_btn)
        
        attr_group.setLayout(attr_layout)
        variant_frame_layout.addWidget(attr_group)
        
        # Variant management section
        variant_mgmt_layout = QHBoxLayout()
        
        # Button to open variant management
        manage_variants_btn = QPushButton("Gérer les variantes")
        manage_variants_btn.clicked.connect(self.manage_variants)
        manage_variants_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                padding: 8px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        variant_mgmt_layout.addWidget(manage_variants_btn)
        
        # Variant count label
        self.variant_count_label = QLabel("Aucune variante configurée")
        self.variant_count_label.setStyleSheet("color: #666;")
        variant_mgmt_layout.addWidget(self.variant_count_label)
        
        variant_frame_layout.addLayout(variant_mgmt_layout)
        
        # Initialize variants data
        self.variants_data = []
        
        self.variant_frame.setLayout(variant_frame_layout)
        self.variant_frame.setEnabled(False)
        variant_layout.addWidget(self.variant_frame)
        
        variant_group.setLayout(variant_layout)
        form_layout.addRow(variant_group)

        # Image Group
        image_group = QGroupBox("Image")
        image_layout = QHBoxLayout()
        
        self.image_button = QPushButton("Sélectionner une image")
        self.image_button.clicked.connect(self.select_image)
        self.image_label = QLabel()
        self.image_label.setFixedSize(100, 100)
        self.image_label.setStyleSheet("border: 1px solid #ccc;")
        
        image_layout.addWidget(self.image_button)
        image_layout.addWidget(self.image_label)
        image_group.setLayout(image_layout)
        form_layout.addRow(image_group)

        # Category
        self.category_combo = QComboBox()
        self.load_categories()
        form_layout.addRow("Catégorie:", self.category_combo)

        scroll_content.setLayout(form_layout)
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Enregistrer")
        cancel_button = QPushButton("Annuler")
        
        save_button.clicked.connect(self.validate_and_accept)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        
        # Connect signals
        self.selling_price.valueChanged.connect(self.calculate_margin)
        self.purchase_price.valueChanged.connect(self.calculate_margin)
        
        # Fill data if editing
        if self.product:
            self.fill_product_data()

    def toggle_variant_options(self, state):
        self.variant_frame.setEnabled(state == Qt.Checked)
        
    def manage_variants(self):
        """Open the variant management dialog"""
        from .variant_management_dialog import VariantManagementDialog

        # Collect selected attributes
        selected_attrs = [
            attr for attr, cb in self.variant_attributes 
            if cb.isChecked()
        ]
        
        # Show the variant management dialog
        dialog = VariantManagementDialog(
            product_id=self.product['id'] if self.product else None,
            parent=self,
            variant_attributes=selected_attrs
        )
        
        if dialog.exec_():
            # Get the variant data
            self.variants_data = dialog.get_variants_data()
            # Update attribute list
            attr_names = dialog.get_attribute_names()
            
            # Update variant count label
            if self.variants_data:
                self.variant_count_label.setText(f"{len(self.variants_data)} variantes configurées")
                self.variant_count_label.setStyleSheet("color: green; font-weight: bold;")
            else:
                self.variant_count_label.setText("Aucune variante configurée")
                self.variant_count_label.setStyleSheet("color: #666;")
                
            # Update the selected attributes in the UI
            for attr, cb in self.variant_attributes:
                cb.setChecked(attr in attr_names)

    def add_custom_attribute(self):
        attr_name = self.custom_attr_input.text().strip()
        if attr_name:
            for existing_attr, _ in self.variant_attributes:
                if existing_attr.lower() == attr_name.lower():
                    QMessageBox.warning(self, "Erreur", "Cet attribut existe déjà!")
                    return
            
            cb = QCheckBox(attr_name)
            self.variant_attributes.append((attr_name, cb))
            self.variant_frame.layout().insertWidget(
                len(self.variant_attributes) - 1,
                cb
            )
            self.custom_attr_input.clear()

    # ... (rest of the methods remain the same)

    def manage_attributes(self):
        """Open the attribute management dialog"""
        from .attribute_management_dialog import AttributeManagementDialog
        dialog = AttributeManagementDialog(self)
        dialog.exec_()
        # We could refresh our attribute list here if needed

    def get_product_data(self):
        selected_attrs = [
            attr for attr, cb in self.variant_attributes 
            if cb.isChecked()
        ]
        
        data = {
            'barcode': self.barcode_input.text(),
            'name': self.name_input.text().strip(),
            'description': self.description_input.toPlainText(),
            'unit_price': self.selling_price.value(),
            'purchase_price': self.purchase_price.value(),
            'stock': self.stock_input.value(),
            'min_stock': self.min_stock.value(),
            'category_id': self.category_combo.currentData(),
            'image_path': self.image_path,
            'has_variants': self.has_variants.isChecked(),
            'variant_attributes': json.dumps(selected_attrs) if selected_attrs else None
        }
        
        # Add variants data if we have it
        if hasattr(self, 'variants_data') and self.variants_data and self.has_variants.isChecked():
            data['variants'] = self.variants_data
            
        return data