export async function uploadSchema(file: File) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch('https://lucid-query-pilot.onrender.com/api/schema/upload', {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to upload schema');
  }
  return response.json();
} 