import json
import io
import pandas as pd
import sqlparse

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
    try:
        text = file_content.decode("utf-8")
        prompt = (
            "You are a database schema and data extraction assistant. "
            "Given the following unstructured text describing a database schema and its data, "
            "extract the schema as a JSON object in the following format:\n\n"
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
            "For each table, list its name, all columns with their names and data types (if available), "
            "and extract all data rows as objects in the 'data' array. "
            "If a data type is not specified, use 'UNKNOWN'.\n\n"
            "Here is the schema and data description:\n"
            "----------------------\n"
            f"{text}\n"
            "----------------------\n"
            "Respond ONLY with the JSON object, no explanation or extra text."
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
        schema = json.loads(response_text)
        print("Parsed schema:", schema)
        # Validate format
        if "tables" not in schema:
            raise ValueError("LLM response does not contain 'tables' key.")
        return schema
    except Exception as e:
        raise ValueError(f"Failed to parse schema with LLM: {e}")
