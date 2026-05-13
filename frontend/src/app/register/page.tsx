'use client';
import React, { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { UtensilsCrossed, Eye, EyeOff, ArrowRight } from 'lucide-react';
import Link from 'next/link';
import { authService } from '@/lib/api/auth';
import { useRouter } from 'next/navigation';

export default function RegisterPage() {
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    password: '',
    role: 'waiter',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const router = useRouter();

  const update = (field: string, value: string) =>
    setFormData((prev) => ({ ...prev, [field]: value }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    try {
      await authService.register(formData);
      router.push('/login?registered=true');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed. Please try again.');
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
        <p className="auth-subtitle">Create your account</p>

        <form onSubmit={handleSubmit}>
          <Input
            label="Full Name"
            placeholder="Enter your full name"
            required
            value={formData.full_name}
            onChange={(e) => update('full_name', e.target.value)}
          />

          <Input
            label="Email"
            placeholder="Enter your email"
            type="email"
            required
            value={formData.email}
            onChange={(e) => update('email', e.target.value)}
          />

          <div className="password-field">
            <Input
              label="Password"
              placeholder="Create a password"
              type={showPassword ? 'text' : 'password'}
              required
              value={formData.password}
              onChange={(e) => update('password', e.target.value)}
            />
            <button
              type="button"
              className="password-toggle"
              onClick={() => setShowPassword(!showPassword)}
            >
              {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
            </button>
          </div>

          <div className="form-group">
            <label className="label">Role</label>
            <select
              className="input-field select-field"
              value={formData.role}
              onChange={(e) => update('role', e.target.value)}
            >
              <option value="waiter">Waiter</option>
              <option value="cashier">Cashier</option>
              <option value="owner">Owner</option>
            </select>
          </div>

          {error && <p className="auth-error">{error}</p>}

          <Button type="submit" isLoading={isLoading}>
            Create Account <ArrowRight size={20} />
          </Button>
        </form>

        <p className="auth-link-row">
          Already have an account?{' '}
          <Link href="/login" className="auth-link-accent">Sign in</Link>
        </p>
        <p className="auth-link-row">
          <Link href="/forgot-password" className="auth-link-muted">Forgot password?</Link>
        </p>
      </div>
    </main>
  );
}
