import streamlit as st
import pandas as pd
from sqlalchemy import bindparam, create_engine, text
import os
from dotenv import load_dotenv

def load_environment():
    """Load environment variables from config.env"""
    load_dotenv('config.env')

@st.cache_resource
def get_db_connection():
    """Establish and return a database connection"""
    try:
        db_user = os.getenv('DB_USER')
        db_password = os.getenv('DB_PASSWORD')
        db_host = os.getenv('DB_HOST')
        db_port = os.getenv('DB_PORT')
        db_name = os.getenv('DB_NAME')
        
        if not all([db_user, db_password, db_host, db_port, db_name]):
            raise ValueError("One or more required environment variables are missing or empty.")
        
        conn_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        
        engine = create_engine(
            conn_string,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            pool_pre_ping=True
        )
        
        return engine  
    except Exception as e:
        st.error(f"Database connection error: {str(e)}")
        return None  

@st.cache_data
def fetch_data(_engine, query, column_name=None, params=None):
    """Fetch data from the database"""
    try:
        df = pd.read_sql(query, _engine, params=params)
        if column_name:
            return df[column_name].tolist()
        return df
    except Exception as e:
        st.error(f"Error executing query: {str(e)}")
        return [] if column_name else pd.DataFrame()


@st.cache_data
def fetch_sub_fields_for_subject_areas(_engine, subject_areas):
    """Fetch distinct sub-fields for one or more subject areas."""
    if not subject_areas:
        return pd.DataFrame()

    try:
        query = text("""
            SELECT DISTINCT ON ("sub_field") "sub_field", "id"
            FROM raw."subject_mapping"
            WHERE "subject_area" IN :areas
            ORDER BY "sub_field", "id"
        """).bindparams(bindparam("areas", expanding=True))
        return pd.read_sql(query, _engine, params={"areas": list(subject_areas)})
    except Exception as e:
        st.error(f"Error executing query: {str(e)}")
        return pd.DataFrame()
