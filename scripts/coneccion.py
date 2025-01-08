import psycopg2

# Configuración de conexión
DB_CONFIG = {
    'dbname': 'gestion_contratistas',
    'user': 'innovacionkennedy',
    'password': 'agile2024.',
    'host': 'localhost',  # Cambiar a '192.168.0.24' si es necesario
    'port': '5432'
}

try:
    # Intentar conexión
    conn = psycopg2.connect(**DB_CONFIG)
    print("Conexión exitosa a la base de datos")
    conn.close()
except Exception as e:
    print(f"Error al conectar: {e}")
