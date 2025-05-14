from database import get_connection
import os

def fix_database_schema():
    """Fix potential database schema issues and ensure consistency"""
    print("Starting database schema check and repair...")
    
    conn = get_connection()
    if not conn:
        print("Failed to connect to database")
        return False
    
    try:
        cursor = conn.cursor()
        
        # Check Sales table structure
        print("Checking Sales table structure...")
        cursor.execute("PRAGMA table_info(Sales)")
        columns = {col[1].lower(): col for col in cursor.fetchall()}
        
        # Check for 'date' column vs 'created_at'
        if 'date' in columns and 'created_at' not in columns:
            print("Found 'date' column but no 'created_at' column in Sales table. Fixing...")
            
            # Create a new temporary table with correct structure
            cursor.execute("""
                CREATE TEMPORARY TABLE Sales_temp (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    total_amount REAL NOT NULL,
                    discount REAL DEFAULT 0,
                    tax_amount REAL DEFAULT 0,
                    final_total REAL NOT NULL,
                    payment_method TEXT DEFAULT 'CASH',
                    payment_status TEXT DEFAULT 'COMPLETED',
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES Users(id)
                )
            """)
            
            # Copy data, mapping 'date' to 'created_at'
            cursor.execute("""
                INSERT INTO Sales_temp (
                    id, user_id, total_amount, discount, tax_amount, 
                    final_total, payment_method, payment_status, notes, created_at
                )
                SELECT 
                    id, user_id, total_amount, 
                    COALESCE(discount, 0) as discount, 
                    COALESCE(tax_amount, 0) as tax_amount,
                    COALESCE(total_amount, 0) as final_total,
                    COALESCE(payment_method, 'CASH') as payment_method,
                    COALESCE(payment_status, 'COMPLETED') as payment_status,
                    notes, date
                FROM Sales
            """)
            
            # Drop old table and rename new one
            cursor.execute("DROP TABLE Sales")
            cursor.execute("ALTER TABLE Sales_temp RENAME TO Sales")
            print("Sales table structure fixed")
        
        # Check SaleItems table structure
        print("Checking SaleItems table structure...")
        cursor.execute("PRAGMA table_info(SaleItems)")
        columns = {col[1].lower(): col for col in cursor.fetchall()}
        
        # Check for missing 'subtotal' column
        if 'subtotal' not in columns:
            print("Missing 'subtotal' column in SaleItems table. Adding it...")
            
            # Add subtotal column
            cursor.execute("ALTER TABLE SaleItems ADD COLUMN subtotal REAL")
            
            # Update existing records to have calculated subtotal
            cursor.execute("""
                UPDATE SaleItems 
                SET subtotal = quantity * unit_price
                WHERE subtotal IS NULL
            """)
            print("SaleItems table structure fixed")
        
        # Check if Stores table has address instead of location
        print("Checking Stores table structure...")
        cursor.execute("PRAGMA table_info(Stores)")
        columns = {col[1].lower(): col for col in cursor.fetchall()}
        
        if 'location' in columns and 'address' not in columns:
            print("Found 'location' column but no 'address' column in Stores table. Fixing...")
            
            # Create a new temporary table with correct structure
            cursor.execute("""
                CREATE TEMPORARY TABLE Stores_temp (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    address TEXT,
                    phone TEXT,
                    email TEXT,
                    active INTEGER NOT NULL DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Copy data, mapping 'location' to 'address'
            cursor.execute("""
                INSERT INTO Stores_temp (
                    id, name, address, active, created_at
                )
                SELECT 
                    id, name, location, 
                    COALESCE(active, 1) as active,
                    COALESCE(created_at, CURRENT_TIMESTAMP) as created_at
                FROM Stores
            """)
            
            # Drop old table and rename new one
            cursor.execute("DROP TABLE Stores")
            cursor.execute("ALTER TABLE Stores_temp RENAME TO Stores")
            print("Stores table structure fixed")
            
        # Create product_images directory if it doesn't exist
        images_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "product_images")
        if not os.path.exists(images_dir):
            os.makedirs(images_dir)
            print(f"Created product images directory: {images_dir}")
            
        # Commit all changes
        conn.commit()
        print("Database schema check and repair completed successfully")
        return True
        
    except Exception as e:
        print(f"Error fixing database schema: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    fix_database_schema()
