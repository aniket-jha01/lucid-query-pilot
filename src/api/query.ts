export async function generateSQL(naturalLanguageQuery: string, schemaId: string) {
  const response = await fetch('https://lucid-query-pilot.onrender.com/api/query/generate-sql', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      natural_language_query: naturalLanguageQuery,
      schema_id: schemaId,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to generate SQL');
  }
  return response.json();
}

export async function fetchActiveSchema() {
  const response = await fetch('https://lucid-query-pilot.onrender.com/api/schema/status');
  if (!response.ok) {
    throw new Error('Failed to fetch schema status');
  }
  return response.json();
}

export async function listConnections() {
  const response = await fetch('https://lucid-query-pilot.onrender.com/api/connections');
  if (!response.ok) {
    throw new Error('Failed to fetch database connections');
  }
  return response.json();
}

export async function executeSQL(sql_query: string, schema_id: string) {
  const response = await fetch('https://lucid-query-pilot.onrender.com/api/query/execute', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ sql_query, schema_id }),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to execute SQL');
  }
  return response.json();
}

export async function analyzeResults(results: any[], originalQuery: string, sql: string) {
  const response = await fetch('https://lucid-query-pilot.onrender.com/api/query/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ results, originalQuery, sql }),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to generate analysis');
  }
  return response.json();
} 