const API_BASE_URL = 'http://localhost:8000';

export async function fetchCandidateProfile() {
  try {
    const response = await fetch(`${API_BASE_URL}/candidate`);
    if (!response.ok) {
      throw new Error(`Failed to fetch candidate info: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching candidate profile:', error);
    return null;
  }
}

export async function sendChatMessageStream(question, onChunk) {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ question }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to get response from Candidate AI');
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder('utf-8');
  let done = false;
  let accumulatedText = '';

  while (!done) {
    const { value, done: readerDone } = await reader.read();
    done = readerDone;
    if (value) {
      const chunk = decoder.decode(value, { stream: !done });
      accumulatedText += chunk;
      if (onChunk) {
        onChunk(accumulatedText);
      }
    }
  }

  return accumulatedText;
}

