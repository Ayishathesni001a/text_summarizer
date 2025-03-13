import psycopg2

def connect_db():
    return psycopg2.connect(
        dbname="voice_to_text",   # Your database name
        user="postgres",          # Your PostgreSQL username
        password="123456789", # Your PostgreSQL password
        host="localhost",
        port="5432"
    )
