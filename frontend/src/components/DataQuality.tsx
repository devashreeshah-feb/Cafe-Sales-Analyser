import React from 'react';
import { useStore } from '../store/useStore';

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('en-GB', { style: 'currency', currency: 'GBP' }).format(value);
};

export const DataQuality = () => {
  const { dataQuality } = useStore();

  if (!dataQuality) return <div className="loader">Loading data quality data...</div>;

  return (
    <div>
      <div className="header">
        <h1>Data Quality Dashboard</h1>
        <p>Audit of missing values and transaction anomalies</p>
      </div>

      <div className="charts-grid">
        <div className="glass-card table-container">
          <div className="chart-header">
            <h3 className="chart-title">Field Completeness Audit</h3>
          </div>
          <table>
            <thead>
              <tr>
                <th>Field</th>
                <th>Missing Records</th>
                <th>Missing %</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {dataQuality.completeness.map((c: any) => (
                <tr key={c.field}>
                  <td>{c.field}</td>
                  <td>{c.missing}</td>
                  <td>{c.missingPercentage.toFixed(1)}%</td>
                  <td>
                    {c.missingPercentage > 10 ? (
                      <span className="badge b-rank">Critical</span>
                    ) : c.missingPercentage > 0 ? (
                      <span className="badge a-rank">Warning</span>
                    ) : (
                      <span className="badge s-rank">Good</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
          <div className="kpi-title">Revenue At Risk</div>
          <div className="kpi-value" style={{ color: 'var(--accent-red)' }}>
            {formatCurrency(dataQuality.revenueAtRisk)}
          </div>
          <p style={{ color: 'var(--text-secondary)', textAlign: 'center', marginTop: '16px', fontSize: '0.875rem' }}>
            Value attributed to transactions with UNKNOWN or ERROR item categories.
          </p>
        </div>
      </div>

      <div className="glass-card">
        <div className="chart-header">
          <h3 className="chart-title">Anomaly Feed (ML Detected)</h3>
        </div>
        <div className="anomaly-list">
          {dataQuality.anomalyFeed.map((a: any) => (
            <div key={a.transactionId} className="anomaly-item">
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span style={{ fontWeight: 600 }}>{a.transactionId}</span>
                <span style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>{new Date(a.date).toLocaleDateString()}</span>
              </div>
              <p>Item: <strong>{a.item}</strong></p>
              <div style={{ display: 'flex', gap: '24px', marginTop: '8px', fontSize: '0.875rem' }}>
                <span>Actual: <strong style={{ color: 'var(--text-primary)' }}>{formatCurrency(a.actualSpent)}</strong></span>
                <span>Predicted: <strong style={{ color: 'var(--text-secondary)' }}>{formatCurrency(a.predictedSpent)}</strong></span>
                <span style={{ color: 'var(--accent-red)' }}>Diff: {formatCurrency(a.difference)}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
