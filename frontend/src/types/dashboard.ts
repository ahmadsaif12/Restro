export interface DashboardStats {
    todayRevenue: number;
    todayOrders: number;
    pendingOrders: number;
    completedOrders: number;
}

export interface PaymentBreakdown {
    cash: number;
    creditCard: number;
    online: number;
    credit: number;
}

export interface Order {
    id: string;
    status: "PAID" | "PENDING";
    paymentMethod: "Cash" | "Card" | "Online";
    table: string;
    time: string;
    amount: number;
    items: number;
}

export interface DashboardData {
    stats: DashboardStats;
    payments: PaymentBreakdown;
    recentOrders: Order[];
}