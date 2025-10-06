import sqlite3

DATABASE_NAME = "app_database.db"

def get_provinces():
    """Retrieves a unique list of all provinces."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT province FROM thai_addresses ORDER BY province")
        provinces = cursor.fetchall()
        return [row[0] for row in provinces]

def get_districts(province):
    """Retrieves districts for a given province."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT district FROM thai_addresses WHERE province = ? ORDER BY district", (province,))
        districts = cursor.fetchall()
        return [row[0] for row in districts]

def get_sub_districts(province, district):
    """Retrieves sub-districts for a given province and district."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT sub_district FROM thai_addresses WHERE province = ? AND district = ? ORDER BY sub_district", (province, district))
        sub_districts = cursor.fetchall()
        return [row[0] for row in sub_districts]

def get_zipcode(province, district, sub_district):
    """Retrieves the zipcode for a given address combination."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT zipcode FROM thai_addresses WHERE province = ? AND district = ? AND sub_district = ? LIMIT 1", 
                       (province, district, sub_district))
        result = cursor.fetchone()
        return result[0] if result else ""

def get_addresses_by_zipcode(zipcode):
    """Retrieves all address records for a given zipcode."""
    with sqlite3.connect(DATABASE_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT province, district, sub_district FROM thai_addresses WHERE zipcode = ?", (zipcode,))
        addresses = cursor.fetchall()
        return [dict(row) for row in addresses]

