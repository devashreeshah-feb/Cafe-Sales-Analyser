import React from 'react';
import { useStore } from '../store/useStore';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  PointElement,
  LineElement,
} from 'chart.js';
import { Bar, Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  PointElement,
  LineElement
);

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('en-GB', { style: 'currency', currency: 'GBP' }).format(value);
};

export const Overview = () => {
  const { overview } = useStore();

  if (!overview) return <div className="loader">Loading overview data...</div>;

  const { kpis, monthlyRevenue, itemRevenue } = overview;

  const monthChartData = {
    labels: monthlyRevenue.map((d: any) => d.month),
    datasets: [
      {
        label: 'Monthly Revenue',
        data: monthlyRevenue.map((d: any) => d.revenue),
        backgroundColor: 'rgba(59, 130, 246, 0.5)',
        borderColor: 'rgba(59, 130, 246, 1)',
        borderWidth: 1,
        borderRadius: 4,
      },
    ],
  };

  const itemChartData = {
    labels: itemRevenue.map((d: any) => d.item),
    datasets: [
      {
        label: 'Revenue by Item',
        data: itemRevenue.map((d: any) => d.revenue),
        backgroundColor: 'rgba(139, 92, 246, 0.5)',
        borderColor: 'rgba(139, 92, 246, 1)',
        borderWidth: 1,
        borderRadius: 4,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        labels: {
          color: '#f8fafc'
        }
      }
    },
    scales: {
      y: {
        ticks: { color: '#94a3b8' },
        grid: { color: 'rgba(255, 255, 255, 0.1)' }
      },
      x: {
        ticks: { color: '#94a3b8' },
        grid: { color: 'rgba(255, 255, 255, 0.1)' }
      }
    }
  };

  return (
    <div>
      <div className="header">
        <h1>Revenue Overview</h1>
        <p>Comprehensive dashboard of sales performance</p>
      </div>

      <div className="kpi-grid">
        <div className="glass-card">
          <div className="kpi-title">Total Revenue</div>
          <div className="kpi-value">{formatCurrency(kpis.totalRevenue)}</div>
        </div>
        <div className="glass-card">
          <div className="kpi-title">Estimated Gross Profit</div>
          <div className="kpi-value">{formatCurrency(kpis.grossProfit)}</div>
        </div>
        <div className="glass-card">
          <div className="kpi-title">Avg Transaction Value</div>
          <div className="kpi-value">{formatCurrency(kpis.avgTransactionValue)}</div>
        </div>
        <div className="glass-card">
          <div className="kpi-title">Data Quality Score</div>
          <div className="kpi-value">{kpis.dataQualityScore.toFixed(1)}%</div>
        </div>
      </div>

      <div className="charts-grid">
        <div className="glass-card">
          <div className="chart-header">
            <h3 className="chart-title">Monthly Revenue</h3>
          </div>
          <Bar options={chartOptions} data={monthChartData} />
        </div>
        <div className="glass-card">
          <div className="chart-header">
            <h3 className="chart-title">Revenue by Item</h3>
          </div>
          <Bar options={{...chartOptions, indexAxis: 'y' as const}} data={itemChartData} />
        </div>
      </div>
    </div>
  );
};
