from PyQt5.QtWidgets import QApplication
import sys
import traceback

def install_error_handlers():
    """Install global error handlers to help with debugging"""
    # Keep reference to original hook
    original_hook = sys.excepthook
    
    def exception_hook(exctype, value, tb):
        """Global exception handler for uncaught exceptions"""
        # Log to console
        print(f"UNCAUGHT EXCEPTION: {exctype.__name__}: {value}")
        
        # Log to file with traceback
        try:
            with open("error_log.txt", "a") as f:
                from datetime import datetime
                f.write(f"\n\n--- {datetime.now()} ---\n")
                f.write(f"UNCAUGHT EXCEPTION: {exctype.__name__}: {value}\n")
                traceback.print_tb(tb, file=f)
                f.write("\n")
        except:
            pass
            
        # Display crash info and continue original hook
        original_hook(exctype, value, tb)
    
    # Install the exception hook
    sys.excepthook = exception_hook
    
    # Also patch Qt's error handler
    def qt_message_handler(mode, context, message):
        if mode > 1:  # Only log warnings and above
            print(f"Qt Message ({mode}): {message}")
            try:
                with open("qt_errors.log", "a") as f:
                    from datetime import datetime
                    f.write(f"{datetime.now()}: [{mode}] {message}\n")
            except:
                pass
    
    try:
        from PyQt5.QtCore import qInstallMessageHandler
        qInstallMessageHandler(qt_message_handler)
    except:
        print("Could not install Qt message handler")

def fix_startup_issues():
    """Fix common startup issues"""
    # Fix database schema
    from schema_fix import fix_database_schema
    fix_database_schema()
    
    # Create necessary directories
    import os
    
    # Product images directory
    images_dir = os.path.join(os.path.dirname(__file__), "product_images")
    os.makedirs(images_dir, exist_ok=True)
    
    # Receipt logos directory
    logos_dir = os.path.join(os.path.dirname(__file__), "receipt_logos")
    os.makedirs(logos_dir, exist_ok=True)
    
    # Make sure log file exists and is writable
    try:
        with open("error_log.txt", "a") as f:
            from datetime import datetime
            f.write(f"\n--- Application started at {datetime.now()} ---\n")
    except:
        print("Warning: Could not write to error log file")

def patch_main():
    """Patch the main application entry point"""
    from main import main as original_main
    
    def patched_main():
        """Patched main function with additional error handling and fixes"""
        print("Starting application with enhanced error handling...")
        
        # Install error handlers
        install_error_handlers()
        
        # Fix common startup issues
        fix_startup_issues()
        
        # Run original main with exception handling
        try:
            original_main()
        except Exception as e:
            print(f"Critical error in main function: {e}")
            traceback.print_exc()
            
            # Try to show error message to user
            try:
                from PyQt5.QtWidgets import QMessageBox
                app = QApplication.instance() or QApplication(sys.argv)
                QMessageBox.critical(
                    None,
                    "Erreur critique",
                    f"Une erreur critique s'est produite: {str(e)}\n\n"
                    f"Consultez le fichier error_log.txt pour plus de détails."
                )
            except:
                pass
    
    return patched_main

# Monkey-patch the main module's main function
def apply_patches():
    """Apply all patches to the main application"""
    import main
    main.main = patch_main()
    print("Applied patches to main application")

# This will be imported by the main application
if __name__ == "__main__":
    # Can be run directly to apply fixes
    print("Running standalone fixes...")
    fix_startup_issues()
    print("Fixes applied successfully")
