import React from 'react';
import { useStore } from '../store/useStore';

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('en-GB', { style: 'currency', currency: 'GBP' }).format(value);
};

export const Profitability = () => {
  const { profitability } = useStore();

  if (!profitability.length) return <div className="loader">Loading profitability data...</div>;

  const getRankClass = (rank: string) => {
    if (rank.startsWith('S')) return 's-rank';
    if (rank.startsWith('A')) return 'a-rank';
    return 'b-rank';
  };

  return (
    <div>
      <div className="header">
        <h1>Profitability Analysis</h1>
        <p>Item-level margin and revenue performance</p>
      </div>

      <div className="glass-card table-container">
        <table>
          <thead>
            <tr>
              <th>Item</th>
              <th>Revenue</th>
              <th>Est. Profit</th>
              <th>Margin %</th>
              <th>Transactions</th>
              <th>Rank</th>
            </tr>
          </thead>
          <tbody>
            {profitability.map((item: any) => (
              <tr key={item.item}>
                <td style={{ fontWeight: 600 }}>{item.item}</td>
                <td>{formatCurrency(item.revenue)}</td>
                <td style={{ color: 'var(--accent-green)' }}>{formatCurrency(item.profit)}</td>
                <td>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <div style={{ width: '40px' }}>{item.margin.toFixed(0)}%</div>
                    <div className="progress-bar-bg" style={{ width: '100px' }}>
                      <div className="progress-bar-fill" style={{ width: `${item.margin}%` }}></div>
                    </div>
                  </div>
                </td>
                <td>{item.transactions}</td>
                <td>
                  <span className={`badge ${getRankClass(item.rank)}`}>
                    {item.rank}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
