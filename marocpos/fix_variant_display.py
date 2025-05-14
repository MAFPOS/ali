from database import get_connection
import json

def fix_variant_attributes():
    print("Fixing variant attributes in database...")
    
    conn = get_connection()
    if not conn:
        print("Failed to connect to database")
        return False
    
    try:
        cursor = conn.cursor()
        
        # Get all products with variants
        cursor.execute("""
            SELECT id, variant_attributes, has_variants 
            FROM Products 
            WHERE has_variants = 1
        """)
        
        variant_products = cursor.fetchall()
        print(f"Found {len(variant_products)} products with variants")
        
        for product in variant_products:
            product_id = product[0]
            attrs = product[1]
            
            # Fix incorrect variant_attributes formats
            if attrs:
                fixed_attrs = None
                try:
                    # Try to parse as JSON
                    if isinstance(attrs, str):
                        parsed = json.loads(attrs)
                        # Convert to list if it's a dict
                        if isinstance(parsed, dict):
                            fixed_attrs = json.dumps(list(parsed.keys()))
                        # Use as is if it's already a list
                        elif isinstance(parsed, list):
                            fixed_attrs = attrs
                        else:
                            fixed_attrs = '[]'
                    else:
                        fixed_attrs = '[]'
                except:
                    fixed_attrs = '[]'
                
                # Update the product
                if fixed_attrs != attrs:
                    cursor.execute("""
                        UPDATE Products
                        SET variant_attributes = ?
                        WHERE id = ?
                    """, (fixed_attrs, product_id))
                    print(f"Fixed variant attributes for product {product_id}")
        
        # Fix variant attribute values
        cursor.execute("SELECT id, attribute_values FROM ProductVariants")
        variants = cursor.fetchall()
        
        for variant in variants:
            variant_id = variant[0]
            attr_values = variant[1]
            
            if attr_values:
                try:
                    # Try to parse as JSON to verify it's valid
                    if isinstance(attr_values, str):
                        json.loads(attr_values)
                    else:
                        # If not a string, convert to proper JSON
                        fixed_values = json.dumps({})
                        cursor.execute("""
                            UPDATE ProductVariants
                            SET attribute_values = ?
                            WHERE id = ?
                        """, (fixed_values, variant_id))
                        print(f"Fixed attribute values for variant {variant_id}")
                except:
                    # If it's invalid JSON, reset it
                    cursor.execute("""
                        UPDATE ProductVariants
                        SET attribute_values = '{}'
                        WHERE id = ?
                    """, (variant_id,))
                    print(f"Reset invalid attribute values for variant {variant_id}")
        
        conn.commit()
        print("Variant attributes fixed successfully")
        return True
        
    except Exception as e:
        print(f"Error fixing variant attributes: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    fix_variant_attributes()
