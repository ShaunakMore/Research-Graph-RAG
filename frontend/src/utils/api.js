// API configuration
const API_BASE_URL = 'http://localhost:8000'; // Your FastAPI backend

export async function uploadPDF(file, paperName) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('paper_name', paperName); // Changed from 'name' to 'paper_name'

  const response = await fetch(`${API_BASE_URL}/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Upload failed');
  }

  return await response.json();
}

export async function sendMessage(message, uploadedPapers) {
  const response = await fetch(`${API_BASE_URL}/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      prompt: message, // Your backend expects 'prompt'
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to send message');
  }

  const data = await response.json();
  return data.message; // Your backend returns { "message": "..." }
}

// Optional: Function to get list of uploaded papers
export async function fetchUploadedPapers() {
  try {
    const response = await fetch(`${API_BASE_URL}/papers`, {
      method: 'GET',
    });

    if (!response.ok) {
      throw new Error('Failed to fetch papers');
    }

    const data = await response.json();
    
    // Transform backend data to match frontend format
    return data.papers.map(paper => ({
      id: paper.paper_id,
      name: paper.paper_id,
      fileName: paper.filename
    }));
  } catch (error) {
    console.error('Error fetching papers:', error);
    return []; // Return empty array if fetch fails
  }
}