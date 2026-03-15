'use client';

import { useState, useEffect } from 'react';
import { signIn, useSession } from 'next-auth/react';
import { User, CheckCircle } from 'lucide-react';
import { Card, CardHeader } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { Alert } from '@/components/ui/Alert';
import { autoApplyApi } from '@/lib/api';

interface ProfileSetupProps {
  onComplete: (userId: string, profile: ProfileData) => void;
}

export interface ProfileData {
  name: string;
  email: string;
  phone: string;
  location: string;
}

export function ProfileSetup({ onComplete }: ProfileSetupProps) {
  const [form, setForm] = useState<ProfileData>({
    name: '',
    email: '',
    phone: '',
    location: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [done, setDone] = useState(false);

  const { data: session, status } = useSession();

  // Auto-complete when an OAuth session already has backend credentials
  useEffect(() => {
    if (status === 'authenticated' && session?.user?.backendUserId && !done) {
      const { backendUserId, backendToken } = session.user;
      if (backendToken && typeof window !== 'undefined') {
        localStorage.setItem('auth_token', backendToken);
      }
      setDone(true);
      onComplete(backendUserId, {
        name: session.user.name ?? '',
        email: session.user.email ?? '',
        phone: '',
        location: '',
      });
    }
  }, [status, session, done, onComplete]);

  const update = (field: keyof ProfileData) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm((p) => ({ ...p, [field]: e.target.value }));

  const handleSubmit = async () => {
    if (!form.name.trim() || !form.email.trim()) {
      setError('Name and email are required');
      return;
    }
    setError('');
    setLoading(true);
    try {
      const result = await autoApplyApi.createUser(form);
      setDone(true);
      onComplete(result.user_id, form);
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Failed to create profile. Is the backend running?');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader
        title="Your Profile"
        icon={<User size={18} />}
      />

      {/* ── Social sign-in ── */}
      {!done && (
        <div className="mb-5">
          <p className="text-xs text-center text-gray-400 mb-3">Sign in with</p>
          <div className="grid grid-cols-2 gap-2">
            {/* Google */}
            <button
              onClick={() => signIn('google', { callbackUrl: typeof window !== 'undefined' ? window.location.href : '/' })}
              className="flex items-center justify-center gap-2 py-2 px-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition text-sm font-medium text-gray-700"
            >
              <svg width="16" height="16" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z"/>
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
              </svg>
              Google
            </button>

            {/* Amazon */}
            <button
              onClick={() => signIn('amazon', { callbackUrl: typeof window !== 'undefined' ? window.location.href : '/' })}
              className="flex items-center justify-center gap-2 py-2 px-3 border border-orange-200 bg-orange-50 rounded-lg hover:bg-orange-100 transition text-sm font-medium text-orange-800"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="#FF9900">
                <path d="M15.93 17.09c-2.27 1.52-5.57 2.33-8.41 2.33-3.98 0-7.56-1.47-10.27-3.91-.21-.19-.02-.45.23-.3 2.92 1.7 6.53 2.72 10.26 2.72 2.52 0 5.28-.52 7.83-1.6.38-.16.7.25.36.76zm1.02-1.16c-.29-.37-1.92-.18-2.65-.09-.22.03-.26-.17-.06-.31 1.3-.91 3.43-.65 3.68-.34.25.31-.07 2.46-1.28 3.49-.19.16-.37.07-.28-.13.27-.68.88-2.25.59-2.62z"/>
                <path d="M3.45 7.93c0-2.91 2.37-4.44 5.86-4.44 1.66 0 3.01.33 4.09.98.94.56 1.44 1.3 1.44 2.46v4.64c0 .67.3 1.28.82 1.73l.01.01v.01c.14.12.16.32.04.46l-1.14 1.02a.37.37 0 0 1-.5-.02c-.54-.48-.84-.95-1.12-1.54-.97 1.1-2.28 1.69-3.77 1.69-2.24 0-3.73-1.4-3.73-3.41 0-1.96 1.3-3.01 3.25-3.44l3.08-.67c.54-.12.71-.3.71-.71v-.22c0-1-.71-1.58-2.09-1.58-1.34 0-2.05.6-2.19 1.59-.04.27-.28.42-.54.36l-1.48-.3a.41.41 0 0 1-.32-.46l-.42-.16zm7.56 3.19V10.3c-.19.08-.38.14-.57.19l-1.4.35c-.92.24-1.39.72-1.39 1.46 0 .82.53 1.29 1.41 1.29 1.16 0 1.95-.73 1.95-2.47z"/>
              </svg>
              Amazon
            </button>

            {/* Apple */}
            <button
              onClick={() => signIn('apple', { callbackUrl: typeof window !== 'undefined' ? window.location.href : '/' })}
              className="flex items-center justify-center gap-2 py-2 px-3 bg-gray-900 rounded-lg hover:bg-black transition text-sm font-medium text-white"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="white">
                <path d="M17.05 20.28c-.98.95-2.05.8-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.25 3.51 7.7 9.05 7.4c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.39-1.32 2.76-2.53 3.99zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z"/>
              </svg>
              Apple
            </button>

            {/* Facebook */}
            <button
              onClick={() => signIn('facebook', { callbackUrl: typeof window !== 'undefined' ? window.location.href : '/' })}
              className="flex items-center justify-center gap-2 py-2 px-3 bg-[#1877F2] rounded-lg hover:bg-[#166FE5] transition text-sm font-medium text-white"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="white">
                <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
              </svg>
              Facebook
            </button>
          </div>

          <div className="relative my-4">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-200" />
            </div>
            <div className="relative flex justify-center text-xs">
              <span className="px-2 bg-white text-gray-400">or fill form below</span>
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="mb-4">
          <Alert type="error" message={error} onDismiss={() => setError('')} />
        </div>
      )}

      <div className="space-y-3">
        <Input
          label="Full Name"
          required
          placeholder="e.g. Chidi Okafor"
          value={form.name}
          onChange={update('name')}
          disabled={done}
        />
        <Input
          label="Email"
          required
          type="email"
          placeholder="chidi@example.com"
          value={form.email}
          onChange={update('email')}
          disabled={done}
        />
        <Input
          label="Phone"
          placeholder="+234 800 000 0000"
          value={form.phone}
          onChange={update('phone')}
          disabled={done}
        />
        <Input
          label="Location"
          placeholder="Lagos, Nigeria"
          value={form.location}
          onChange={update('location')}
          disabled={done}
        />

        {done ? (
          <div className="flex items-center gap-2 text-sm text-green-600 font-medium pt-1">
            <CheckCircle size={16} />
            Profile created successfully
          </div>
        ) : (
          <Button
            className="w-full mt-1"
            onClick={handleSubmit}
            loading={loading}
            disabled={!form.name || !form.email}
          >
            Create Profile
          </Button>
        )}
      </div>
    </Card>
  );
}