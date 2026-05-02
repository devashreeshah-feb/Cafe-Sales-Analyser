import React from 'react';
import { useStore } from '../store/useStore';
import { LayoutDashboard, TrendingUp, AlertTriangle, Coffee } from 'lucide-react';

export const Sidebar = () => {
  const { activeTab, setActiveTab } = useStore();

  const navItems = [
    { id: 'overview', label: 'Revenue Overview', icon: <LayoutDashboard size={20} /> },
    { id: 'profitability', label: 'Profitability', icon: <TrendingUp size={20} /> },
    { id: 'dataquality', label: 'Data Quality', icon: <AlertTriangle size={20} /> },
  ];

  return (
    <div className="sidebar">
      <div className="logo">
        <Coffee size={28} color="#3b82f6" />
        Café Analytics
      </div>
      <div className="nav-links">
        {navItems.map((item) => (
          <div
            key={item.id}
            className={`nav-item ${activeTab === item.id ? 'active' : ''}`}
            onClick={() => setActiveTab(item.id)}
          >
            {item.icon}
            {item.label}
          </div>
        ))}
      </div>
    </div>
  );
};
