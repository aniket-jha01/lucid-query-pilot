import json
import io
import pandas as pd
import sqlparse

# UNIVERSAL LLM PROMPT FOR SCHEMA EXTRACTION
#
# You are a database schema and data extraction assistant. Given the following file content (which may be JSON, CSV, Excel, SQL, or unstructured text),
# output a JSON object in this format:
# {
#   "tables": [
#     {
#       "name": "table_name",
#       "columns": [
#         {"name": "column_name", "type": "column_type"},
#         ...
#       ],
#       "data": [
#         {"column1": value1, "column2": value2, ...},
#         ...
#       ]
#     },
#     ...
#   ]
# }
# No matter how the schema and data are described, always output a JSON object with tables, columns (with name and type), and data rows. If you cannot do this, respond ONLY with the string: UNPARSABLE.
# Here is the file content:
# ----------------------
# <file content here>
# ----------------------
# Respond ONLY with the JSON object or the string UNPARSABLE, no explanation or extra text.

def parse_json_schema(file_content: bytes) -> dict:
    """
    Parses a JSON schema file and returns a standardized schema dictionary.
    Assumes the JSON is already in the expected format or convertible to it.
    """
    try:
        data = json.loads(file_content.decode("utf-8"))
        # If already in standard format, return as is
        if "tables" in data:
            return data
        # Otherwise, attempt to convert (example: {table_name: {columns: [...]}})
        tables = []
        for table_name, table_info in data.items():
            columns = []
            for col in table_info.get("columns", []):
                if isinstance(col, dict):
                    columns.append({
                        "name": col.get("name"),
                        "type": col.get("type", "UNKNOWN")
                    })
                else:
                    columns.append({
                        "name": col,
                        "type": "UNKNOWN"
                    })
            tables.append({"name": table_name, "columns": columns})
        return {"tables": tables}
    except Exception as e:
        raise ValueError(f"Failed to parse JSON schema: {e}")

def parse_excel_schema(file_content: bytes) -> dict:
    """
    Parses an Excel file and returns a standardized schema dictionary.
    Assumes the first sheet contains columns: table, column, type.
    """
    try:
        df = pd.read_excel(io.BytesIO(file_content), engine="openpyxl")
        required_cols = {"table", "column", "type"}
        if not required_cols.issubset(set(df.columns.str.lower())):
            # Try to normalize column names
            df.columns = [c.lower() for c in df.columns]
        if not required_cols.issubset(set(df.columns)):
            raise ValueError("Excel schema must have columns: table, column, type")
        schema = {}
        for _, row in df.iterrows():
            table = str(row["table"])
            column = str(row["column"])
            col_type = str(row["type"])
            if table not in schema:
                schema[table] = []
            schema[table].append({"name": column, "type": col_type})
        tables = [{"name": t, "columns": cols} for t, cols in schema.items()]
        return {"tables": tables}
    except Exception as e:
        raise ValueError(f"Failed to parse Excel schema: {e}")

def parse_csv_schema(file_content: bytes) -> dict:
    """
    Parses a CSV file and returns a standardized schema dictionary.
    Assumes columns: table, column, type.
    """
    try:
        df = pd.read_csv(io.BytesIO(file_content))
        required_cols = {"table", "column", "type"}
        if not required_cols.issubset(set(df.columns.str.lower())):
            # Try to normalize column names
            df.columns = [c.lower() for c in df.columns]
        if not required_cols.issubset(set(df.columns)):
            raise ValueError("CSV schema must have columns: table, column, type")
        schema = {}
        for _, row in df.iterrows():
            table = str(row["table"])
            column = str(row["column"])
            col_type = str(row["type"])
            if table not in schema:
                schema[table] = []
            schema[table].append({"name": column, "type": col_type})
        tables = [{"name": t, "columns": cols} for t, cols in schema.items()]
        return {"tables": tables}
    except Exception as e:
        raise ValueError(f"Failed to parse CSV schema: {e}")

def parse_sql_ddl_schema(file_content: bytes) -> dict:
    """
    Parses SQL DDL (CREATE TABLE statements) and returns a standardized schema dictionary.
    Uses sqlparse to extract table and column info.
    """
    try:
        sql = file_content.decode("utf-8")
        parsed = sqlparse.parse(sql)
        tables = []
        for stmt in parsed:
            if stmt.get_type() != "CREATE":
                continue
            tokens = [t for t in stmt.tokens if not t.is_whitespace]
            table_name = None
            columns = []
            # Find table name
            for i, token in enumerate(tokens):
                if token.ttype is None and token.is_group:
                    # This is likely the parenthesis group with columns
                    col_tokens = [t for t in token.tokens if not t.is_whitespace]
                    for col_def in col_tokens:
                        if col_def.ttype is None and col_def.is_group:
                            # Nested group, skip
                            continue
                        col_parts = [p for p in col_def.flatten() if not p.is_whitespace]
                        if len(col_parts) >= 2:
                            col_name = col_parts[0].value.strip('`"[]')
                            col_type = col_parts[1].value
                            columns.append({"name": col_name, "type": col_type})
                elif token.ttype is sqlparse.tokens.Name:
                    # Table name is usually after "TABLE"
                    prev = tokens[i-1] if i > 0 else None
                    if prev and prev.match(sqlparse.tokens.Keyword, "TABLE", regex=False):
                        table_name = token.value.strip('`"[]')
            if table_name and columns:
                tables.append({"name": table_name, "columns": columns})
        return {"tables": tables}
    except Exception as e:
        raise ValueError(f"Failed to parse SQL DDL schema: {e}")

def parse_text_schema_with_llm(file_content: bytes, llm_model) -> dict:
    """
    Uses an LLM (e.g., Gemini 1.5 Pro) to analyze unstructured text and infer a structured schema.
    The llm_model should have a .generate_content(prompt) method that returns a response with .text.
    """
    import json as _json
    try:
        text = file_content.decode("utf-8")
        prompt = (
            "You are a database schema and data extraction assistant. "
            "Given the following file content (which may be JSON, CSV, Excel, SQL, or unstructured text), "
            "output a JSON object in this format:\n\n"
            "{\n"
            '  "tables": [\n'
            "    {\n"
            '      "name": "table_name",\n'
            '      "columns": [\n'
            '        {"name": "column_name", "type": "column_type"},\n'
            "        ...\n"
            "      ],\n"
            '      "data": [\n'
            '        {"column1": value1, "column2": value2, ...},\n'
            "        ...\n"
            "      ]\n"
            "    },\n"
            "    ...\n"
            "  ]\n"
            "}\n\n"
            "No matter how the schema and data are described, always output a JSON object with tables, columns (with name and type), and data rows. "
            "For each table, extract all columns (with name and type) and ALL data rows. If data rows are present in the file under any key (such as 'rows', 'data', etc.), always output them under the 'data' key for each table in the output. Map any data arrays (e.g., 'rows', 'data', etc.) to the 'data' key in the output. "
            "If you cannot do this, respond ONLY with the string: UNPARSABLE.\n\n"
            "Here is the file content:\n"
            "----------------------\n"
            f"{text}\n"
            "----------------------\n"
            "Respond ONLY with the JSON object or the string UNPARSABLE, no explanation or extra text."
        )
        response = llm_model.generate_content(prompt)
        print("LLM raw response:", response.text)
        response_text = response.text.strip()
        # Sometimes LLMs wrap JSON in code blocks
        if response_text.startswith("````") or response_text.startswith("```json") or response_text.startswith("```"):
            response_text = response_text.strip("`")
            # Remove possible language hint
            if response_text.startswith("json"):
                response_text = response_text[4:].strip()
        if response_text.strip().upper() == "UNPARSABLE":
            raise ValueError("LLM could not parse the schema/data. Please upload a file with clear tables, columns, and rows.")
        schema = json.loads(response_text)
        print("Parsed schema:", schema)
        # Validate format
        if "tables" not in schema:
            raise ValueError("LLM response does not contain 'tables' key.")
        # Fallback: If the output is missing 'data' but the input had 'rows' or 'data', attempt to map it
        input_json = None
        try:
            input_json = _json.loads(text)
        except Exception:
            pass
        for table in schema["tables"]:
            if not table.get("data") or not isinstance(table["data"], list) or len(table["data"]) == 0:
                # Try to find matching table in input_json and map 'rows' or 'data' to 'data'
                if input_json and isinstance(input_json, dict):
                    tname = table.get("name")
                    tdata = input_json.get(tname)
                    if tdata and isinstance(tdata, dict):
                        for key in ["rows", "data"]:
                            if key in tdata and isinstance(tdata[key], list) and len(tdata[key]) > 0:
                                table["data"] = tdata[key]
                                print(f"Mapped '{key}' from input to 'data' for table {tname}")
        # Validate that at least one table has data rows
        has_data = False
        for table in schema["tables"]:
            if table.get("data") and isinstance(table["data"], list) and len(table["data"]) > 0:
                has_data = True
                break
        if not has_data:
            raise ValueError("No data rows were extracted from your file. Please ensure your file includes data for each table.")
        return schema
    except Exception as e:
        raise ValueError(f"Failed to parse schema with LLM: {e}")

def is_clean_json(file_content: bytes) -> bool:
    try:
        data = json.loads(file_content.decode("utf-8"))
        if not isinstance(data, dict):
            return False
        for table, tdata in data.items():
            if not isinstance(tdata, dict):
                return False
            if "columns" not in tdata or not isinstance(tdata["columns"], (list, tuple)):
                return False
            if not ("rows" in tdata or "data" in tdata):
                return False
            rows = tdata.get("rows") or tdata.get("data")
            if not isinstance(rows, list):
                return False
        return True
    except Exception:
        return False

def parse_clean_json(file_content: bytes) -> dict:
    data = json.loads(file_content.decode("utf-8"))
    tables = []
    for table_name, tdata in data.items():
        # Normalize columns
        columns = []
        for col in tdata["columns"]:
            if isinstance(col, str):
                columns.append({"name": col, "type": "TEXT"})
            elif isinstance(col, dict):
                columns.append({"name": col.get("name"), "type": col.get("type", "TEXT")})
        # Normalize data
        rows = tdata.get("rows") or tdata.get("data")
        tables.append({"name": table_name, "columns": columns, "data": rows})
    return {"tables": tables}

def is_clean_csv(file_content: bytes) -> bool:
    try:
        df = pd.read_csv(io.BytesIO(file_content))
        if set(df.columns.str.lower()) >= {"table", "column", "type"}:
            return True
        return False
    except Exception:
        return False

def parse_clean_csv(file_content: bytes) -> dict:
    df = pd.read_csv(io.BytesIO(file_content))
    df.columns = [c.lower() for c in df.columns]
    schema = {}
    for _, row in df.iterrows():
        table = str(row["table"])
        column = str(row["column"])
        col_type = str(row["type"])
        if table not in schema:
            schema[table] = []
        schema[table].append({"name": column, "type": col_type})
    tables = [{"name": t, "columns": cols, "data": []} for t, cols in schema.items()]
    return {"tables": tables}

def is_clean_excel(file_content: bytes) -> bool:
    try:
        df = pd.read_excel(io.BytesIO(file_content), engine="openpyxl")
        if set(df.columns.str.lower()) >= {"table", "column", "type"}:
            return True
        return False
    except Exception:
        return False

def parse_clean_excel(file_content: bytes) -> dict:
    df = pd.read_excel(io.BytesIO(file_content), engine="openpyxl")
    df.columns = [c.lower() for c in df.columns]
    schema = {}
    for _, row in df.iterrows():
        table = str(row["table"])
        column = str(row["column"])
        col_type = str(row["type"])
        if table not in schema:
            schema[table] = []
        schema[table].append({"name": column, "type": col_type})
    tables = [{"name": t, "columns": cols, "data": []} for t, cols in schema.items()]
    return {"tables": tables}

def parse_schema_hybrid(file_content: bytes, file_extension: str, llm_model=None) -> dict:
    """
    Hybrid parsing: Try deterministic parsing for clean files, fallback to LLM if ambiguous or fails.
    """
    print(f"Hybrid parsing for file type: {file_extension}")
    if file_extension == "json":
        if is_clean_json(file_content):
            print("Using deterministic JSON parser.")
            return parse_clean_json(file_content)
        else:
            print("JSON not clean, falling back to LLM.")
    elif file_extension == "csv":
        if is_clean_csv(file_content):
            print("Using deterministic CSV parser.")
            return parse_clean_csv(file_content)
        else:
            print("CSV not clean, falling back to LLM.")
    elif file_extension in ["xlsx", "xls"]:
        if is_clean_excel(file_content):
            print("Using deterministic Excel parser.")
            return parse_clean_excel(file_content)
        else:
            print("Excel not clean, falling back to LLM.")
    elif file_extension == "sql":
        try:
            print("Trying SQL DDL parser.")
            return parse_sql_ddl_schema(file_content)
        except Exception:
            print("SQL DDL parsing failed, falling back to LLM.")
    # For txt or fallback for all
    if llm_model is not None:
        print("Using LLM for schema extraction.")
        return parse_text_schema_with_llm(file_content, llm_model)
    raise ValueError("No valid parser found and LLM model not provided.")
