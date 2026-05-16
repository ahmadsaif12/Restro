import api from './axios';
import { DashboardData } from '@/types/dashboard';

export async function fetchDashboardData(): Promise<DashboardData> {
  try {
    const response = await api.get('/orders/summary/');
    return response.data;
  } catch (error) {
    console.error('Error fetching dashboard data:', error);
    // Return mock data for now to keep the UI functional if backend is not ready
    return {
      stats: {
        todayRevenue: 0,
        todayOrders: 0,
        pendingOrders: 0,
        completedOrders: 0,
      },
      payments: {
        cash: 0,
        creditCard: 0,
        online: 0,
        credit: 0,
      },
      recentOrders: [],
    };
  }
}
