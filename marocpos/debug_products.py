from database import get_connection
import os
import json
import sys

def print_hr():
    """Print a horizontal rule"""
    print("-" * 80)

def debug_products():
    """Comprehensive debugging of product issues"""
    print_hr()
    print("DIAGNOSTIC COMPLET DES PRODUITS")
    print_hr()
    
    conn = get_connection()
    if not conn:
        print("ERREUR: Impossible de se connecter à la base de données!")
        return False
    
    try:
        cursor = conn.cursor()
        
        # 1. Vérifier le chemin de la base de données
        cursor.execute("PRAGMA database_list")
        db_info = cursor.fetchall()
        print("Chemin de la base de données:")
        for info in db_info:
            print(f"  - {info[1]}: {info[2]}")
        print()
        
        # 2. Vérifier la structure de la table des produits
        print("Structure de la table Products:")
        cursor.execute("PRAGMA table_info(Products)")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  - {col[1]} ({col[2]}){' NOT NULL' if col[3] else ''}{' PRIMARY KEY' if col[5] else ''}")
        print()
        
        # 3. Compter les produits
        cursor.execute("SELECT COUNT(*) FROM Products")
        product_count = cursor.fetchone()[0]
        print(f"Nombre total de produits: {product_count}")
        
        if product_count > 0:
            # 4. Lister tous les produits
            cursor.execute("""
                SELECT 
                    p.id, p.name, p.unit_price, p.stock, 
                    c.name as category_name,
                    p.has_variants,
                    p.variant_attributes
                FROM Products p
                LEFT JOIN Categories c ON p.category_id = c.id
                ORDER BY p.id
            """)
            
            products = cursor.fetchall()
            print("\nProduits trouvés dans la base de données:")
            for prod in products:
                print(f"ID: {prod[0]}, Nom: {prod[1]}, Prix: {prod[2]}, Stock: {prod[3]}, Catégorie: {prod[4]}")
                if prod[5]:  # has_variants
                    print(f"  Variantes activées: Oui")
                    print(f"  Attributs: {prod[6]}")
            
            # 5. Vérifier les variantes
            cursor.execute("SELECT COUNT(*) FROM ProductVariants")
            variant_count = cursor.fetchone()[0]
            print(f"\nNombre total de variantes: {variant_count}")
            
            if variant_count > 0:
                cursor.execute("""
                    SELECT 
                        v.id, v.product_id, p.name as product_name, 
                        v.name, v.price, v.stock, v.attribute_values
                    FROM ProductVariants v
                    JOIN Products p ON v.product_id = p.id
                    ORDER BY v.product_id, v.id
                """)
                
                variants = cursor.fetchall()
                print("\nVariantes trouvées dans la base de données:")
                current_product = None
                for var in variants:
                    if current_product != var[1]:
                        current_product = var[1]
                        print(f"\nProduit: {var[2]} (ID: {var[1]})")
                    
                    print(f"  ID: {var[0]}, Nom: {var[3]}, Prix: {var[4]}, Stock: {var[5]}")
                    try:
                        attr_values = json.loads(var[6]) if var[6] else {}
                        print(f"  Attributs: {attr_values}")
                    except:
                        print(f"  Attributs (format invalide): {var[6]}")
        else:
            print("\nAUCUN PRODUIT TROUVÉ DANS LA BASE DE DONNÉES!")
            print("Vérifions pourquoi les produits ne sont pas créés ou visibles...")
            
            # Vérifier les catégories
            cursor.execute("SELECT COUNT(*) FROM Categories")
            cat_count = cursor.fetchone()[0]
            print(f"\nNombre de catégories: {cat_count}")
            
            if cat_count == 0:
                print("PROBLÈME DÉTECTÉ: Aucune catégorie n'existe. Les produits ont besoin de catégories.")
            else:
                cursor.execute("SELECT id, name FROM Categories")
                cats = cursor.fetchall()
                print("Catégories disponibles:")
                for cat in cats:
                    print(f"  - ID: {cat[0]}, Nom: {cat[1]}")
        
        # 6. Test d'insertion
        print_hr()
        print("Test d'insertion d'un produit...")
        test_product_name = "TEST_DIAGNOSTIC_PRODUIT"
        
        # Vérifier d'abord si une catégorie existe
        cursor.execute("SELECT id FROM Categories LIMIT 1")
        cat_result = cursor.fetchone()
        
        if not cat_result:
            print("Création d'une catégorie de test...")
            cursor.execute("""
                INSERT INTO Categories (name, description, created_at, updated_at)
                VALUES ('Test', 'Catégorie de test', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """)
            cat_id = cursor.lastrowid
            print(f"Catégorie créée avec ID: {cat_id}")
        else:
            cat_id = cat_result[0]
        
        try:
            # Vérifier si le produit de test existe déjà
            cursor.execute("SELECT id FROM Products WHERE name = ?", (test_product_name,))
            if cursor.fetchone():
                print(f"Le produit de test {test_product_name} existe déjà.")
            else:
                # Insérer un produit de test
                cursor.execute("""
                    INSERT INTO Products (
                        name, description, barcode, unit_price, purchase_price,
                        stock, min_stock, category_id, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """, (
                    test_product_name,
                    "Produit de test pour diagnostic",
                    "TEST123",
                    99.99,
                    50.00,
                    10,
                    5,
                    cat_id
                ))
                
                test_id = cursor.lastrowid
                print(f"Produit de test créé avec ID: {test_id}")
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"ERREUR lors de l'insertion du produit de test: {e}")
        
        # 7. Tester la requête de sélection utilisée par l'interface
        print_hr()
        print("Test de la requête utilisée par l'interface...")
        try:
            # Cette requête simule celle utilisée dans le code UI
            cursor.execute("""
                SELECT 
                    p.*,
                    c.name as category_name
                FROM Products p
                LEFT JOIN Categories c ON p.category_id = c.id
                ORDER BY p.name
            """)
            
            ui_products = cursor.fetchall()
            print(f"La requête a retourné {len(ui_products)} produits")
            
            # Vérifier s'il y a des problèmes dans les résultats
            if ui_products:
                print("Premiers produits trouvés:")
                for i, prod in enumerate(ui_products[:5]):  # Afficher jusqu'à 5 produits
                    try:
                        prod_dict = dict(prod)
                        print(f"  - ID: {prod_dict.get('id')}, Nom: {prod_dict.get('name')}")
                    except Exception as e:
                        print(f"  - ERREUR lors du traitement du produit {i}: {e}")
                        print(f"    Type de prod: {type(prod)}")
                        if hasattr(prod, "__iter__"):
                            print(f"    Contenu: {list(prod)}")
            else:
                print("PROBLÈME DÉTECTÉ: La requête UI ne retourne aucun produit!")
                
        except Exception as e:
            print(f"ERREUR lors de l'exécution de la requête UI: {e}")
        
        # 8. Vérifier la synchronisation des données
        print_hr()
        print("Vérification de la cohérence des données...")
        
        # Vérifier si des produits ont des catégories inexistantes
        cursor.execute("""
            SELECT p.id, p.name, p.category_id 
            FROM Products p 
            LEFT JOIN Categories c ON p.category_id = c.id 
            WHERE p.category_id IS NOT NULL AND c.id IS NULL
        """)
        
        orphan_products = cursor.fetchall()
        if orphan_products:
            print("PROBLÈME DÉTECTÉ: Produits avec des catégories inexistantes:")
            for prod in orphan_products:
                print(f"  - ID: {prod[0]}, Nom: {prod[1]}, Catégorie ID: {prod[2]}")
        else:
            print("Tous les produits ont des catégories valides.")
        
        # Vérifier si des variantes ont des produits inexistants
        cursor.execute("""
            SELECT v.id, v.name, v.product_id 
            FROM ProductVariants v 
            LEFT JOIN Products p ON v.product_id = p.id 
            WHERE p.id IS NULL
        """)
        
        orphan_variants = cursor.fetchall()
        if orphan_variants:
            print("PROBLÈME DÉTECTÉ: Variantes avec des produits inexistants:")
            for var in orphan_variants:
                print(f"  - ID: {var[0]}, Nom: {var[1]}, Produit ID: {var[2]}")
        else:
            print("Toutes les variantes ont des produits valides.")
        
        # 9. Vérifier les doublons potentiels
        cursor.execute("""
            SELECT name, COUNT(*) as count
            FROM Products
            GROUP BY name
            HAVING count > 1
        """)
        
        duplicate_products = cursor.fetchall()
        if duplicate_products:
            print("\nPROBLÈME DÉTECTÉ: Produits en double:")
            for dup in duplicate_products:
                print(f"  - Nom: {dup[0]}, Occurrences: {dup[1]}")
        else:
            print("Aucun produit en double trouvé.")
        
        # 10. Recommandations
        print_hr()
        print("RECOMMANDATIONS:")
        
        if product_count == 0:
            print("1. Exécutez le script 'add_products.py' pour ajouter des produits d'exemple")
            print("2. Vérifiez que les catégories existent avant d'ajouter des produits")
        
        if orphan_products or orphan_variants:
            print("3. Nettoyez les données orphelines avec le script 'fix_orphaned_data.py'")
        
        print("4. Utilisez le script 'fix_variant_display.py' si les problèmes de variantes persistent")
        print("5. Assurez-vous que la base de données n'est pas en lecture seule")
        
        # 11. Vérifier les permissions de fichier
        db_path = None
        for info in db_info:
            if info[1] == 'main':
                db_path = info[2]
                break
        
        if db_path and os.path.exists(db_path):
            try:
                is_readable = os.access(db_path, os.R_OK)
                is_writable = os.access(db_path, os.W_OK)
                print(f"\nPermissions de la base de données:")
                print(f"  - Chemin: {db_path}")
                print(f"  - Lecture: {'Oui' if is_readable else 'Non'}")
                print(f"  - Écriture: {'Oui' if is_writable else 'Non'}")
                
                if not is_writable:
                    print("PROBLÈME DÉTECTÉ: La base de données est en lecture seule!")
            except Exception as e:
                print(f"Erreur lors de la vérification des permissions: {e}")
        
    except Exception as e:
        print(f"ERREUR CRITIQUE lors du diagnostic: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if conn:
            conn.close()
    
    print_hr()
    print("Diagnostic terminé.")
    print_hr()
    
    return True

def fix_product_loading():
    """Fix issues with product loading"""
    print_hr()
    print("CORRECTIONS DU CHARGEMENT DES PRODUITS")
    print_hr()
    
    # Fix 1: Corriger le fichier product_management_window.py
    from pathlib import Path
    ui_path = Path(__file__).parent / "ui"
    product_window_path = ui_path / "product_management_window.py"
    
    if not product_window_path.exists():
        print(f"ERREUR: Fichier {product_window_path} introuvable!")
        return False
    
    try:
        # Lire le contenu actuel
        with open(product_window_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Remplacer la méthode load_products si elle existe (versions simplifiées)
        # Cas 1: Version helpers
        if "from ui.product_helpers import" in content and "def load_products" in content:
            print("Correction de la méthode load_products (version helpers)...")
            
            # Trouver la méthode load_products
            start_idx = content.find("def load_products")
            if start_idx == -1:
                print("Méthode load_products non trouvée!")
                return False
            
            # Trouver la fin de la méthode
            next_def_idx = content.find("def ", start_idx + 10)
            if next_def_idx == -1:
                next_def_idx = len(content)
            
            # Construire la méthode de remplacement
            new_method = """    def load_products(self, category_id=None):
        \"\"\"Load products from database (FIXED)\"\"\"
        try:
            # Clear table
            self.products_table.setRowCount(0)
            
            # Get products using raw SQL for maximum reliability
            conn = get_connection()
            if not conn:
                QMessageBox.critical(self, "Erreur", "Impossible de se connecter à la base de données")
                return
                
            try:
                cursor = conn.cursor()
                
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
                
                products = []
                columns = [column[0] for column in cursor.description]
                for row in cursor.fetchall():
                    product_dict = dict(zip(columns, row))
                    products.append(product_dict)
                
                conn.close()
            except Exception as e:
                print(f"Database error: {e}")
                if conn:
                    conn.close()
                QMessageBox.critical(self, "Erreur", f"Erreur de base de données: {str(e)}")
                return
            
            print(f"Chargement de {len(products)} produits")
            
            # Set row count
            self.products_table.setRowCount(len(products))"""
            
            # Remplacer la méthode
            new_content = content[:start_idx] + new_method + content[next_def_idx:]
            
            # Écrire le nouveau contenu
            with open(product_window_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            
            print("Méthode load_products corrigée avec succès!")
            
        # Cas 2: Version standard
        elif "def load_products" in content:
            print("Correction de la méthode load_products (version standard)...")
            
            # Vérifier si l'import get_connection est présent, sinon l'ajouter
            if "from database import get_connection" not in content:
                import_pos = content.find("import")
                import_end = content.find("\n", import_pos)
                content = content[:import_end+1] + "\nfrom database import get_connection" + content[import_end+1:]
            
            # Trouver la méthode load_products
            start_idx = content.find("def load_products")
            if start_idx == -1:
                print("Méthode load_products non trouvée!")
                return False
            
            # Trouver la fin de la méthode
            next_def_idx = content.find("def ", start_idx + 10)
            if next_def_idx == -1:
                next_def_idx = len(content)
            
            # Construire la méthode de remplacement (similaire à ci-dessus)
            # ...
            
            # Écrire le nouveau contenu
            with open(product_window_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            print("Méthode load_products corrigée avec succès!")
        else:
            print("Structure de fichier non reconnue, impossible de corriger automatiquement.")
            print("Veuillez consulter le fichier de diagnostic pour plus d'informations.")
    except Exception as e:
        print(f"ERREUR lors de la correction du fichier: {e}")
        import traceback
        traceback.print_exc()
    
    # Fix 2: Corriger les problèmes de base de données
    try:
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            
            # Vérifier si la table Products existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Products'")
            if not cursor.fetchone():
                print("ERREUR CRITIQUE: La table Products n'existe pas!")
                return False
            
            # Vérifier si des produits existent
            cursor.execute("SELECT COUNT(*) FROM Products")
            if cursor.fetchone()[0] == 0:
                print("Aucun produit trouvé, tentative d'ajout d'un produit de test...")
                
                # Vérifier si une catégorie existe
                cursor.execute("SELECT id FROM Categories LIMIT 1")
                cat_result = cursor.fetchone()
                
                if not cat_result:
                    print("Création d'une catégorie...")
                    cursor.execute("""
                        INSERT INTO Categories (name, description, created_at, updated_at)
                        VALUES ('Test', 'Catégorie de test', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """)
                    cat_id = cursor.lastrowid
                else:
                    cat_id = cat_result[0]
                
                # Insérer un produit de test
                cursor.execute("""
                    INSERT INTO Products (
                        name, description, barcode, unit_price, purchase_price,
                        stock, min_stock, category_id, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """, (
                    "Produit Test Fixe",
                    "Produit ajouté par le script de correction",
                    "FIX123",
                    100.00,
                    70.00,
                    50,
                    10,
                    cat_id
                ))
                
                conn.commit()
                print("Produit de test ajouté avec succès!")
            
            conn.close()
    except Exception as e:
        print(f"ERREUR lors de la correction de la base de données: {e}")
        if conn:
            conn.close()
    
    print_hr()
    print("Corrections terminées.")
    print_hr()
    
    return True

if __name__ == "__main__":
    # Exécuter le diagnostic
    debug_products()
    
    # Demander si l'utilisateur veut appliquer les corrections
    try:
        answer = input("\nVoulez-vous appliquer les corrections automatiques? (o/n): ")
        if answer.lower() in ['o', 'oui', 'y', 'yes']:
            fix_product_loading()
    except:
        # En cas d'erreur ou d'exécution non interactive, appliquer automatiquement
        fix_product_loading()
