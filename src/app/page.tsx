'use client';

import { useState } from 'react';
import Segments from './Segments';

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
    const res = await fetch('http://localhost:8000/upload', {
      method: 'POST',
      body: formData,
    });
    const data = await res.json();
    setJobId(data.job_id);
    setAudioUrl('http://localhost:8000' + data.audio_url);
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
