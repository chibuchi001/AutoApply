'use client';

import { useState, useRef } from 'react';
import { Upload, FileText, CheckCircle, Loader2 } from 'lucide-react';
import { Card, CardHeader } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Alert } from '@/components/ui/Alert';
import { autoApplyApi } from '@/lib/api';
import { ResumeData } from '@/types';

interface ResumeUploadProps {
  userId: string;
  onComplete: (parsed: ResumeData, rawText: string, filePath: string) => void;
}

export function ResumeUpload({ userId, onComplete }: ResumeUploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [parsed, setParsed] = useState<ResumeData | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = (f: File) => {
    if (!f.name.endsWith('.pdf')) {
      setError('Only PDF files are supported');
      return;
    }
    setFile(f);
    setError('');
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const f = e.dataTransfer.files[0];
    if (f) handleFile(f);
  };

  const handleParse = async () => {
    if (!file) return;
    setLoading(true);
    setError('');
    try {
      const result = await autoApplyApi.uploadResume(userId, file);
      setParsed(result.parsed);
      onComplete(result.parsed, result.parsed.raw_text || '', result.file_path || '');
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Resume parsing failed');
    } finally {
      setLoading(false);
    }
  };

  if (parsed) {
    return (
      <Card>
        <CardHeader title="Resume" icon={<FileText size={18} />} />
        <div className="bg-green-50 border border-green-200 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-3">
            <CheckCircle size={16} className="text-green-600" />
            <span className="text-sm font-semibold text-green-800">
              {file?.name} — Parsed by Nova 2 Lite
            </span>
          </div>
          <div className="grid grid-cols-2 gap-2 text-xs text-green-700 mb-3">
            <div>
              <span className="font-medium">Experience:</span> {parsed.years_experience} yrs
            </div>
            <div>
              <span className="font-medium">Skills found:</span> {parsed.skills?.length ?? 0}
            </div>
          </div>
          <div className="flex flex-wrap gap-1">
            {parsed.technical_skills?.slice(0, 10).map((skill) => (
              <span
                key={skill}
                className="text-xs bg-white text-green-700 px-2 py-0.5 rounded-full border border-green-200"
              >
                {skill}
              </span>
            ))}
            {(parsed.technical_skills?.length ?? 0) > 10 && (
              <span className="text-xs text-green-600">
                +{(parsed.technical_skills?.length ?? 0) - 10} more
              </span>
            )}
          </div>
        </div>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader title="Resume" icon={<Upload size={18} />} />

      {error && (
        <div className="mb-3">
          <Alert type="error" message={error} onDismiss={() => setError('')} />
        </div>
      )}

      <div
        onDrop={handleDrop}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onClick={() => !file && inputRef.current?.click()}
        className={`
          border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-all
          ${dragOver
            ? 'border-indigo-400 bg-indigo-50'
            : file
            ? 'border-indigo-300 bg-indigo-50/50 cursor-default'
            : 'border-gray-200 hover:border-indigo-300 hover:bg-indigo-50/30'
          }
        `}
      >
        {file ? (
          <>
            <FileText size={28} className="mx-auto mb-2 text-indigo-500" />
            <p className="text-sm font-medium text-indigo-700">{file.name}</p>
            <p className="text-xs text-gray-400 mt-1">
              {(file.size / 1024).toFixed(0)} KB
            </p>
          </>
        ) : (
          <>
            <Upload size={28} className="mx-auto mb-2 text-gray-400" />
            <p className="text-sm text-gray-600 font-medium">
              Drop your PDF resume here
            </p>
            <p className="text-xs text-gray-400 mt-1">or click to browse</p>
          </>
        )}
        <input
          ref={inputRef}
          type="file"
          accept=".pdf"
          className="hidden"
          onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
        />
      </div>

      {file && !loading && (
        <Button
          className="w-full mt-3"
          onClick={handleParse}
          loading={loading}
          icon={<Upload size={14} />}
        >
          Parse with Nova 2 Lite
        </Button>
      )}

      {loading && (
        <div className="flex items-center gap-2 justify-center mt-3 text-sm text-indigo-600">
          <Loader2 size={14} className="animate-spin" />
          Parsing resume with Nova 2 Lite…
        </div>
      )}
    </Card>
  );
}
