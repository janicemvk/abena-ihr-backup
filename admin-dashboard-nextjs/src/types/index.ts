// User types
export interface User {
  id: number;
  name: string;
  email: string;
  role: 'Admin' | 'Provider' | 'Staff';
  status: 'Active' | 'Inactive';
}

// Appointment types
export interface Appointment {
  id: number;
  patientName: string;
  type: string;
  date: string;
  time: string;
  provider: string;
  status: 'Confirmed' | 'Pending' | 'Cancelled';
}

// Billing types
export interface Claim {
  id: string;
  patient: string;
  provider: string;
  service: string;
  amount: number;
  status: 'Pending' | 'Approved' | 'Paid';
  submitted: string;
}

// Feedback types
export interface Feedback {
  id: number;
  patientName: string;
  rating: number;
  comment: string;
  date: string;
  provider: string;
}

// Analytics types
export interface StatItem {
  name: string;
  value: string;
  change?: string;
  changeType?: 'increase' | 'decrease';
  icon: any; // This will be a React component
}

export interface ActivityItem {
  id: number;
  type: string;
  description: string;
  timestamp: string;
} 