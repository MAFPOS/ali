from database import get_connection
import json
import os
import sys

def fix_database_connections():
    """Fix issues with database connections and loading"""
    print("Réparation de la connexion à la base de données...")
    
    # Check if database file exists and is accessible
    conn = get_connection()
    if not conn:
        print("ERREUR: Impossible de se connecter à la base de données!")
        return False
    
    try:
        cursor = conn.cursor()
        
        # Check database path
        cursor.execute("PRAGMA database_list")
        db_info = cursor.fetchall()
        db_path = None
        for info in db_info:
            if info[1] == 'main':
                db_path = info[2]
                print(f"Base de données utilisée: {db_path}")
                break
        
        # Check if database is writable
        if db_path and os.path.exists(db_path):
            is_writable = os.access(db_path, os.W_OK)
            if not is_writable:
                print(f"AVERTISSEMENT: La base de données est en lecture seule! ({db_path})")
                print("Tentative de correction des permissions...")
                try:
                    os.chmod(db_path, 0o666)  # rw-rw-rw-
                    print("Permissions mises à jour.")
                except Exception as e:
                    print(f"Impossible de modifier les permissions: {e}")
        
        # Verify database integrity
        cursor.execute("PRAGMA integrity_check")
        integrity = cursor.fetchone()[0]
        if integrity != "ok":
            print(f"AVERTISSEMENT: Problème d'intégrité dans la base de données: {integrity}")
            print("Tentative de réparation...")
            cursor.execute("VACUUM")
            print("Base de données compactée.")
        
        # Make sure Products table exists and has correct structure
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Products'")
        if not cursor.fetchone():
            print("ERREUR CRITIQUE: La table Products n'existe pas!")
            return False
        
        # Check if product loading works
        cursor.execute("SELECT COUNT(*) FROM Products")
        count = cursor.fetchone()[0]
        print(f"Nombre de produits dans la base de données: {count}")
        
        conn.close()
        return True
    except Exception as e:
        print(f"ERREUR lors de la vérification de la base de données: {e}")
        if conn:
            conn.close()
        return False

def fix_product_loading_code():
    """Fix product loading code in UI files"""
    print("\nRéparation du code de chargement des produits...")
    
    ui_dir = os.path.join(os.path.dirname(__file__), "ui")
    product_window_path = os.path.join(ui_dir, "product_management_window.py")
    
    if not os.path.exists(product_window_path):
        print(f"ERREUR: Fichier d'interface introuvable: {product_window_path}")
        return False
    
    # Create a backup of the original file
    backup_path = product_window_path + ".backup"
    try:
        with open(product_window_path, "r", encoding="utf-8") as f:
            original_content = f.read()
        
        with open(backup_path, "w", encoding="utf-8") as f:
            f.write(original_content)
        
        print(f"Sauvegarde créée: {backup_path}")
    except Exception as e:
        print(f"AVERTISSEMENT: Impossible de créer une sauvegarde: {e}")
    
    # Rewrite the load_products method
    try:
        modified_content = original_content
        
        # Find the load_products method
        load_products_start = modified_content.find("def load_products")
        if load_products_start == -1:
            print("Impossible de trouver la méthode load_products dans le fichier.")
            return False
        
        # Find the end of the method (next method definition)
        next_method = modified_content.find("def ", load_products_start + 10)
        if next_method == -1:
            print("Impossible de trouver la fin de la méthode load_products.")
            return False
        
        # Insert our fixed method
        fixed_method = """    def load_products(self, category_id=None):
        \"\"\"Load products from database - FIXED version\"\"\"
        try:
            # Clear table
            self.products_table.setRowCount(0)
            
            # Get products directly with SQL
            from database import get_connection
            conn = get_connection()
            if not conn:
                print("Erreur de connexion à la base de données")
                return
                
            try:
                cursor = conn.cursor()
                
                # Direct SQL query
                if category_id:
                    cursor.execute(\"\"\"
                        SELECT 
                            p.id, p.barcode, p.name, p.unit_price, p.purchase_price,
                            p.stock, p.min_stock, p.category_id, c.name as category_name,
                            p.image_path, p.has_variants, p.variant_attributes, p.description
                        FROM Products p
                        LEFT JOIN Categories c ON p.category_id = c.id
                        WHERE p.category_id = ?
                        ORDER BY p.name
                    \"\"\", (category_id,))
                else:
                    cursor.execute(\"\"\"
                        SELECT 
                            p.id, p.barcode, p.name, p.unit_price, p.purchase_price,
                            p.stock, p.min_stock, p.category_id, c.name as category_name,
                            p.image_path, p.has_variants, p.variant_attributes, p.description
                        FROM Products p
                        LEFT JOIN Categories c ON p.category_id = c.id
                        ORDER BY p.name
                    \"\"\")
                
                # Get column names
                columns = [column[0] for column in cursor.description]
                
                # Fetch rows and convert to dictionaries
                products = []
                for row in cursor.fetchall():
                    product_dict = dict(zip(columns, row))
                    products.append(product_dict)
                
                print(f"Chargé {len(products)} produits depuis la base de données")
                
                # Set row count
                self.products_table.setRowCount(len(products))
                
                # Fill table
                for row, product_dict in enumerate(products):
                    try:
                        # Extract values with defaults
                        product_id = product_dict.get('id', 0)
                        unit_price = float(product_dict.get('unit_price', 0))
                        purchase_price = float(product_dict.get('purchase_price', 0))
                        stock = int(product_dict.get('stock', 0))
                        min_stock = int(product_dict.get('min_stock', 0))
                        
                        # Log for debugging
                        print(f"Affichage du produit: {product_dict['name']} (ID: {product_id})")
                        
                        # ID column
                        id_item = QTableWidgetItem(str(product_id))
                        id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)  # Make read-only
                        self.products_table.setItem(row, 0, id_item)
                        
                        # Image column
                        image_label = QLabel()
                        image_label.setAlignment(Qt.AlignCenter)
                        
                        # Check if image exists
                        if product_dict.get('image_path') and os.path.exists(product_dict.get('image_path', '')):
                            pixmap = QPixmap(product_dict.get('image_path', ''))
                            if not pixmap.isNull():
                                scaled_pixmap = pixmap.scaled(
                                    60, 60,
                                    Qt.KeepAspectRatio,
                                    Qt.SmoothTransformation
                                )
                                image_label.setPixmap(scaled_pixmap)
                        
                        self.products_table.setCellWidget(row, 1, image_label)
                        
                        # Other columns
                        self.products_table.setItem(row, 2, QTableWidgetItem(str(product_dict.get('barcode', ''))))
                        self.products_table.setItem(row, 3, QTableWidgetItem(str(product_dict.get('name', ''))))
                        self.products_table.setItem(row, 4, QTableWidgetItem(f"{unit_price:.2f} MAD"))
                        self.products_table.setItem(row, 5, QTableWidgetItem(f"{purchase_price:.2f} MAD"))
                        
                        # Color stock cell based on min stock
                        stock_item = QTableWidgetItem(str(stock))
                        if stock <= min_stock:
                            stock_item.setBackground(Qt.red)
                            stock_item.setForeground(Qt.white)
                        self.products_table.setItem(row, 6, stock_item)
                        
                        self.products_table.setItem(row, 7, QTableWidgetItem(str(min_stock)))
                        self.products_table.setItem(row, 8, QTableWidgetItem(str(product_dict.get('category_name', ''))))
                        
                        # Variants info
                        has_variants = product_dict.get('has_variants', False)
                        variant_text = "Oui" if has_variants else "Non"
                        
                        if has_variants and product_dict.get('variant_attributes'):
                            try:
                                # Convert to list if it's a string
                                variant_attrs = None
                                if isinstance(product_dict['variant_attributes'], str):
                                    variant_attrs = json.loads(product_dict['variant_attributes'])
                                else:
                                    variant_attrs = product_dict['variant_attributes']
                                    
                                # Handle list or non-list data
                                if isinstance(variant_attrs, list):
                                    variant_text += f"\\n({', '.join(variant_attrs)})"
                                elif isinstance(variant_attrs, dict):
                                    variant_text += f"\\n({', '.join(variant_attrs.keys())})"
                                else:
                                    variant_text += "\\n(Format inconnu)"
                            except Exception as e:
                                print(f"Error parsing variant attributes: {e}")
                                variant_text += "\\n(Erreur de format)"
                        
                        self.products_table.setItem(row, 9, QTableWidgetItem(variant_text))
                        
                        # Profit margin
                        margin = 0
                        if purchase_price > 0:
                            margin = ((unit_price - purchase_price) / purchase_price) * 100
                        self.products_table.setItem(row, 10, QTableWidgetItem(f"{margin:.1f}%"))
                        
                        # Actions buttons
                        actions_widget = QWidget()
                        actions_layout = QHBoxLayout(actions_widget)
                        actions_layout.setContentsMargins(0, 0, 0, 0)
                        
                        stock_btn = QPushButton("📦")
                        variant_btn = QPushButton("🔄")
                        edit_btn = QPushButton("✏️")
                        delete_btn = QPushButton("🗑️")
                        
                        stock_btn.setToolTip("Gérer le stock")
                        variant_btn.setToolTip("Gérer les variantes")
                        edit_btn.setToolTip("Modifier le produit")
                        delete_btn.setToolTip("Supprimer le produit")
                        
                        # Connect buttons to actions
                        stock_btn.clicked.connect(lambda checked, p=product_dict: self.manage_stock(p))
                        edit_btn.clicked.connect(lambda checked, p=product_dict: self.edit_product(p))
                        delete_btn.clicked.connect(lambda checked, id=product_id: self.delete_product(id))
                        variant_btn.clicked.connect(lambda checked, p=product_dict: self.manage_variants(p))
                        
                        # Smaller button sizes
                        for btn in [stock_btn, variant_btn, edit_btn, delete_btn]:
                            btn.setMaximumWidth(40)
                            btn.setMaximumHeight(30)
                        
                        actions_layout.addWidget(stock_btn)
                        
                        if has_variants:
                            actions_layout.addWidget(variant_btn)
                            
                        actions_layout.addWidget(edit_btn)
                        actions_layout.addWidget(delete_btn)
                        actions_layout.addStretch()
                        
                        self.products_table.setCellWidget(row, 11, actions_widget)
                        
                    except Exception as e:
                        print(f"Error loading product row {row}: {e}")
                        print(f"Product data: {product_dict}")
                        import traceback
                        traceback.print_exc()
                        continue
            except Exception as e:
                print(f"Database error: {e}")
                import traceback
                traceback.print_exc()
            finally:
                if conn:
                    conn.close()
        except Exception as e:
            print(f"Error loading products: {e}")
            import traceback
            traceback.print_exc()
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Erreur", f"Erreur lors du chargement des produits: {str(e)}")
"""
        
        # Replace the method
        modified_content = modified_content[:load_products_start] + fixed_method + modified_content[next_method:]
        
        # Fix possible import missing
        if "import os" not in modified_content:
            first_import = modified_content.find("import")
            if first_import != -1:
                import_end = modified_content.find("\n", first_import)
                modified_content = modified_content[:import_end+1] + "\nimport os\nimport json" + modified_content[import_end+1:]
        
        # Write the modified content back to the file
        with open(product_window_path, "w", encoding="utf-8") as f:
            f.write(modified_content)
        
        print("Code de chargement des produits mis à jour avec succès!")
        return True
    except Exception as e:
        print(f"ERREUR lors de la mise à jour du code: {e}")
        import traceback
        traceback.print_exc()
        return False

def reinstall_required_packages():
    """Reinstall required packages to ensure they work correctly"""
    print("\nVérification et réinstallation des packages requis...")
    
    try:
        import subprocess
        
        # PyQt5 with all necessary components
        print("Réinstallation de PyQt5...")
        subprocess.call([sys.executable, "-m", "pip", "install", "--upgrade", "PyQt5"])
        subprocess.call([sys.executable, "-m", "pip", "install", "--upgrade", "PyQt5-sip"])
        subprocess.call([sys.executable, "-m", "pip", "install", "--upgrade", "PyQt5-Qt5"])
        
        print("Installation réussie!")
        return True
    except Exception as e:
        print(f"ERREUR lors de l'installation des packages: {e}")
        return False

def add_force_product():
    """Add a test product directly to the database to test loading"""
    print("\nAjout d'un produit de test forcé...")
    
    conn = get_connection()
    if not conn:
        print("ERREUR: Impossible de se connecter à la base de données!")
        return False
    
    try:
        cursor = conn.cursor()
        
        # Make sure we have a category
        cursor.execute("SELECT id FROM Categories LIMIT 1")
        cat = cursor.fetchone()
        
        if not cat:
            print("Aucune catégorie trouvée, création d'une catégorie...")
            cursor.execute("""
                INSERT INTO Categories (name, description, created_at, updated_at)
                VALUES ('Général', 'Catégorie générale', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """)
            cat_id = cursor.lastrowid
        else:
            cat_id = cat[0]
        
        # Add a test product
        product_name = f"Produit Test Force {int(os.urandom(2).hex(), 16)}"
        cursor.execute("""
            INSERT INTO Products (
                name, description, barcode, unit_price, purchase_price,
                stock, min_stock, category_id, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (
            product_name,
            "Produit de test créé par le script de correction",
            f"TEST{int(os.urandom(2).hex(), 16)}",
            199.99,
            100.00,
            50,
            10,
            cat_id
        ))
        
        prod_id = cursor.lastrowid
        
        conn.commit()
        print(f"Produit de test '{product_name}' créé avec ID {prod_id}")
        
        # Verify it was added
        cursor.execute("SELECT id, name FROM Products WHERE id = ?", (prod_id,))
        result = cursor.fetchone()
        
        if result:
            print(f"Vérification réussie: Produit '{result[1]}' (ID: {result[0]}) existe dans la base de données.")
        else:
            print("ERREUR: Le produit n'a pas été ajouté correctement!")
        
        conn.close()
        return True
    except Exception as e:
        print(f"ERREUR lors de l'ajout du produit: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

def main():
    """Run all fixes"""
    print("=== UTILITAIRE DE RÉPARATION DE CHARGEMENT DE PRODUITS ===\n")
    
    success = True
    
    # Fix 1: Database connections
    if not fix_database_connections():
        print("AVERTISSEMENT: Problèmes avec la connexion à la base de données.")
        success = False
    
    # Fix 2: Product loading code
    if not fix_product_loading_code():
        print("AVERTISSEMENT: Impossible de corriger le code de chargement des produits.")
        success = False
    
    # Fix 3: Add force product
    if not add_force_product():
        print("AVERTISSEMENT: Impossible d'ajouter un produit de test.")
        success = False
    
    # Fix 4: Reinstall required packages
    # Commented out to avoid unnecessary package reinstall
    # if not reinstall_required_packages():
    #     print("AVERTISSEMENT: Problèmes lors de la réinstallation des packages.")
    #     success = False
    
    if success:
        print("\n✅ TOUTES LES RÉPARATIONS ONT ÉTÉ APPLIQUÉES AVEC SUCCÈS!\n")
    else:
        print("\n⚠️ CERTAINES RÉPARATIONS ONT ÉCHOUÉ. VÉRIFIEZ LES MESSAGES CI-DESSUS.\n")
    
    print("Instructions pour tester la correction:")
    print("1. Exécutez l'application: python main.py")
    print("2. Connectez-vous et allez à la page de gestion des produits")
    print("3. Vérifiez si les produits sont maintenant affichés correctement")
    print("4. Si les problèmes persistent, exécutez: python debug_products.py")
    
    return success

if __name__ == "__main__":
    main()
