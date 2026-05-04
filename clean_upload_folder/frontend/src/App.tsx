import React, { useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { Overview } from './components/Overview';
import { Profitability } from './components/Profitability';
import { DataQuality } from './components/DataQuality';
import { Chatbot } from './components/Chatbot';
import { useStore } from './store/useStore';

function App() {
  const { activeTab, fetchDashboardData, loading, error } = useStore();

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  return (
    <div className="app-container">
      <Sidebar />
      <main className="main-content">
        {error && (
          <div style={{ padding: '16px', background: 'rgba(239, 68, 68, 0.1)', color: '#ef4444', borderRadius: '8px', marginBottom: '24px' }}>
            Error loading data: {error}
          </div>
        )}
        
        {loading ? (
          <div className="loader">Loading dashboard data...</div>
        ) : (
          <>
            {activeTab === 'overview' && <Overview />}
            {activeTab === 'profitability' && <Profitability />}
            {activeTab === 'dataquality' && <DataQuality />}
          </>
        )}
      </main>
      <Chatbot />
    </div>
  );
}

export default App;
