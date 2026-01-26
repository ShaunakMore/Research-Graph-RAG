// API configuration
const API_BASE_URL = 'https://research-graph-rag-proxy.vercel.app/';

// Helper function to get auth headers
async function getAuthHeaders(getToken) {
  const token = await getToken();
  return {
    'Authorization': `Bearer ${token}`,
  };
}

export async function uploadPDF(file, paperName, getToken) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('paper_name', paperName);

  const authHeaders = await getAuthHeaders(getToken);

  const response = await fetch(`${API_BASE_URL}/upload`, {
    method: 'POST',
    headers: authHeaders,
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Upload failed');
  }

  return await response.json();
}

export async function sendMessage(message, uploadedPapers, getToken) {
  const authHeaders = await getAuthHeaders(getToken);

  const response = await fetch(`${API_BASE_URL}/query`, {
    method: 'POST',
    headers: {
      ...authHeaders,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      prompt: message,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to send message');
  }

  const data = await response.json();
  return data.message;
}

export async function fetchUploadedPapers(getToken) {
  try {
    const authHeaders = await getAuthHeaders(getToken);

    const response = await fetch(`${API_BASE_URL}/papers`, {
      method: 'GET',
      headers: authHeaders,
    });

    if (!response.ok) {
      throw new Error('Failed to fetch papers');
    }

    const data = await response.json();
    
    return data.papers.map(paper => ({
      id: paper.paper_id,
      name: paper.paper_id,
      fileName: paper.filename
    }));
  } catch (error) {
    console.error('Error fetching papers:', error);
    return [];
  }
}
