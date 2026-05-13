import api from './axios';
import { LoginResponse, RegisterResponse, User } from '@/types/auth';

export const authService = {
  async login(data: any): Promise<LoginResponse> {
    const response = await api.post('/auth/login/', data);
    return response.data;
  },

  async register(data: any): Promise<RegisterResponse> {
    const response = await api.post('/auth/register/', data);
    return response.data;
  },

  async logout(): Promise<void> {
    await api.post('/autho/logout/');
  },

  async getMe(): Promise<User> {
    const response = await api.get('/auth/profile/');
    return response.data;
  },

  async forgotPassword(email: string): Promise<void> {
    await api.post('/auth/password/forgot/', { email });
  },

  async resetPassword(data: any): Promise<void> {
    await api.post('/auth/password/reset/confirm/', data);
  },
};
