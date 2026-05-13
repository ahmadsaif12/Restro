'use client';
import React, { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { UtensilsCrossed, Eye, EyeOff, ArrowRight } from 'lucide-react';
import Link from 'next/link';
import { authService } from '@/lib/api/auth';
import { useAuthStore } from '@/store/auth-store';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const setAuth = useAuthStore((s) => s.setAuth);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    try {
      const data = await authService.login({ email, password });
      setAuth(data.user, data.access, data.refresh);
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed. Please check your credentials.');
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
        <p className="auth-subtitle">Welcome back!</p>

        <form onSubmit={handleSubmit}>
          <Input
            label="Email"
            placeholder="Enter your email"
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

          <div className="password-field">
            <Input
              label="Password"
              placeholder="Enter your password"
              type={showPassword ? 'text' : 'password'}
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <button
              type="button"
              className="password-toggle"
              onClick={() => setShowPassword(!showPassword)}
            >
              {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
            </button>
          </div>

          {error && <p className="auth-error">{error}</p>}

          <Button type="submit" isLoading={isLoading}>
            Sign In <ArrowRight size={20} />
          </Button>
        </form>

        <p className="auth-link-row">
          Don&apos;t have an account?{' '}
          <Link href="/register" className="auth-link-accent">Sign up</Link>
        </p>
        <p className="auth-link-row">
          <Link href="/forgot-password" className="auth-link-muted">Forgot password?</Link>
        </p>
      </div>
    </main>
  );
}
