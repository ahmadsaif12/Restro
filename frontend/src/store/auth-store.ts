import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User } from '@/types/auth';
import { setCookie, deleteCookie } from 'cookies-next';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  setAuth: (user: User, access: string, refresh: string) => void;
  logout: () => void;
  updateUser: (user: User) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      setAuth: (user, access, refresh) => {
        setCookie('access_token', access);
        setCookie('refresh_token', refresh);
        set({ user, isAuthenticated: true });
      },
      logout: () => {
        deleteCookie('access_token');
        deleteCookie('refresh_token');
        set({ user: null, isAuthenticated: false });
      },
      updateUser: (user) => set({ user }),
    }),
    {
      name: 'auth-storage',
    }
  )
);
