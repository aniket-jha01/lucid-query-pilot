import os
import uuid # For generating UUIDs for IDs
from datetime import datetime # For timestamping creation/update
from typing import List, Dict, Any
import json
import time
import re

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, String, DateTime, text
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy.dialects.postgresql import UUID as PG_UUID # Use this if considering PostgreSQL later, otherwise just String for UUID
from sqlalchemy.types import JSON # For storing JSON content directly
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from dotenv import load_dotenv
import google.generativeai as genai
from schema_parser import parse_json_schema, parse_excel_schema, parse_csv_schema, parse_sql_ddl_schema, parse_text_schema_with_llm
from pydantic import BaseModel
import pandas as pd
import sqlparse
import io

# Load environment variables from .env file
load_dotenv()

# Configure Google Gemini API (ensure GOOGLE_API_KEY is in your .env file)
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in .env file. Please set it.")
genai.configure(api_key=GEMINI_API_KEY)

app = FastAPI(
    title="QueryAgent Backend",
    description="Backend for Natural Language to SQL generation and data analysis using Agentic AI.",
    version="0.1.0"
)

# --- CORS Middleware ---
# Configure CORS to allow your React frontend to communicate with this backend
# In a production environment, restrict origins to your specific frontend URL(s)
origins = [
    "http://localhost:3000",
    "http://192.168.1.2:8080",
    "http://192.168.1.2:8082",
    "http://192.168.1.5:8080",
    "https://lucid-query-pilot.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Database Setup (PostgreSQL for production, SQLite fallback for dev) ---
POSTGRES_URL = os.getenv("POSTGRES_URL")
if POSTGRES_URL and POSTGRES_URL.strip():  # Only use if not empty
    DATABASE_URL = POSTGRES_URL
else:
    DATABASE_URL = "sqlite:///./queryagent.db"
    print("Using SQLite database for development/testing")

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()

# ORM Model: Schema
class Schema(Base):
    __tablename__ = "schemas"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    file_type = Column(String, nullable=False)
    status = Column(String, nullable=False, default="PROCESSING")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to SchemaStructure
    structures = relationship("SchemaStructure", back_populates="schema")

# ORM Model: SchemaStructure
class SchemaStructure(Base):
    __tablename__ = "schema_structures"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    schema_id = Column(String(36), ForeignKey("schemas.id"), nullable=False)
    content = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to Schema
    schema = relationship("Schema", back_populates="structures")

# --- SQLAlchemy Model: DatabaseConnection ---
class DatabaseConnection(Base):
    __tablename__ = "database_connections"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, nullable=False)
    connection_string = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# --- Pydantic Model: ConnectionCreate ---
class ConnectionCreate(BaseModel):
    name: str
    connection_string: str

# --- Pydantic Model: ConnectionResponse ---
class ConnectionResponse(BaseModel):
    id: str
    name: str
    created_at: datetime

# Create all tables in the database
Base.metadata.create_all(bind=engine)

# Dependency for getting DB session in FastAPI endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- Root Endpoint ---
@app.get("/")
async def read_root():
    return {"message": "Welcome to the QueryAgent Backend! Backend is running."}

# --- Schema Upload Endpoint (To be implemented fully) ---
# Remove the duplicate upload_schema endpoint (the one with status_code=status.HTTP_202_ACCEPTED)

# --- Other API Endpoints (To be implemented later) ---
# /api/query/generate-sql
# /api/query/execute
# /api/query/analyze

# --- SQL Generation Request Model ---
class SQLGenerationRequest(BaseModel):
    natural_language_query: str
    schema_id: str

def format_schema_for_prompt(schema):
    lines = []
    for table in schema.get("tables", []):
        col_str = ", ".join(col["name"] for col in table["columns"])
        lines.append(f"Table: {table['name']} ({col_str})")
    return "\n".join(lines)

def format_schema_for_prompt_json(schema):
    return json.dumps(schema, indent=2)

def extract_identifiers_from_sql(sql):
    # Simple regex to extract table and column names (not perfect, but works for most cases)
    tables = set(re.findall(r'from\s+([a-zA-Z0-9_]+)', sql, re.IGNORECASE))
    tables.update(re.findall(r'join\s+([a-zA-Z0-9_]+)', sql, re.IGNORECASE))
    columns = set(re.findall(r'select\s+(.*?)\s+from', sql, re.IGNORECASE))
    # Flatten columns
    if columns:
        columns = set([c.strip().split(' as ')[0].split(',')[0] for c in ','.join(columns).split(',')])
    return tables, columns

def schema_tables_and_columns(schema):
    table_names = set()
    column_names = set()
    for table in schema.get("tables", []):
        table_names.add(table["name"])
        for col in table["columns"]:
            column_names.add(col["name"])
    return table_names, column_names

@app.post("/api/query/generate-sql")
async def generate_sql(
    request: SQLGenerationRequest,
    db: Session = Depends(get_db)
):
    # Retrieve schema structure by schema_id
    schema_structure = db.query(SchemaStructure).filter(SchemaStructure.schema_id == request.schema_id).first()
    if not schema_structure:
        raise HTTPException(status_code=404, detail="Schema not found for the provided schema_id.")
    # Load schema from the 'schema' key in content
    schema_content = schema_structure.content.get("schema")
    if not schema_content:
        raise HTTPException(status_code=404, detail="Schema content not found for the provided schema_id.")
    schema_lines = format_schema_for_prompt(schema_content)
    # Universal, optimized prompt
    prompt = (
        "You are an expert SQL query generator. Given the following database schema and a natural language question, "
        "write a syntactically correct SQL query that answers the question.\n"
        "IMPORTANT:\n"
        "- Only use the tables and columns listed below. Do NOT guess or invent table or column names.\n"
        "- Use the exact names and case as shown.\n"
        "- If the question asks for a column or table not present, return a SQL query that returns no rows (e.g., SELECT * FROM employees WHERE 1=0;).\n"
        "- If the question is ambiguous, use only the available columns.\n"
        "The database schema is as follows:\n"
        f"{schema_lines}\n\n"
        "Examples:\n"
        "Q: Who are the employees?\n"
        "A: SELECT name FROM employees;\n"
        "Q: What is the salary of each employee?\n"
        "A: SELECT name, salary FROM employees;\n"
        "Q: What is the first name of each employee? (Column does not exist)\n"
        "A: SELECT * FROM employees WHERE 1=0;\n"
        "\n"
        f"Question: {request.natural_language_query}\n\n"
        "SQL:"
    )
    try:
        llm_model = genai.GenerativeModel("gemini-1.5-pro")
        response = llm_model.generate_content(prompt)
        generated_sql = response.text.strip()
        # Remove code block markers if present
        if generated_sql.startswith("````") or generated_sql.startswith("```sql") or generated_sql.startswith("```"):
            generated_sql = generated_sql.strip("`")
            if generated_sql.startswith("sql"):
                generated_sql = generated_sql[3:].strip()
        # --- Post-processing: check tables/columns ---
        tables_in_sql, columns_in_sql = extract_identifiers_from_sql(generated_sql)
        schema_tables, schema_columns = schema_tables_and_columns(schema_content)
        print("LLM generated SQL:", generated_sql)
        print("Tables in SQL:", tables_in_sql)
        print("Schema tables:", schema_tables)
        print("Columns in SQL:", columns_in_sql)
        print("Schema columns:", schema_columns)
        if not tables_in_sql.issubset(schema_tables) or not all(
            (col in schema_columns or col == "*") for col in columns_in_sql
        ):
            return JSONResponse(
                content={
                    "message": "Generated SQL references tables or columns not in the schema.",
                    "generated_sql": generated_sql
                },
                status_code=status.HTTP_200_OK
            )
        return JSONResponse(
            content={
                "message": "SQL generated successfully.",
                "generated_sql": generated_sql
            },
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate SQL: {str(e)}")

# --- SQL Execution Request Model ---
class SqlExecuteRequest(BaseModel):
    sql_query: str
    schema_id: str

@app.post("/api/query/execute")
async def execute(
    request: SqlExecuteRequest,
    db: Session = Depends(get_db)
):
    # Retrieve the schema structure by schema_id
    schema_structure = db.query(SchemaStructure).filter(SchemaStructure.schema_id == request.schema_id).first()
    if not schema_structure or "db_path" not in schema_structure.content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Database file not found for this schema."
        )
    db_path = schema_structure.content["db_path"]
    try:
        engine = create_engine(f"sqlite:///{db_path}")
        with engine.connect() as connection:
            result = connection.execute(text(request.sql_query))
            rows = result.fetchall()
            columns = result.keys()
            results = [dict(zip(columns, row)) for row in rows]
        return JSONResponse(
            content={
                "message": "SQL query executed successfully.",
                "results": results
            },
            status_code=status.HTTP_200_OK
        )
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"SQL execution error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unexpected error: {str(e)}"
        )

# --- Pydantic Model: AnalysisRequest ---
class AnalysisRequest(BaseModel):
    results: List[Dict[str, Any]]
    originalQuery: str
    sql: str

@app.post("/api/query/analyze")
async def analyze_query(
    request: AnalysisRequest,
    db: Session = Depends(get_db)
):
    # Construct the LLM prompt
    prompt = (
        "You are an expert data analyst. Analyze the following SQL query results, considering the original natural language question and the SQL used. "
        "Provide a concise, insightful summary of the data in plain language. If applicable, highlight key trends, anomalies, or interesting observations.\n\n"
        f"Original Question: {request.originalQuery}\n"
        f"SQL Executed: {request.sql}\n"
        f"Query Results: {json.dumps(request.results)}\n"
    )
    try:
        llm_model = genai.GenerativeModel("gemini-1.5-pro")
        response = llm_model.generate_content(prompt)
        analysis = response.text.strip()
        return JSONResponse(
            content={
                "message": "Data analysis generated successfully.",
                "analysis": analysis
            },
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate analysis: {str(e)}"
        )

# --- Database Startup Event ---
@app.on_event("startup")
def on_startup():
    # Ensure all SQLAlchemy tables are created at app startup
    Base.metadata.create_all(bind=engine)

def create_tables_and_insert_data(engine, schema):
    with engine.begin() as conn:
        for table in schema.get("tables", []):
            table_name = table["name"]
            print(f"Creating table: {table_name}")
            columns = table["columns"]
            # Normalize columns: ensure each is an object with 'name' and 'type'
            norm_columns = []
            for col in columns:
                if isinstance(col, str):
                    norm_columns.append({"name": col, "type": "TEXT"})
                elif isinstance(col, dict):
                    norm_columns.append({"name": col.get("name"), "type": col.get("type", "TEXT")})
            columns = norm_columns
            col_defs = []
            for col in columns:
                col_name = col["name"]
                col_type = col.get("type", "TEXT")
                col_defs.append(f'"{col_name}" {col_type}')
            col_defs_str = ", ".join(col_defs)
            create_sql = f'CREATE TABLE IF NOT EXISTS "{table_name}" ({col_defs_str});'
            conn.execute(text(create_sql))
            # Insert data if present (support both 'data' and 'rows' keys)
            data_rows = table.get("data") or table.get("rows")
            inserted_count = 0
            if data_rows:
                col_names_set = set(col["name"] for col in columns)
                for row in data_rows:
                    if not isinstance(row, dict):
                        print(f"Skipping malformed row in table {table_name}: {row}")
                        continue
                    # Align row keys with columns: fill missing with None, ignore extras
                    norm_row = {col: row.get(col, None) for col in col_names_set}
                    col_names = ", ".join([f'"{k}"' for k in norm_row.keys()])
                    placeholders = ", ".join([f':{k}' for k in norm_row.keys()])
                    insert_sql = f'INSERT INTO "{table_name}" ({col_names}) VALUES ({placeholders});'
                    try:
                        conn.execute(text(insert_sql), norm_row)
                        inserted_count += 1
                    except Exception as e:
                        print(f"Failed to insert row into {table_name}: {norm_row} | Error: {e}")
                        continue
            print(f"Inserted {inserted_count} rows into {table_name}")
            # Fetch and print a sample of data from the table
            try:
                sample = conn.execute(text(f'SELECT * FROM "{table_name}" LIMIT 3;')).fetchall()
                print(f"Sample data from {table_name}: {sample}")
            except Exception as e:
                print(f"Failed to fetch sample data from {table_name}: {e}")
        # Print tables in DB for debug
        tables = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';")).fetchall()
        print("Tables in DB after upload:", [t[0] for t in tables])
        # Check if any data is present in any table
        total_rows = 0
        for t in tables:
            tname = t[0]
            try:
                count = conn.execute(text(f'SELECT COUNT(*) FROM "{tname}";')).scalar()
                total_rows += count
            except Exception as e:
                print(f"Failed to count rows in {tname}: {e}")
        if total_rows == 0:
            raise ValueError("No data was inserted into any table. Please check your file format or try a different file.")

# --- Modified upload_schema endpoint ---
@app.post("/api/schema/upload")
async def upload_schema(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded.")

    file_extension = file.filename.split(".")[-1].lower()
    allowed_extensions = ["json", "xlsx", "xls", "csv", "sql", "txt", "db"]

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )

    try:
        file_content = await file.read()
        print(f"Received file: {file.filename}, type: {file_extension}")
        print(f"Content length: {len(file_content)} bytes")

        # Create a new Schema instance and store in DB
        placeholder_user_id = str(uuid.UUID("00000000-0000-0000-0000-000000000001"))
        new_schema = Schema(
            id=str(uuid.uuid4()),
            user_id=placeholder_user_id,
            name=file.filename,
            file_type=file_extension,
            status="PROCESSING"
        )
        db.add(new_schema)
        db.commit()
        db.refresh(new_schema)

        # --- File Processing and DB Creation Logic ---
        user_db_dir = os.path.join(os.path.dirname(__file__), "user_dbs")
        os.makedirs(user_db_dir, exist_ok=True)
        # Use a unique DB file name per upload
        user_db_path = os.path.join(user_db_dir, f"{new_schema.id}.sqlite")
        # Clean up old .sqlite files except the current one
        for fname in os.listdir(user_db_dir):
            fpath = os.path.join(user_db_dir, fname)
            if fname.endswith('.sqlite') and fpath != user_db_path:
                try:
                    os.remove(fpath)
                    print(f"Deleted old DB file: {fpath}")
                except Exception as e:
                    print(f"Could not delete {fpath}: {e}")
        print(f"DB file created at: {user_db_path}")

        if file_extension == "db":
            with open(user_db_path, "wb") as f:
                f.write(file_content)
        else:
            engine = create_engine(f"sqlite:///{user_db_path}")
            llm_model = genai.GenerativeModel("gemini-1.5-pro")
            from schema_parser import parse_schema_hybrid
            schema = parse_schema_hybrid(file_content, file_extension, llm_model)
            print("Parsed schema:", schema)
            create_tables_and_insert_data(engine, schema)

        # Store the DB path and schema in SchemaStructure for future reference
        new_schema_structure = SchemaStructure(
            id=str(uuid.uuid4()),
            schema_id=new_schema.id,
            content={"db_path": user_db_path, "schema": schema}
        )
        db.add(new_schema_structure)
        db.commit()

        # Update schema status to ACTIVE
        new_schema.status = "ACTIVE"
        db.commit()

        response_data = {
            "message": "Schema uploaded and database created successfully.",
            "filename": file.filename,
            "file_type": file_extension,
            "schemaId": str(new_schema.id)
        }
        print(f"Returning response: {response_data}")
        return JSONResponse(
            content=response_data,
            status_code=status.HTTP_201_CREATED
        )
    except Exception as e:
        if 'new_schema' in locals():
            new_schema.status = "ERROR"
            db.commit()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process and store schema/database: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload schema: {str(e)}")

@app.get("/api/schema/status")
async def schema_status(db: Session = Depends(get_db)):
    active_schema = db.query(Schema).filter(Schema.status == "ACTIVE").order_by(Schema.created_at.desc()).first()
    if active_schema:
        return JSONResponse(
            content={
                "status": "active",
                "schema_id": active_schema.id,
                "schema_name": active_schema.name
            },
            status_code=status.HTTP_200_OK
        )
    else:
        return JSONResponse(
            content={
                "status": "no_schema",
                "message": "No active schema found."
            },
            status_code=status.HTTP_200_OK
        )

@app.post("/api/connections")
async def add_connection(
    request: ConnectionCreate,
    db: Session = Depends(get_db)
):
    new_connection = DatabaseConnection(
        name=request.name,
        connection_string=request.connection_string
    )
    db.add(new_connection)
    try:
        db.commit()
        db.refresh(new_connection)
        return JSONResponse(
            content={
                "message": "Database connection added successfully.",
                "connection_id": new_connection.id
            },
            status_code=status.HTTP_201_CREATED
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Connection with this name already exists."
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add connection: {str(e)}"
        )

@app.get("/api/connections")
async def list_connections(db: Session = Depends(get_db)):
    connections = db.query(DatabaseConnection).all()
    response_data = [
        {
            "id": conn.id,
            "name": conn.name,
            "created_at": conn.created_at.isoformat() if conn.created_at else None
        }
        for conn in connections
    ]
    return JSONResponse(
        content={
            "message": "Database connections retrieved successfully.",
            "connections": response_data
        },
        status_code=status.HTTP_200_OK
    )


