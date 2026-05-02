import { create } from 'zustand';
import axios from 'axios';

const API_URL = '/api';

interface StoreState {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  overview: any;
  profitability: any[];
  dataQuality: any;
  loading: boolean;
  error: string | null;
  fetchDashboardData: () => Promise<void>;
}

export const useStore = create<StoreState>((set) => ({
  activeTab: 'overview',
  setActiveTab: (tab) => set({ activeTab: tab }),
  overview: null,
  profitability: [],
  dataQuality: null,
  loading: false,
  error: null,
  fetchDashboardData: async () => {
    set({ loading: true, error: null });
    try {
      const [overviewRes, profitabilityRes, qualityRes] = await Promise.all([
        axios.get(`${API_URL}/dashboard/overview`),
        axios.get(`${API_URL}/dashboard/profitability`),
        axios.get(`${API_URL}/dashboard/data-quality`)
      ]);
      
      set({
        overview: overviewRes.data,
        profitability: profitabilityRes.data,
        dataQuality: qualityRes.data,
        loading: false
      });
    } catch (error: any) {
      set({ loading: false, error: error.message });
    }
  }
}));
