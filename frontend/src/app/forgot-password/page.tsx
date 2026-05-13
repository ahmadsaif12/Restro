'use client';
import React, { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { UtensilsCrossed, ArrowRight } from 'lucide-react';
import Link from 'next/link';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    try {
      const { authService } = await import('@/lib/api/auth');
      await authService.forgotPassword(email);
      setSent(true);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Something went wrong.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="auth-page">
      <div className="auth-card">
        <div className="auth-logo-wrap">
          <div className="auth-logo">
            <UtensilsCrossed color="white" size={32} />
          </div>
        </div>
        <h1 className="auth-title">Handle My Restro</h1>
        <p className="auth-subtitle">
          {sent ? 'Check your email for the reset link.' : 'Reset your password'}
        </p>

        {!sent ? (
          <form onSubmit={handleSubmit}>
            <Input
              label="Email"
              placeholder="Enter your email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            {error && <p className="auth-error">{error}</p>}
            <Button type="submit" isLoading={isLoading}>
              Send Reset Link <ArrowRight size={20} />
            </Button>
          </form>
        ) : (
          <p className="auth-hint" style={{ marginTop: '16px' }}>
            Didn&apos;t receive it? Check your spam folder or try again.
          </p>
        )}

        <p className="auth-link-row">
          <Link href="/login" className="auth-link-accent">Back to Sign in</Link>
        </p>
      </div>
    </main>
  );
}
