from database import get_connection
import os

def add_example_products():
    print("Adding example products...")
    
    conn = get_connection()
    if not conn:
        print("Failed to connect to database")
        return False
    
    try:
        cursor = conn.cursor()
        
        # Create example categories if they don't exist
        categories = [
            ("Électronique", "Produits électroniques et gadgets"),
            ("Alimentation", "Produits alimentaires"),
            ("Vêtements", "Vêtements et accessoires"),
            ("Papeterie", "Fournitures de bureau")
        ]
        
        cat_ids = {}
        for cat_name, cat_desc in categories:
            cursor.execute("SELECT id FROM Categories WHERE name = ?", (cat_name,))
            result = cursor.fetchone()
            
            if result:
                cat_ids[cat_name] = result[0]
            else:
                cursor.execute("""
                    INSERT INTO Categories (name, description, created_at, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """, (cat_name, cat_desc))
                cat_ids[cat_name] = cursor.lastrowid
                print(f"Created category: {cat_name}")
        
        # Example products
        products = [
            # (name, description, unit_price, purchase_price, stock, min_stock, category)
            ("Smartphone X", "Smartphone haut de gamme", 4999.99, 3500.00, 20, 5, "Électronique"),
            ("Tablette Pro", "Tablette professionnelle", 3599.99, 2400.00, 15, 3, "Électronique"),
            ("Écouteurs sans fil", "Écouteurs Bluetooth", 599.99, 350.00, 30, 10, "Électronique"),
            ("Chocolat noir", "Tablette de chocolat noir 100g", 15.99, 8.50, 50, 20, "Alimentation"),
            ("Eau minérale", "Bouteille d'eau 1.5L", 5.99, 3.00, 100, 40, "Alimentation"),
            ("T-shirt coton", "T-shirt en coton", 99.99, 45.00, 40, 10, "Vêtements"),
            ("Chemise", "Chemise formelle", 199.99, 90.00, 25, 5, "Vêtements"),
            ("Cahier", "Cahier 100 pages", 12.99, 5.00, 200, 50, "Papeterie"),
            ("Stylo", "Stylo à bille", 3.99, 1.50, 300, 100, "Papeterie")
        ]
        
        # Add products
        for name, desc, unit_price, purchase_price, stock, min_stock, category in products:
            # Check if product already exists
            cursor.execute("SELECT id FROM Products WHERE name = ?", (name,))
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO Products (
                        name, description, unit_price, purchase_price,
                        stock, min_stock, category_id, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """, (
                    name, desc, unit_price, purchase_price,
                    stock, min_stock, cat_ids[category]
                ))
                print(f"Added product: {name}")
        
        conn.commit()
        print("Example products added successfully")
        return True
        
    except Exception as e:
        print(f"Error adding example products: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    add_example_products()
