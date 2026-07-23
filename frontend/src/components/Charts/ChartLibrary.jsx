import React, { useEffect, useRef } from 'react';
import Plotly from 'plotly.js-dist-min';
import { useTheme } from '../../contexts/ThemeContext';

const usePlotlyResizer = (ref) => {
  useEffect(() => {
    const handleResize = () => {
      if (ref.current) {
        Plotly.Plots.resize(ref.current);
      }
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [ref]);
};

const getThemeColors = (isDark) => ({
  fontColor: isDark ? '#cbd5e1' : '#334155',
  gridColor: isDark ? '#1e293b' : '#f1f5f9',
  paperColor: 'transparent',
  plotColor: 'transparent',
});

// 1. Line Chart
export const LineChart = ({ x, y, title, height = 300 }) => {
  const containerRef = useRef(null);
  const { isDark } = useTheme();
  usePlotlyResizer(containerRef);

  useEffect(() => {
    if (!containerRef.current) return;
    const colors = getThemeColors(isDark);

    const trace = {
      x,
      y,
      type: 'scatter',
      mode: 'lines+markers',
      line: { color: '#3f709d', width: 3 },
      marker: { size: 6, color: '#1b2c40' },
    };

    const layout = {
      title,
      height,
      margin: { t: 40, b: 40, l: 40, r: 20 },
      paper_bgcolor: colors.paperColor,
      plot_bgcolor: colors.plotColor,
      font: { family: 'Inter, sans-serif', color: colors.fontColor },
      xaxis: { gridcolor: colors.gridColor },
      yaxis: { gridcolor: colors.gridColor },
    };

    Plotly.newPlot(containerRef.current, [trace], layout, { responsive: true, displayModeBar: false });
  }, [x, y, title, height, isDark]);

  return <div ref={containerRef} className="w-full" />;
};

// 2. Bar Chart
export const BarChart = ({ x, y, title, height = 300 }) => {
  const containerRef = useRef(null);
  const { isDark } = useTheme();
  usePlotlyResizer(containerRef);

  useEffect(() => {
    if (!containerRef.current) return;
    const colors = getThemeColors(isDark);

    const trace = {
      x,
      y,
      type: 'bar',
      marker: { color: '#3f709d' },
    };

    const layout = {
      title,
      height,
      margin: { t: 40, b: 45, l: 40, r: 20 },
      paper_bgcolor: colors.paperColor,
      plot_bgcolor: colors.plotColor,
      font: { family: 'Inter, sans-serif', color: colors.fontColor },
      xaxis: { gridcolor: colors.gridColor },
      yaxis: { gridcolor: colors.gridColor },
    };

    Plotly.newPlot(containerRef.current, [trace], layout, { responsive: true, displayModeBar: false });
  }, [x, y, title, height, isDark]);

  return <div ref={containerRef} className="w-full" />;
};

// 3. Donut / Pie Chart
export const DonutChart = ({ values, labels, title, height = 300 }) => {
  const containerRef = useRef(null);
  const { isDark } = useTheme();
  usePlotlyResizer(containerRef);

  useEffect(() => {
    if (!containerRef.current) return;
    const colors = getThemeColors(isDark);

    const trace = {
      values,
      labels,
      type: 'pie',
      hole: 0.45,
      marker: {
        colors: ['#3f709d', '#e06666', '#f6b26b', '#ffd966', '#8e7cc3', '#93c47d'],
      },
    };

    const layout = {
      title,
      height,
      margin: { t: 40, b: 20, l: 20, r: 20 },
      paper_bgcolor: colors.paperColor,
      font: { family: 'Inter, sans-serif', color: colors.fontColor },
      showlegend: true,
      legend: { orientation: 'h', y: -0.15 },
    };

    Plotly.newPlot(containerRef.current, [trace], layout, { responsive: true, displayModeBar: false });
  }, [values, labels, title, height, isDark]);

  return <div ref={containerRef} className="w-full" />;
};

// 4. Area Chart
export const AreaChart = ({ x, y, title, height = 300 }) => {
  const containerRef = useRef(null);
  const { isDark } = useTheme();
  usePlotlyResizer(containerRef);

  useEffect(() => {
    if (!containerRef.current) return;
    const colors = getThemeColors(isDark);

    const trace = {
      x,
      y,
      type: 'scatter',
      mode: 'lines',
      fill: 'tozeroy',
      fillcolor: 'rgba(63, 112, 157, 0.2)',
      line: { color: '#3f709d', width: 2.5 },
    };

    const layout = {
      title,
      height,
      margin: { t: 40, b: 40, l: 40, r: 20 },
      paper_bgcolor: colors.paperColor,
      plot_bgcolor: colors.plotColor,
      font: { family: 'Inter, sans-serif', color: colors.fontColor },
      xaxis: { gridcolor: colors.gridColor },
      yaxis: { gridcolor: colors.gridColor },
    };

    Plotly.newPlot(containerRef.current, [trace], layout, { responsive: true, displayModeBar: false });
  }, [x, y, title, height, isDark]);

  return <div ref={containerRef} className="w-full" />;
};

// 5. Heatmap (Density Map)
export const GeographicHeatmap = ({ z, x, y, title, height = 300 }) => {
  const containerRef = useRef(null);
  const { isDark } = useTheme();
  usePlotlyResizer(containerRef);

  useEffect(() => {
    if (!containerRef.current) return;
    const colors = getThemeColors(isDark);

    const trace = {
      z,
      x,
      y,
      type: 'heatmap',
      colorscale: 'Portland',
    };

    const layout = {
      title,
      height,
      margin: { t: 40, b: 40, l: 40, r: 20 },
      paper_bgcolor: colors.paperColor,
      plot_bgcolor: colors.plotColor,
      font: { family: 'Inter, sans-serif', color: colors.fontColor },
    };

    Plotly.newPlot(containerRef.current, [trace], layout, { responsive: true, displayModeBar: false });
  }, [z, x, y, title, height, isDark]);

  return <div ref={containerRef} className="w-full" />;
};

// 6. Gauge Chart
export const GaugeChart = ({ value, title, height = 240 }) => {
  const containerRef = useRef(null);
  const { isDark } = useTheme();
  usePlotlyResizer(containerRef);

  useEffect(() => {
    if (!containerRef.current) return;
    const colors = getThemeColors(isDark);

    const trace = {
      value,
      title: { text: title, font: { size: 14 } },
      type: 'indicator',
      mode: 'gauge+number',
      gauge: {
        axis: { range: [0, 100], tickcolor: colors.fontColor },
        bar: { color: '#3f709d' },
        bgcolor: isDark ? '#111c2a' : '#f8fafc',
        borderwidth: 1,
        bordercolor: isDark ? '#1e293b' : '#e2e8f0',
        steps: [
          { range: [0, 50], color: 'rgba(239, 68, 68, 0.15)' },
          { range: [50, 75], color: 'rgba(245, 158, 11, 0.15)' },
          { range: [75, 100], color: 'rgba(16, 185, 129, 0.15)' },
        ],
      },
    };

    const layout = {
      height,
      margin: { t: 30, b: 20, l: 30, r: 30 },
      paper_bgcolor: colors.paperColor,
      font: { family: 'Inter, sans-serif', color: colors.fontColor },
    };

    Plotly.newPlot(containerRef.current, [trace], layout, { responsive: true, displayModeBar: false });
  }, [value, title, height, isDark]);

  return <div ref={containerRef} className="w-full" />;
};
