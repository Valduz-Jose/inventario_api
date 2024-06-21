import sqlite3

def vaciar_tablas(db_file):
    try:
        # Conectar a la base de datos SQLite
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Obtener el nombre de todas las tablas en la base de datos
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        # Iterar sobre las tablas y vaciar cada una
        for table in tables:
            table_name = table[0]
            cursor.execute(f"DELETE FROM {table_name};")
            print(f"Se han eliminado todos los registros de la tabla '{table_name}'")

        # Confirmar los cambios y cerrar la conexión
        conn.commit()
        conn.close()

        print("Se han vaciado todas las tablas de la base de datos.")

    except sqlite3.Error as e:
        print(f"Error al vaciar las tablas de la base de datos: {e}")

# Ejemplo de uso
if __name__ == "__main__":
    db_file = 'test.db'
    vaciar_tablas(db_file)