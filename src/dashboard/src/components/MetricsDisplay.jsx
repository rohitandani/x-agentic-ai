import React, { useState, useEffect } from 'react';

function MetricsDisplay() {
  const [metrics, setMetrics] = useState([]);
  const prometheusUrl = 'http://prometheus:9090/api/v1/query';

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const response = await fetch(`${prometheusUrl}?query=bigip_cpu_usage`);
        const data = await response.json();
        setMetrics(data.data.result);
      } catch (error) {
        console.error('Error fetching metrics:', error);
      }
    };
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 15000); // Refresh every 15s
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="grid grid-cols-1 gap-4">
      {metrics.length > 0 ? (
        metrics.map((metric, index) => (
          <div key={index} className="bg-white p-4 rounded shadow">
            <h2 className="text-xl font-semibold">{metric.metric.__name__}</h2>
            <p>Instance: {metric.metric.instance}</p>
            <p>Value: {metric.value[1]}</p>
          </div>
        ))
      ) : (
        <p>Loading metrics...</p>
      )}
    </div>
  );
}

export default MetricsDisplay;