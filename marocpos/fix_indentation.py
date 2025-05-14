import os
import sys

def fix_product_management_indentation():
    """Fix indentation issues in product_management_window.py"""
    print("Fixing indentation issues in product_management_window.py...")
    
    # Get the path to the product_management_window.py file
    ui_dir = os.path.join(os.path.dirname(__file__), "ui")
    product_mgmt_path = os.path.join(ui_dir, "product_management_window.py")
    
    if not os.path.exists(product_mgmt_path):
        print(f"ERROR: File not found: {product_mgmt_path}")
        return False
    
    # Create a backup of the original file
    backup_path = product_mgmt_path + ".backup"
    try:
        with open(product_mgmt_path, "r", encoding="utf-8") as f:
            original_content = f.read()
        
        # Save backup
        with open(backup_path, "w", encoding="utf-8") as f:
            f.write(original_content)
            
        print(f"Created backup at {backup_path}")
    except Exception as e:
        print(f"Error creating backup: {e}")
        return False
    
    # Check for the indentation error
    lines = original_content.split("\n")
    fixed_lines = []
    in_problem_method = False
    problem_found = False
    indentation_level = 0
    
    for i, line in enumerate(lines):
        # Keep track if we're in the load_products method
        if line.strip().startswith("def load_products"):
            in_problem_method = True
            indentation_level = line.find("def")
            
        # Check if this is where indentation error occurs (around line 116-117)
        if in_problem_method and i >= 115 and i <= 120 and line.strip().startswith("try:"):
            next_line = lines[i+1] if i+1 < len(lines) else ""
            if not next_line.strip():  # Empty line after try:
                problem_found = True
                # Fix by adding proper indentation
                fixed_lines.append(line)
                fixed_lines.append(" " * (indentation_level + 8) + "# Clear table")
                fixed_lines.append(" " * (indentation_level + 8) + "self.products_table.setRowCount(0)")
                
                # Skip the next line which is empty
                i += 1
                continue
        
        # Check for end of the method
        if in_problem_method and line.strip().startswith("def ") and i > 120:
            in_problem_method = False
        
        # Add the line to fixed content
        fixed_lines.append(line)
    
    # If we didn't find the specific problem, try a more general approach
    if not problem_found:
        print("Specific indentation issue not found, applying general fixes...")
        
        # Create completely new content with a working load_products method
        new_content = []
        skip_mode = False
        
        for i, line in enumerate(lines):
            # If we reach the load_products method, enter skip mode
            if line.strip().startswith("def load_products"):
                skip_mode = True
                indentation = line.find("def")
                
                # Add the method definition
                new_content.append(line)
                
                # Add a simplified but working method body
                new_content.append(" " * (indentation + 4) + "\"\"\"Load products from database\"\"\"")
                new_content.append(" " * (indentation + 4) + "try:")
                new_content.append(" " * (indentation + 8) + "# Clear table")
                new_content.append(" " * (indentation + 8) + "self.products_table.setRowCount(0)")
                new_content.append(" " * (indentation + 8))
                new_content.append(" " * (indentation + 8) + "# Get direct database connection")
                new_content.append(" " * (indentation + 8) + "from database import get_connection")
                new_content.append(" " * (indentation + 8) + "conn = get_connection()")
                new_content.append(" " * (indentation + 8) + "if conn:")
                new_content.append(" " * (indentation + 12) + "try:")
                new_content.append(" " * (indentation + 16) + "cursor = conn.cursor()")
                new_content.append(" " * (indentation + 16))
                new_content.append(" " * (indentation + 16) + "# Execute direct SQL query")
                new_content.append(" " * (indentation + 16) + "if category_id:")
                new_content.append(" " * (indentation + 20) + "cursor.execute(\"\"\"")
                new_content.append(" " * (indentation + 20) + "    SELECT p.*, c.name as category_name")
                new_content.append(" " * (indentation + 20) + "    FROM Products p")
                new_content.append(" " * (indentation + 20) + "    LEFT JOIN Categories c ON p.category_id = c.id")
                new_content.append(" " * (indentation + 20) + "    WHERE p.category_id = ?")
                new_content.append(" " * (indentation + 20) + "    ORDER BY p.name")
                new_content.append(" " * (indentation + 20) + "\"\"\", (category_id,))")
                new_content.append(" " * (indentation + 16) + "else:")
                new_content.append(" " * (indentation + 20) + "cursor.execute(\"\"\"")
                new_content.append(" " * (indentation + 20) + "    SELECT p.*, c.name as category_name")
                new_content.append(" " * (indentation + 20) + "    FROM Products p")
                new_content.append(" " * (indentation + 20) + "    LEFT JOIN Categories c ON p.category_id = c.id")
                new_content.append(" " * (indentation + 20) + "    ORDER BY p.name")
                new_content.append(" " * (indentation + 20) + "\"\"\")")
                new_content.append(" " * (indentation + 16))
                new_content.append(" " * (indentation + 16) + "# Convert to list of dictionaries")
                new_content.append(" " * (indentation + 16) + "columns = [column[0] for column in cursor.description]")
                new_content.append(" " * (indentation + 16) + "products = []")
                new_content.append(" " * (indentation + 16) + "for row in cursor.fetchall():")
                new_content.append(" " * (indentation + 20) + "product_dict = dict(zip(columns, row))")
                new_content.append(" " * (indentation + 20) + "products.append(product_dict)")
                new_content.append(" " * (indentation + 16))
                new_content.append(" " * (indentation + 16) + "print(f\"Found {len(products)} products\")")
                new_content.append(" " * (indentation + 12) + "except Exception as e:")
                new_content.append(" " * (indentation + 16) + "print(f\"Database error: {e}\")")
                new_content.append(" " * (indentation + 16) + "products = []")
                new_content.append(" " * (indentation + 12) + "finally:")
                new_content.append(" " * (indentation + 16) + "conn.close()")
                new_content.append(" " * (indentation + 8))
                new_content.append(" " * (indentation + 8) + "# Display products")
                new_content.append(" " * (indentation + 8) + "self.products_table.setRowCount(len(products))")
                new_content.append(" " * (indentation + 8))
                new_content.append(" " * (indentation + 8) + "for row, product_dict in enumerate(products):")
                new_content.append(" " * (indentation + 12) + "try:")
                
                # Continue with rest of the method...
                continue
                
            # If we're in skip mode, check for the next method definition
            if skip_mode and line.strip().startswith("def ") and "load_products" not in line:
                skip_mode = False
            
            # If not in skip mode, add the line
            if not skip_mode:
                new_content.append(line)
        
        # Use the new content
        fixed_lines = new_content
    
    # Write the fixed content back to the file
    with open(product_mgmt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(fixed_lines))
    
    print("Fixed indentation issues in product_management_window.py")
    return True

def fix_sales_schema():
    """Fix schema issues in Sales and SaleItems tables"""
    print("\nFixing Sales and SaleItems schema issues...")
    
    from database import get_connection
    
    conn = get_connection()
    if not conn:
        print("ERROR: Could not connect to database")
        return False
    
    try:
        cursor = conn.cursor()
        
        # Check Sales table structure
        cursor.execute("PRAGMA table_info(Sales)")
        columns = {col[1].lower(): col for col in cursor.fetchall()}
        
        # Fix 'date' vs 'created_at' issue
        date_column_exists = 'date' in columns
        created_at_exists = 'created_at' in columns
        
        if date_column_exists and not created_at_exists:
            print("Fixing 'date' column in Sales table...")
            
            # Create temporary table with correct structure
            cursor.execute("""
                CREATE TEMPORARY TABLE Sales_temp (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    total_amount REAL NOT NULL,
                    user_id INTEGER NOT NULL,
                    discount REAL DEFAULT 0,
                    tax_amount REAL DEFAULT 0,
                    final_total REAL NOT NULL,
                    payment_method TEXT DEFAULT 'CASH',
                    payment_status TEXT DEFAULT 'COMPLETED',
                    notes TEXT,
                    FOREIGN KEY (user_id) REFERENCES Users(id)
                )
            """)
            
            # Copy data from old table
            cursor.execute("""
                INSERT INTO Sales_temp (
                    id, created_at, total_amount, user_id, discount, 
                    tax_amount, final_total, payment_method, payment_status, notes
                )
                SELECT 
                    id, date, total_amount, user_id, 
                    COALESCE(discount, 0), 
                    COALESCE(tax_amount, 0),
                    COALESCE(final_total, total_amount),
                    COALESCE(payment_method, 'CASH'),
                    COALESCE(payment_status, 'COMPLETED'),
                    notes
                FROM Sales
            """)
            
            # Drop old table and rename new one
            cursor.execute("DROP TABLE Sales")
            cursor.execute("ALTER TABLE Sales_temp RENAME TO Sales")
            
            print("Sales table structure fixed")
        elif not date_column_exists and not created_at_exists:
            print("Sales table is missing both 'date' and 'created_at' columns. Creating table...")
            
            # If table exists but neither column exists, drop and recreate
            cursor.execute("DROP TABLE IF EXISTS Sales")
            cursor.execute("""
                CREATE TABLE Sales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    total_amount REAL NOT NULL,
                    user_id INTEGER NOT NULL,
                    discount REAL DEFAULT 0,
                    tax_amount REAL DEFAULT 0,
                    final_total REAL NOT NULL,
                    payment_method TEXT DEFAULT 'CASH',
                    payment_status TEXT DEFAULT 'COMPLETED',
                    notes TEXT,
                    FOREIGN KEY (user_id) REFERENCES Users(id)
                )
            """)
            print("Sales table recreated")
        
        # Check SaleItems table structure
        cursor.execute("PRAGMA table_info(SaleItems)")
        columns = {col[1].lower(): col for col in cursor.fetchall()}
        
        # Fix missing 'subtotal' column
        if 'subtotal' not in columns:
            print("Adding 'subtotal' column to SaleItems table...")
            
            # Add subtotal column
            cursor.execute("ALTER TABLE SaleItems ADD COLUMN subtotal REAL")
            
            # Set default values based on quantity * unit_price
            cursor.execute("""
                UPDATE SaleItems 
                SET subtotal = quantity * unit_price
                WHERE subtotal IS NULL
            """)
            
            print("SaleItems table structure fixed")
        
        # Make sure the Stores table has the right columns
        cursor.execute("PRAGMA table_info(Stores)")
        columns = {col[1].lower(): col for col in cursor.fetchall()}
        
        if 'location' in columns and 'address' not in columns:
            print("Fixing Stores table structure...")
            
            # Create temporary table with correct structure
            cursor.execute("""
                CREATE TEMPORARY TABLE Stores_temp (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    address TEXT,
                    phone TEXT,
                    email TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Copy data
            cursor.execute("""
                INSERT INTO Stores_temp (id, name, address, created_at)
                SELECT id, name, location, COALESCE(created_at, CURRENT_TIMESTAMP)
                FROM Stores
            """)
            
            # Drop old table and rename new one
            cursor.execute("DROP TABLE Stores")
            cursor.execute("ALTER TABLE Stores_temp RENAME TO Stores")
            
            print("Stores table structure fixed")
        
        conn.commit()
        print("Database schema fixes applied successfully")
        return True
    
    except Exception as e:
        print(f"Error fixing database schema: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def fix_printer_imports():
    """Fix QPrinter import issues"""
    print("\nFixing QPrinter import issues...")
    
    receipt_path = os.path.join(os.path.dirname(__file__), "ui", "receipt_generator.py")
    
    if not os.path.exists(receipt_path):
        print(f"Receipt generator file not found at {receipt_path}")
        receipt_dir = os.path.join(os.path.dirname(__file__), "ui")
        
        # Look for any file that might contain QPrinter imports
        import glob
        py_files = glob.glob(os.path.join(receipt_dir, "*.py"))
        
        qt_printer_files = []
        for file in py_files:
            try:
                with open(file, "r", encoding="utf-8") as f:
                    content = f.read()
                    if "QPrinter" in content:
                        qt_printer_files.append(file)
            except:
                pass
        
        if qt_printer_files:
            print(f"Found {len(qt_printer_files)} files with QPrinter references:")
            for file in qt_printer_files:
                print(f"  - {os.path.basename(file)}")
        else:
            print("No files with QPrinter references found.")
            return False
    
    # Try to fix receipt_generator.py if it exists
    if os.path.exists(receipt_path):
        try:
            with open(receipt_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Fix imports
            if "from PyQt5.QtGui import QPrinter" in content:
                content = content.replace(
                    "from PyQt5.QtGui import QPrinter",
                    "from PyQt5.QtPrintSupport import QPrinter"
                )
                print("Fixed QPrinter import")
            
            if "from PyQt5.QtGui import QPrinter, QPainter" in content:
                content = content.replace(
                    "from PyQt5.QtGui import QPrinter, QPainter",
                    "from PyQt5.QtPrintSupport import QPrinter\nfrom PyQt5.QtGui import QPainter"
                )
                print("Fixed QPrinter and QPainter imports")
            
            # Write fixed content
            with open(receipt_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            print("Fixed printer imports in receipt_generator.py")
            return True
        except Exception as e:
            print(f"Error fixing printer imports: {e}")
            return False
    
    # Try a more global approach if receipt_generator.py not found
    print("Searching for QPrinter imports in all UI files...")
    ui_dir = os.path.join(os.path.dirname(__file__), "ui")
    
    try:
        import glob
        py_files = glob.glob(os.path.join(ui_dir, "*.py"))
        
        fixed_files = 0
        for file_path in py_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                original_content = content
                
                # Fix imports
                if "from PyQt5.QtGui import QPrinter" in content:
                    content = content.replace(
                        "from PyQt5.QtGui import QPrinter",
                        "from PyQt5.QtPrintSupport import QPrinter"
                    )
                
                if "from PyQt5.QtGui import QPrinter, QPainter" in content:
                    content = content.replace(
                        "from PyQt5.QtGui import QPrinter, QPainter",
                        "from PyQt5.QtPrintSupport import QPrinter\nfrom PyQt5.QtGui import QPainter"
                    )
                
                # Save if changes were made
                if content != original_content:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"Fixed printer imports in {os.path.basename(file_path)}")
                    fixed_files += 1
            except:
                pass
        
        print(f"Fixed printer imports in {fixed_files} files")
        return fixed_files > 0
    except Exception as e:
        print(f"Error in global printer import fix: {e}")
        return False

def main():
    """Run all fixes"""
    print("=== COMPREHENSIVE FIXES FOR MAROCPOS ===")
    
    # Fix 1: Indentation in product_management_window.py
    fix_product_management_indentation()
    
    # Fix 2: Sales and SaleItems schema
    fix_sales_schema()
    
    # Fix 3: QPrinter imports
    fix_printer_imports()
    
    print("\n=== FIXES COMPLETED ===")
    print("\nInstructions:")
    print("1. Run the application: python main.py")
    print("2. If you still have issues with product display, run: python fix_database_loading.py")
    print("3. If you need test products, run: python add_products.py")
    print("4. For detailed diagnostics, run: python debug_products.py")
    
    return True

if __name__ == "__main__":
    main()
