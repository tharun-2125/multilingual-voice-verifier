const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const uploadAudio = async (file, language, sourceLanguage, pipeline, suggestLinks = true, claimExtraction = true) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('language', language);
  formData.append('source_language', sourceLanguage);
  formData.append('pipeline', pipeline);
  formData.append('suggest_links', suggestLinks);
  formData.append('extract_claim', claimExtraction);

  const response = await fetch(`${API_BASE_URL}/upload-audio`, {
    method: 'POST',
    body: formData,
  });


  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    throw new Error(errorData?.detail || 'Failed to upload audio');
  }

  return response.json();
};
