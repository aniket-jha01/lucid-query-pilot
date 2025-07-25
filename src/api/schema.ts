export async function uploadSchema(file: File) {
  const formData = new FormData();
  formData.append('file', file);

  console.log('Uploading file:', file.name);
  
  const response = await fetch('https://lucid-query-pilot.onrender.com/api/schema/upload', {
    method: 'POST',
    body: formData,
  });

  console.log('Response status:', response.status);
  console.log('Response headers:', response.headers);

  if (!response.ok) {
    const error = await response.json();
    console.error('Upload error:', error);
    throw new Error(error.detail || 'Failed to upload schema');
  }
  
  const result = await response.json();
  console.log('Upload success:', result);
  return result;
} 