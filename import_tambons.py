import sqlite3
import re

DATABASE_NAME = "app_database.db"
SQL_FILE_PATH = "tambons.sql"

def create_table(cursor):
    """Creates the thai_addresses table."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS thai_addresses (
            id INTEGER PRIMARY KEY,
            sub_district TEXT NOT NULL,
            district TEXT NOT NULL,
            province TEXT NOT NULL,
            zipcode TEXT NOT NULL,
            sub_district_code TEXT,
            district_code TEXT,
            province_code TEXT
        )
    """)
    print("Table 'thai_addresses' created or already exists.")

def import_data():
    """Parses the tambons.sql file and inserts data into the SQLite database."""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    create_table(cursor)

    print(f"Reading data from {SQL_FILE_PATH}...")
    try:
        with open(SQL_FILE_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"ERROR: The file {SQL_FILE_PATH} was not found in the project directory.")
        print("Please make sure you have saved the SQL file with that name.")
        return

    # Use regex to find all INSERT statements and their values
    # This is more robust than splitting by lines
    insert_regex = re.compile(r"INSERT INTO `tambons` .*? VALUES\s*(.*?);", re.DOTALL)
    values_regex = re.compile(r"\((.*?)\)")

    total_inserted = 0
    matches = insert_regex.findall(content)

    if not matches:
        print("No INSERT statements found in the SQL file. Nothing to import.")
        conn.close()
        return

    print(f"Found {len(matches)} INSERT blocks. Processing...")

    for values_block in matches:
        value_tuples = values_regex.findall(values_block)
        for value_tuple_str in value_tuples:
            try:
                # Split and clean up values
                values = [v.strip().strip("'" ) for v in value_tuple_str.split(',')]
                # The SQL file has 8 columns, we map them to our table
                if len(values) == 8:
                    cursor.execute("""
                        INSERT INTO thai_addresses (id, sub_district, district, province, zipcode, sub_district_code, district_code, province_code)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, tuple(values))
                    total_inserted += 1
            except sqlite3.IntegrityError:
                # This will catch errors if we try to insert a duplicate primary key (id)
                # We can safely ignore them if we run the script multiple times
                pass
            except Exception as e:
                print(f"Skipping a row due to error: {e} -> {value_tuple_str}")

    conn.commit()
    conn.close()

    print("\n--- Import Complete ---")
    print(f"Successfully inserted {total_inserted} records into the 'thai_addresses' table.")
    print("You can now delete the import_tambons.py and tambons.sql files if you wish.")

if __name__ == "__main__":
    import_data()
