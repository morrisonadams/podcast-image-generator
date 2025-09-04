'use client';

import { useState } from 'react';
import Segments from './Segments';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function Home() {
  const [jobId, setJobId] = useState<string | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);

  const handleUpload = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const fileInput = e.currentTarget.elements.namedItem('audio') as HTMLInputElement;
    const file = fileInput.files?.[0];
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_URL}/upload`, {
      method: 'POST',
      body: formData,
    });
    const data = await res.json();
    // Support both camelCase and snake_case responses
    const id = data.job_id || data.jobId;
    setJobId(id);
    const audioPath = data.audio_url || data.audioUrl;
    if (audioPath) {
      setAudioUrl(`${API_URL}${audioPath}`);
    }
  };

  return (
    <main>
      {!jobId && (
        <form onSubmit={handleUpload}>
          <input type="file" name="audio" accept="audio/*" required />
          <button type="submit">Upload</button>
        </form>
      )}
      {audioUrl && (
        <div>
          <audio controls src={audioUrl} />
        </div>
      )}
      {jobId && <Segments jobId={jobId} />}
    </main>
  );
}
