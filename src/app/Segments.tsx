'use client';

import { useEffect, useState } from 'react';

interface Segment {
  id: number;
  image_url: string;
  title?: string;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function Segments({ jobId }: { jobId: string }) {
  const [segments, setSegments] = useState<Segment[]>([]);

  useEffect(() => {
    if (!jobId) return;
    const es = new EventSource(`${API_URL}/segments/${jobId}`);
    es.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setSegments(data.segments || []);
      } catch (err) {
        console.error('segments parse error', err);
      }
    };
    return () => {
      es.close();
    };
  }, [jobId]);

  if (!segments.length) {
    return <p>Waiting for images...</p>;
  }

  return (
    <div className="segments">
      {segments.map((seg) => (
        <div key={seg.id}>
          <img
            src={`${API_URL}${seg.image_url}`}
            alt={seg.title || ''}
            width={320}
          />
        </div>
      ))}
    </div>
  );
}
