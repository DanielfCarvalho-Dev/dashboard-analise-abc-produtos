from sqlalchemy import create_engine

SERVER = "DOUGTATTOO\\SQLEXPRESS"
DATABASE = "EMPRESA_DB"

connection_string = (
    f"mssql+pyodbc://@{SERVER}/{DATABASE}?driver=ODBC+Driver+17+for+SQL+Server""&trusted_connection=yes"
)
engine = create_engine(connection_string)

def conectar_banco():
    return engine.connect()