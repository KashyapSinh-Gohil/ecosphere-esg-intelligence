import { useState, useEffect } from 'react';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer,
  BarChart, Bar, Legend, LineChart, Line
} from 'recharts';
import { 
  LayoutDashboard, Leaf, Users, Shield, Trophy, FileText, Settings,
  CloudOff, Cloud, Info, Activity
} from 'lucide-react';
import './index.css';

// Reusable Tooltip Component
const InfoTooltip = ({ text }) => (
  <div className="tooltip-container">
    <Info size={14} className="info-icon" />
    <span className="tooltip-text">{text}</span>
  </div>
);

// Base API URL config
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const WS_BASE_URL = API_BASE_URL.replace(/^http/, 'ws');

function App() {
  const [activeTab, setActiveTab] = useState('Dashboard');
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  
  // A/B Testing State (Global)
  const [useAlternativeViz, setUseAlternativeViz] = useState(false);

  // Global Backend Data State
  const [departmentScores, setDepartmentScores] = useState([]);
  const [forecastData, setForecastData] = useState([]);
  const [telemetryStream, setTelemetryStream] = useState([]);

  // Fetch initial data
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Fetch initial scores
    fetch(`${API_BASE_URL}/department-scores`)
      .then(res => res.json())
      .then(data => setDepartmentScores(data))
      .catch(console.error);

    // Fetch forecast
    fetch(`${API_BASE_URL}/forecast`)
      .then(res => res.json())
      .then(data => {
        // Transform backend forecast to chart format
        const formatted = Object.keys(data.forecast).map((date, idx) => ({
          month: date,
          baseline: data.forecast[date],
          projected: data.forecast[date] // will be modified by simulator later
        })).slice(0, 30); // Take first 30 days for readability
        setForecastData(formatted);
      })
      .catch(console.error);

    // WebSocket connection
    const ws = new WebSocket(`${WS_BASE_URL}/ws/telemetry`);
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setTelemetryStream(prev => {
        const newStream = [...prev, { time: new Date().toLocaleTimeString(), value: data.value }];
        return newStream.slice(-20); // Keep last 20 data points
      });
    };

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      ws.close();
    };
  }, []);

  const navItems = [
    { name: 'Dashboard', icon: <LayoutDashboard size={18} /> },
    { name: 'Environmental', icon: <Leaf size={18} /> },
    { name: 'Social', icon: <Users size={18} /> },
    { name: 'Governance', icon: <Shield size={18} /> },
    { name: 'Gamification', icon: <Trophy size={18} /> },
    { name: 'Reports', icon: <FileText size={18} /> },
    { name: 'Settings', icon: <Settings size={18} /> },
  ];

  // Calculate aggregated scores from backend data
  const avgEnv = departmentScores.length > 0 ? (departmentScores.reduce((acc, curr) => acc + curr.environmental_score, 0) / departmentScores.length).toFixed(1) : 0;
  const avgSoc = departmentScores.length > 0 ? (departmentScores.reduce((acc, curr) => acc + curr.social_score, 0) / departmentScores.length).toFixed(1) : 0;
  const avgGov = departmentScores.length > 0 ? (departmentScores.reduce((acc, curr) => acc + curr.governance_score, 0) / departmentScores.length).toFixed(1) : 0;
  const avgTotal = departmentScores.length > 0 ? (departmentScores.reduce((acc, curr) => acc + curr.total_score, 0) / departmentScores.length).toFixed(1) : 0;

  return (
    <div className="app-layout">
      {/* Sidebar Navigation */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <h2>EcoSphere</h2>
          <p>ESG Platform</p>
        </div>
        <nav className="nav-menu">
          {navItems.map(item => (
            <button 
              key={item.name}
              className={`nav-item ${activeTab === item.name ? 'active' : ''}`}
              onClick={() => setActiveTab(item.name)}
            >
              {item.icon} {item.name}
            </button>
          ))}
        </nav>
        
        {/* Real-time telemetry mini-chart in sidebar */}
        {telemetryStream.length > 0 && (
          <div style={{padding: '1rem', marginTop: 'auto'}}>
            <div style={{fontSize: '11px', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem'}}>
              <Activity size={12} color="var(--accent-jade)" /> LIVE SENSOR DATA
            </div>
            <div style={{height: '60px', width: '100%'}}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={telemetryStream}>
                  <Line type="monotone" dataKey="value" stroke="var(--accent-jade)" strokeWidth={2} dot={false} isAnimationActive={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        <div className="sidebar-footer">
          <div className={`status-badge ${isOnline ? 'online' : 'offline'}`}>
            {isOnline ? <Cloud size={14} /> : <CloudOff size={14} />}
            {isOnline ? 'System Live' : 'Local Mode'}
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        <header className="content-header">
          <h1>{activeTab} Overview</h1>
          <div style={{display: 'flex', alignItems: 'center', gap: '1rem'}}>
            <span style={{fontSize: '12px', color: 'var(--text-muted)'}}>A/B Test Variant</span>
            <label className="toggle-switch">
              <input 
                type="checkbox" 
                checked={useAlternativeViz} 
                onChange={() => setUseAlternativeViz(!useAlternativeViz)}
              />
              <span className="slider"></span>
            </label>
          </div>
        </header>

        <div className="scrollable-content">
          {activeTab === 'Dashboard' && (
            <DashboardView 
              useAlternativeViz={useAlternativeViz}
              scores={{env: avgEnv, soc: avgSoc, gov: avgGov, total: avgTotal}}
              baseForecast={forecastData}
            />
          )}
          {activeTab === 'Environmental' && <EnvironmentalView />}
          {activeTab === 'Settings' && (
            <SettingsView 
              useAlternativeViz={useAlternativeViz} 
              setUseAlternativeViz={setUseAlternativeViz} 
            />
          )}
          {['Social', 'Governance', 'Gamification', 'Reports'].includes(activeTab) && (
            <PlaceholderView title={`${activeTab} Module`} />
          )}
        </div>
      </main>
    </div>
  );
}

function DashboardView({ useAlternativeViz, scores, baseForecast }) {
  const [slider1, setSlider1] = useState(50);
  const [slider2, setSlider2] = useState(30);

  // Apply simulator logic to backend forecast data
  const derivedData = baseForecast.map(d => ({
    ...d,
    projected: d.baseline - (d.baseline * ((slider1 + slider2) / 200))
  }));

  const resetScenario = () => {
    setSlider1(0);
    setSlider2(0);
  };

  return (
    <div className="dashboard-grid">
      {/* Dynamic Score Cards from Backend */}
      <div className="score-cards-row">
        <div className="glass-panel score-card environment">
          <div className="score-title">
            Environment Score <InfoTooltip text="Calculated based on Scope 1, 2, and 3 footprint" />
          </div>
          <div className="score-value">{scores.env || '--'} / 100</div>
        </div>
        <div className="glass-panel score-card social">
          <div className="score-title">
            Social Score <InfoTooltip text="Aggregated from D&I and Community engagement" />
          </div>
          <div className="score-value">{scores.soc || '--'} / 100</div>
        </div>
        <div className="glass-panel score-card governance">
          <div className="score-title">
            Governance Score <InfoTooltip text="Board diversity, ethics, and compliance audits" />
          </div>
          <div className="score-value">{scores.gov || '--'} / 100</div>
        </div>
        <div className="glass-panel score-card overall">
          <div className="score-title">
            Overall ESG Score <InfoTooltip text="Weighted average of E, S, and G pillars" />
          </div>
          <div className="score-value">{scores.total || '--'} / 100</div>
        </div>
      </div>

      <div className="glass-panel simulator-box">
        <h3>
          Policy What-If Simulator
          <button className="btn-reset" onClick={resetScenario}>Reset</button>
        </h3>
        <p style={{fontSize: '12px', color: 'var(--text-muted)', marginBottom: '1.5rem'}}>
          Adjust the levers below to see the projected impact on future emissions.
        </p>
        
        <div className="simulator-control">
          <div className="simulator-label">
            <span>Logistics Electrification</span>
            <span>{slider1}% Fleet</span>
          </div>
          <input 
            type="range" min="0" max="100" value={slider1} 
            onChange={(e) => setSlider1(parseInt(e.target.value))}
            className="simulator-slider"
          />
        </div>

        <div className="simulator-control">
          <div className="simulator-label">
            <span>Clean Grid Energy Mix</span>
            <span>{slider2}% Renewables</span>
          </div>
          <input 
            type="range" min="0" max="100" value={slider2} 
            onChange={(e) => setSlider2(parseInt(e.target.value))}
            className="simulator-slider"
          />
        </div>
        
        <button className="btn-primary" style={{width: '100%', marginTop: '1rem'}}>
          Apply Scenario to Operations
        </button>
      </div>

      <div className="glass-panel chart-box">
        <h3>
          Emissions Forecast 
          <InfoTooltip text="Comparison of baseline emissions vs simulator projections (Live Backend Data)" />
        </h3>
        <div style={{height: '250px', marginTop: '1rem'}}>
          <ResponsiveContainer width="100%" height="100%">
            {useAlternativeViz ? (
              <BarChart data={derivedData}>
                <XAxis dataKey="month" stroke="#869489" fontSize={10} tickFormatter={(val) => val.substring(5,10)} />
                <RechartsTooltip contentStyle={{backgroundColor: '#0B2B1F', border: '1px solid rgba(255,255,255,0.1)'}} />
                <Legend iconType="circle" />
                <Bar dataKey="baseline" name="Baseline (tCO2e)" stackId="a" fill="#7B1FA2" radius={[0, 0, 0, 0]} />
                <Bar dataKey="projected" name="Projected (tCO2e)" stackId="a" fill="#00A86B" radius={[4, 4, 0, 0]} />
              </BarChart>
            ) : (
              <AreaChart data={derivedData}>
                <defs>
                  <linearGradient id="colorBaseline" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#7B1FA2" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#7B1FA2" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorProjected" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#00A86B" stopOpacity={0.5}/>
                    <stop offset="95%" stopColor="#00A86B" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="month" stroke="#869489" fontSize={10} tickFormatter={(val) => val.substring(5,10)} />
                <RechartsTooltip contentStyle={{backgroundColor: '#0B2B1F', border: '1px solid rgba(255,255,255,0.1)'}} />
                <Legend iconType="plainline" />
                <Area type="monotone" dataKey="baseline" name="Baseline (tCO2e)" stroke="#7B1FA2" fillOpacity={1} fill="url(#colorBaseline)" />
                <Area type="monotone" dataKey="projected" name="Projected (tCO2e)" stroke="#00A86B" fillOpacity={1} fill="url(#colorProjected)" />
              </AreaChart>
            )}
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

function EnvironmentalView() {
  return (
    <div className="dashboard-grid">
      <div className="glass-panel table-panel">
        <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem'}}>
          <h3 style={{fontSize: '16px'}}>Emissions Tracking & Goals</h3>
          <button className="btn-secondary">Export Data</button>
        </div>
        
        <table className="data-table">
          <thead>
            <tr>
              <th>Metric <InfoTooltip text="Scope classification according to GHG Protocol" /></th>
              <th>Target 2026</th>
              <th>Current (YTD)</th>
              <th style={{width: '30%'}}>Progress</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Scope 1 (Direct)</td>
              <td>5,000 tCO2e</td>
              <td>2,100 tCO2e</td>
              <td><div className="progress-bar"><div className="fill env" style={{width: '42%'}}></div></div></td>
              <td><span className="badge success">On Track</span></td>
            </tr>
            <tr>
              <td>Scope 2 (Indirect)</td>
              <td>8,000 tCO2e</td>
              <td>6,500 tCO2e</td>
              <td><div className="progress-bar"><div className="fill env" style={{width: '81%'}}></div></div></td>
              <td><span className="badge warning">At Risk</span></td>
            </tr>
            <tr>
              <td>Scope 3 (Supply Chain)</td>
              <td>25,000 tCO2e</td>
              <td>12,000 tCO2e</td>
              <td><div className="progress-bar"><div className="fill env" style={{width: '48%'}}></div></div></td>
              <td><span className="badge success">On Track</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}

function SettingsView({ useAlternativeViz, setUseAlternativeViz }) {
  return (
    <div className="glass-panel" style={{maxWidth: '600px'}}>
      <h3 style={{marginBottom: '2rem'}}>Configuration</h3>
      
      <div className="setting-row">
        <div className="setting-label">
          <h4>A/B Testing: Visualization Mode</h4>
          <p>Toggle between Area Chart (Variant A) and Stacked Bar Chart (Variant B).</p>
        </div>
        <label className="toggle-switch">
          <input 
            type="checkbox" 
            checked={useAlternativeViz} 
            onChange={(e) => setUseAlternativeViz(e.target.checked)}
          />
          <span className="slider"></span>
        </label>
      </div>
    </div>
  );
}

function PlaceholderView({ title }) {
  return (
    <div className="glass-panel" style={{textAlign: 'center', padding: '6rem 2rem'}}>
      <h2 style={{marginBottom: '1rem', color: 'var(--text-muted)'}}>{title}</h2>
      <p style={{color: 'var(--text-muted)', opacity: 0.7}}>This module is currently active and collecting data.</p>
    </div>
  );
}

export default App;
