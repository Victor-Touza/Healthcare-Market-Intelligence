# ============================================================
#  DATA TRANSFER PROGRAM: DATABASE_MANAGEMENT.PY
# ============================================================

import pandas as pd
from sqlalchemy import create_engine, text
import sys

# ============================================================
# 1. Connect to PostgreSQL
# ============================================================

user = 'XXXXXX'
password = 'XXXXX'
host = 'localhost'
port = 'XXXX'
database = 'TFM_Healthcare_Products'

engine = create_engine(
    f'postgresql://{user}:{password}@{host}:{port}/{database}'
)

# ============================================================
# 2. Create tables if they do not exist
# ============================================================

def create_tables():
    with engine.begin() as conn:

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS countries (
                id_country SERIAL PRIMARY KEY,
                country_code VARCHAR(100) UNIQUE,
                country VARCHAR(100)
            );
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS products (
                id_product SERIAL PRIMARY KEY,
                product_code VARCHAR(150) UNIQUE,
                product_name VARCHAR(150)
            );
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS results (
                id_result SERIAL PRIMARY KEY,
                id_country INTEGER REFERENCES countries(id_country),
                id_product INTEGER REFERENCES products(id_product),
                country VARCHAR(150),
                country_code VARCHAR(150),
                product_name VARCHAR(150),
                product_code VARCHAR(150),
                year INTEGER,
                annual_sales_index FLOAT,
                global_sales_index FLOAT,
                UNIQUE (id_country, id_product, year)
            );
        """))

        conn.execute(text("""
                CREATE TABLE IF NOT EXISTS sales_forecast (
                id_forecast SERIAL PRIMARY KEY,
                id_country INTEGER REFERENCES countries(id_country),
                id_product INTEGER REFERENCES products(id_product),
                year INTEGER,
                predicted_sales_index FLOAT,
                UNIQUE (id_country, id_product, year)
            );
        """))

        # NEW METRICS TABLE
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS predictive_model_metrics (
                id_metric SERIAL PRIMARY KEY,
                id_country INTEGER REFERENCES countries(id_country),
                id_product INTEGER REFERENCES products(id_product),
                mae FLOAT,
                rmse FLOAT,
                UNIQUE (id_country, id_product)
            );
        """))

# ============================================================
# 3. Insert dimensions
# ============================================================

def insert_dimensions(df_countries_py, df_products_py):

    with engine.begin() as conn:

        for _, row in df_countries_py.iterrows():
            conn.execute(text("""
                INSERT INTO countries (country_code, country)
                VALUES (:code, :name)
                ON CONFLICT (country_code) DO NOTHING;
            """), {"code": row["Country_Code"], "name": row["Country"]})

        for _, row in df_products_py.iterrows():
            conn.execute(text("""
                INSERT INTO products (product_code, product_name)
                VALUES (:code, :name)
                ON CONFLICT (product_code) DO NOTHING;
            """), {"code": row["Product_Code"], "name": row["Product_Name"]})

# ============================================================
# 4. Insert historical results
# ============================================================

def insert_results(df_analysis_py):

    with engine.connect() as conn:
        df_countries_sql = pd.read_sql("SELECT id_country, country_code FROM countries", conn)
        df_products_sql = pd.read_sql("SELECT id_product, product_name FROM products", conn)

    dict_countries = dict(zip(df_countries_sql["country_code"], df_countries_sql["id_country"]))
    dict_products = dict(zip(df_products_sql["product_name"], df_products_sql["id_product"]))

    with engine.begin() as conn:
        for _, row in df_analysis_py.iterrows():

            id_country = dict_countries.get(row["Country_Code"])
            id_product = dict_products.get(row["Product_Name"])

            if id_country is None or id_product is None:
                continue

            conn.execute(text("""
                INSERT INTO results (
                    id_country, id_product, country, country_code,
                    product_name, product_code, year,
                    annual_sales_index, global_sales_index
                )
                VALUES (
                    :id_country, :id_product, :country, :country_code,
                    :product_name, :product_code, :year,
                    :annual_index, :global_index
                )
                ON CONFLICT (id_country, id_product, year)
                DO UPDATE SET
                    annual_sales_index = EXCLUDED.annual_sales_index,
                    global_sales_index = EXCLUDED.global_sales_index
            """), {
                "id_country": id_country,
                "id_product": id_product,
                "country": row["Country"],
                "country_code": row["Country_Code"],
                "product_name": row["Product_Name"],
                "product_code": row["Product_Code"],
                "year": int(row["Year"]),
                "annual_index": float(row["Annual_Sales_Index"]),
                "global_index": float(row["Global_Sales_Index"])
            })

# ============================================================
# 5. Insert sales forecasts
# ============================================================

def insert_sales_forecast(df_forecast_py):

    with engine.connect() as conn:
        df_countries_sql = pd.read_sql("SELECT id_country, country FROM countries", conn)
        df_products_sql = pd.read_sql("SELECT id_product, product_name FROM products", conn)

    dict_countries = dict(zip(df_countries_sql["country"], df_countries_sql["id_country"]))
    dict_products = dict(zip(df_products_sql["product_name"], df_products_sql["id_product"]))

    with engine.begin() as conn:
        for _, row in df_forecast_py.iterrows():

            id_country = dict_countries.get(row["Country"])
            id_product = dict_products.get(row["Product_Name"])

            if id_country is None or id_product is None:
                continue

            conn.execute(text("""
                INSERT INTO sales_forecast (
                    id_country, id_product, year, predicted_sales_index
                )
                VALUES (:id_country, :id_product, :year, :predicted_sales_index)
                ON CONFLICT (id_country, id_product, year)
                DO UPDATE SET predicted_sales_index = EXCLUDED.predicted_sales_index
            """), {
                "id_country": id_country,
                "id_product": id_product,
                "year": int(row["Year"]),
                "predicted_sales_index": float(row["Predicted_Sales_Index"])
            })

# ============================================================
# 6. # Insert predictive model metrics
# ============================================================

def insert_metrics(df_metrics_py):

    with engine.connect() as conn:
        df_countries_sql = pd.read_sql("SELECT id_country, country FROM countries", conn)
        df_products_sql = pd.read_sql("SELECT id_product, product_name FROM products", conn)

    dict_countries = dict(zip(df_countries_sql["country"], df_countries_sql["id_country"]))
    dict_products = dict(zip(df_products_sql["product_name"], df_products_sql["id_product"]))

    with engine.begin() as conn:
        for _, row in df_metrics_py.iterrows():

            id_country = dict_countries.get(row["Country"])
            id_product = dict_products.get(row["Product_Name"])

            if id_country is None or id_product is None:
                continue

            conn.execute(text("""
                INSERT INTO predictive_model_metrics (
                    id_country, id_product, mae, rmse
                )
                VALUES (:id_country, :id_product, :mae, :rmse)
                ON CONFLICT (id_country, id_product)
                DO UPDATE SET
                    mae = EXCLUDED.mae,
                    rmse = EXCLUDED.rmse
            """), {
                "id_country": id_country,
                "id_product": id_product,
                "mae": row["MAE"],
                "rmse": row["RMSE"]
            })

# ============================================================
# 7. Main export
# ============================================================

def export_to_postgres(df_analysis_py, df_products_py, df_forecast_py, df_metrics_py):

    create_tables()
    insert_dimensions(df_analysis_py[["Country","Country_Code"]].drop_duplicates(), df_products_py)
    insert_results(df_analysis_py)
    insert_sales_forecast(df_forecast_py)
    insert_metrics(df_metrics_py)

    print("Completed export with metrics.")

# ============================================================
# 8. Execute
# ============================================================

if __name__ == "__main__":

    sys.path.append("C:/TFM/Programs")
    import importlib
    import sales_model as pv
    importlib.reload(pv)

    export_to_postgres(
        pv.df_analysis,
        pv.df_devices,
        pv.df_forecast,
        pv.df_metrics
    )