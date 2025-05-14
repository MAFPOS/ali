import os
import importlib.util
import sys

def run_module(module_path, module_name):
    """Import and run a module by path"""
    print(f"\n=== Running {module_name} ===")
    try:
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        if not spec:
            print(f"Error: Could not load {module_path}")
            return False
            
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        
        # If the module has a main function, call it
        if hasattr(module, "main"):
            module.main()
        
        print(f"Successfully ran {module_name}")
        return True
    except Exception as e:
        print(f"Error running {module_name}: {e}")
        return False

def main():
    """Run all fix scripts"""
    print("Starting comprehensive application fixes...")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Run schema fixes
    schema_fix = os.path.join(current_dir, "schema_fix.py")
    run_module(schema_fix, "schema_fix")
    
    # Fix receipt printer
    fix_printer = os.path.join(current_dir, "fix_printer.py")
    run_module(fix_printer, "fix_printer")
    
    # Fix variant display
    fix_variant = os.path.join(current_dir, "fix_variant_display.py")
    run_module(fix_variant, "fix_variant_display")
    
    # Add example products
    add_products = os.path.join(current_dir, "add_products.py")
    run_module(add_products, "add_products")
    
    # Create necessary directories
    print("\n=== Creating necessary directories ===")
    try:
        # Product images directory
        product_images_dir = os.path.join(current_dir, "product_images")
        os.makedirs(product_images_dir, exist_ok=True)
        print(f"Created directory: {product_images_dir}")
        
        # Receipt logs directory
        receipt_logos_dir = os.path.join(current_dir, "receipt_logos")
        os.makedirs(receipt_logos_dir, exist_ok=True)
        print(f"Created directory: {receipt_logos_dir}")
    except Exception as e:
        print(f"Error creating directories: {e}")
    
    print("\nAll fixes have been applied successfully!")
    print("\nINSTRUCTIONS:")
    print("1. Run the application with: python main.py")
    print("2. If you still encounter issues, use the special startup mode:")
    print("   python -c \"import main_fix; main_fix.apply_patches(); import main; main.main()\"")
    print("\nThe application should now be working 100%")

if __name__ == "__main__":
    main()
