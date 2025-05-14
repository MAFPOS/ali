from tkinter import Widget
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFormLayout, QSpinBox, QDoubleSpinBox,
    QComboBox, QTextEdit, QFileDialog, QMessageBox,
    QCheckBox, QGroupBox, QScrollArea, QFrame
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
        scroll_content = Widget()
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
        
        for attr in predefined_attributes:
            cb = QCheckBox(attr)
            self.variant_attributes.append((attr, cb))
            variant_frame_layout.addWidget(cb)
        
        # Custom attribute
        custom_attr_layout = QHBoxLayout()
        self.custom_attr_input = QLineEdit()
        self.custom_attr_input.setPlaceholderText("Autre attribut...")
        add_attr_btn = QPushButton("+")
        add_attr_btn.clicked.connect(self.add_custom_attribute)
        custom_attr_layout.addWidget(self.custom_attr_input)
        custom_attr_layout.addWidget(add_attr_btn)
        variant_frame_layout.addLayout(custom_attr_layout)
        
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

    def get_product_data(self):
        selected_attrs = [
            attr for attr, cb in self.variant_attributes 
            if cb.isChecked()
        ]
        
        return {
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