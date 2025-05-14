from database import get_connection
import os

def fix_receipt_module():
    print("Fixing receipt generator module...")
    
    # Path to the receipt generator file
    receipt_path = os.path.join(os.path.dirname(__file__), "ui", "receipt_generator.py")
    
    if not os.path.exists(receipt_path):
        print(f"Error: Receipt file not found at {receipt_path}")
        return False
    
    try:
        # Read file content
        with open(receipt_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Fix the imports
        if "from PyQt5.QtGui import QPrinter" in content:
            # Replace the import
            content = content.replace(
                "from PyQt5.QtGui import QPrinter", 
                "from PyQt5.QtPrintSupport import QPrinter"
            )
            print("Fixed QPrinter import in receipt_generator.py")
        
        if "from PyQt5.QtGui import QPrinter, QPainter" in content:
            # Replace the import
            content = content.replace(
                "from PyQt5.QtGui import QPrinter, QPainter", 
                "from PyQt5.QtPrintSupport import QPrinter\nfrom PyQt5.QtGui import QPainter"
            )
            print("Fixed QPrinter and QPainter imports in receipt_generator.py")
            
        if "from PyQt5.QtPrintSupport import QPrintDialog" not in content:
            # Add missing import
            if "from PyQt5.QtPrintSupport import QPrinter" in content:
                content = content.replace(
                    "from PyQt5.QtPrintSupport import QPrinter",
                    "from PyQt5.QtPrintSupport import QPrinter, QPrintDialog"
                )
            else:
                # Add the import line after last import
                import_pos = content.rfind("import ")
                import_line_end = content.find("\n", import_pos)
                content = content[:import_line_end+1] + "\nfrom PyQt5.QtPrintSupport import QPrinter, QPrintDialog" + content[import_line_end+1:]
            
            print("Added QPrintDialog import in receipt_generator.py")
        
        # Write updated content back to file
        with open(receipt_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        print("Receipt generator module fixed successfully")
        return True
        
    except Exception as e:
        print(f"Error fixing receipt module: {e}")
        return False

if __name__ == "__main__":
    fix_receipt_module()
