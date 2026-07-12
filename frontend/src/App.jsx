/* eslint-disable react/jsx-key -- table cells receive stable keys in DataTable */
import { useEffect, useState } from 'react';
import {
  AlertTriangle, ArrowDownRight, ArrowRight, Award, BarChart3, Bell,
  Check, CheckCircle2, ChevronDown, Cloud, CloudOff, Download,
  FileCheck2, FileText, Gift, Globe2, LayoutDashboard, Leaf, Menu, MoreHorizontal,
  Plus, Settings, ShieldCheck, Sparkles, Target, Trophy, Users,
  WalletCards, X, Zap
} from 'lucide-react';
import {
  Area, AreaChart, Bar, BarChart, CartesianGrid, Cell, Line, LineChart, Pie,
  PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis
} from 'recharts';
import './index.css';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const WS = API.replace(/^http/, 'ws');
async function api(path, options = {}) {
  const response = await fetch(`${API}${path}`, {headers:{'Content-Type':'application/json', ...(options.headers||{})}, ...options});
  if (!response.ok) { const error = await response.json().catch(()=>({detail:'Request failed'})); throw new Error(error.detail || 'Request failed'); }
  return response.json();
}

const nav = [
  ['Dashboard', LayoutDashboard], ['Environmental', Leaf], ['Social', Users],
  ['Governance', ShieldCheck], ['Gamification', Trophy], ['Reports', FileText], ['Settings', Settings],
];
const fallbackScores = [
  { department_id: 1, environmental_score: 78, social_score: 82, governance_score: 91, total_score: 83 },
  { department_id: 2, environmental_score: 91, social_score: 77, governance_score: 88, total_score: 86 },
  { department_id: 3, environmental_score: 72, social_score: 85, governance_score: 84, total_score: 79 },
  { department_id: 4, environmental_score: 86, social_score: 89, governance_score: 90, total_score: 88 },
];
const forecastFallback = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'].map((month, i) => ({ month, baseline: 780-i*18+(i%3)*20 }));
const emissions = [
  { month:'Jan', scope1:180, scope2:240, scope3:330 }, { month:'Feb', scope1:166, scope2:228, scope3:315 },
  { month:'Mar', scope1:171, scope2:218, scope3:307 }, { month:'Apr', scope1:151, scope2:210, scope3:292 },
  { month:'May', scope1:148, scope2:198, scope3:281 }, { month:'Jun', scope1:139, scope2:188, scope3:270 },
];
const departments = ['Manufacturing','Corporate HQ','Logistics','R&D'];

function App() {
  const [active, setActive] = useState('Dashboard');
  const [mobileNav, setMobileNav] = useState(false);
  const [online, setOnline] = useState(navigator.onLine);
  const [scores, setScores] = useState(fallbackScores);
  const [forecast, setForecast] = useState(forecastFallback);
  const [telemetry, setTelemetry] = useState([]);
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [toast, setToast] = useState('');
  const [modal, setModal] = useState(null);

  useEffect(() => {
    const on = () => setOnline(true); const off = () => setOnline(false);
    window.addEventListener('online', on); window.addEventListener('offline', off);
    fetch(`${API}/department-scores`).then(r => r.ok ? r.json() : Promise.reject()).then(setScores).catch(() => {});
    fetch(`${API}/forecast`).then(r => r.ok ? r.json() : Promise.reject()).then(data => setForecast(data.slice(0,12).map((d,i) => ({ month: new Date(d.date).toLocaleDateString('en',{day:'2-digit',month:'short'}), baseline:d.emissions || forecastFallback[i]?.baseline })))).catch(() => {});
    let ws; try { ws = new WebSocket(`${WS}/ws/telemetry`); ws.onmessage = e => { const d=JSON.parse(e.data); const value=[d.value,d.energy_kw,d.power_kw,d.power_usage].map(Number).find(Number.isFinite); if (value === undefined) return; setTelemetry(p => [...p,{time:new Date().toLocaleTimeString([],{minute:'2-digit',second:'2-digit'}),value}].slice(-18)); }; } catch { /* local demo fallback */ }
    return () => { window.removeEventListener('online',on); window.removeEventListener('offline',off); ws?.close(); };
  }, []);
  useEffect(()=>{const handler=e=>notify(`${e.detail} opened`);window.addEventListener('ecosphere-action',handler);return()=>window.removeEventListener('ecosphere-action',handler)},[]);

  const notify = message => { setToast(message); window.setTimeout(() => setToast(''), 2600); };
  const go = page => { setActive(page); setMobileNav(false); };
  const props = { notify, setModal, scores, forecast, telemetry };

  return <div className="app-shell">
    <aside className={`sidebar ${mobileNav ? 'open' : ''}`}>
      <div className="brand"><div className="brand-mark"><Leaf size={21}/></div><div><strong>EcoSphere</strong><span>ESG Intelligence</span></div><button className="mobile-close" onClick={()=>setMobileNav(false)}><X/></button></div>
      <div className="org-switch"><div className="avatar small">AC</div><div><strong>Acme Industries</strong><span>Global organization</span></div><ChevronDown size={15}/></div>
      <nav>{nav.map(([name,Icon])=><button key={name} className={active===name?'active':''} onClick={()=>go(name)}><Icon size={19}/><span>{name}</span>{name==='Governance'&&<i>3</i>}</button>)}</nav>
      <div className="sidebar-live"><div><span className="live-dot"/> LIVE OPERATIONS</div><strong>{Number.isFinite(telemetry.at(-1)?.value) ? telemetry.at(-1).value.toFixed(1) : '42.8'} kW</strong><small>Plant 01 · Energy sensor</small>{telemetry.length>1&&<div className="mini-chart"><ResponsiveContainer><LineChart data={telemetry}><Line dataKey="value" stroke="#63e6a7" dot={false} strokeWidth={2}/></LineChart></ResponsiveContainer></div>}</div>
      <div className="user-card"><div className="avatar">KS</div><div><strong>Kashyap S.</strong><span>ESG Manager</span></div><MoreHorizontal size={18}/></div>
    </aside>
    {mobileNav&&<button className="scrim" aria-label="Close menu" onClick={()=>setMobileNav(false)}/>} 
    <main>
      <header><button className="menu-button" onClick={()=>setMobileNav(true)}><Menu/></button><div><p>Acme Industries <span>/</span> {active}</p><h1>{active==='Dashboard'?'Good morning, Kashyap':active}</h1></div><div className="header-actions"><div className={`sync ${online?'':'offline'}`}>{online?<Cloud size={15}/>:<CloudOff size={15}/>}<span>{online?'Live & synced':'Offline mode'}</span></div><button className="icon-button" onClick={()=>setNotificationsOpen(!notificationsOpen)}><Bell size={19}/><i/></button><div className="avatar">KS</div></div>
        {notificationsOpen&&<NotificationPanel close={()=>setNotificationsOpen(false)}/>} 
      </header>
      <section className="page"><Page name={active} {...props}/></section>
    </main>
    {modal&&<Modal type={modal} close={()=>setModal(null)} notify={notify}/>} 
    {toast&&<div className="toast"><CheckCircle2 size={18}/>{toast}</div>}
  </div>;
}

function Page({name,...props}) {
  return ({Dashboard:<Dashboard/>,Environmental:<Environmental/>,Social:<Social/>,Governance:<Governance/>,Gamification:<Gamification/>,Reports:<Reports/>,Settings:<SettingsView/>}[name])?.type ? (()=>{const C={Dashboard,Environmental,Social,Governance,Gamification,Reports,Settings:SettingsView}[name];return <C {...props}/>})() : null;
}

function Dashboard({scores,forecast,telemetry,notify,setModal}) {
  const [period,setPeriod]=useState('This year'); const [department,setDepartment]=useState('All departments'); const [fleet,setFleet]=useState(35); const [energy,setEnergy]=useState(45);
  const avg = key => Math.round(scores.reduce((a,s)=>a+Number(s[key]||0),0)/scores.length);
  const scenario = forecast.map(d=>({...d, projected:Math.round(d.baseline*(1-(fleet*.0022+energy*.0018)))}));
  const scoreCards=[['Environmental','environmental_score',Leaf,'+4.2','green'],['Social','social_score',Users,'+2.8','blue'],['Governance','governance_score',ShieldCheck,'+1.4','violet'],['Overall ESG','total_score',Sparkles,'+3.1','lime']];
  return <>
    <div className="page-heading"><div><p>Your organization is moving in the right direction.</p></div><div className="toolbar"><button className="select-button" onClick={()=>setDepartment(department==="All departments"?"Manufacturing":department==="Manufacturing"?"Logistics":"All departments")}><Globe2 size={16}/>{department}<ChevronDown size={15}/></button><button className="select-button" onClick={()=>setPeriod(period==='This year'?'Last 12 months':'This year')}>{period}<ChevronDown size={15}/></button><button className="primary" onClick={()=>setModal('carbon')}><Plus size={17}/>Log carbon data</button></div></div>
    <div className="metric-grid">{scoreCards.map(([label,key,Icon,delta,color])=><button className={`metric-card ${color}`} key={label} onClick={()=>notify(`${label} score lineage opened`)}><div className="metric-top"><span><Icon size={17}/>{label}</span><ArrowRight size={16}/></div><div className="metric-value">{avg(key)}<small>/100</small></div><div className="metric-foot"><b><ArrowDownRight size={13}/>{delta}%</b> vs last period</div><div className="score-track"><i style={{width:`${avg(key)}%`}}/></div></button>)}</div>
    <div className="two-col main-row"><Panel title="Emissions trajectory" subtitle="Actual and projected tCO₂e" action="View details"><div className="chart-lg"><ResponsiveContainer><AreaChart data={scenario}><defs><linearGradient id="actual" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#39d98a" stopOpacity=".38"/><stop offset="1" stopColor="#39d98a" stopOpacity="0"/></linearGradient></defs><CartesianGrid stroke="#24352f" vertical={false}/><XAxis dataKey="month"/><YAxis/><Tooltip contentStyle={tooltipStyle}/><Area dataKey="baseline" stroke="#39d98a" fill="url(#actual)" strokeWidth={2}/><Line dataKey="projected" stroke="#94a3a0" strokeDasharray="5 5" dot={false}/></AreaChart></ResponsiveContainer></div></Panel>
      <Panel title="Department performance" subtitle="Overall ESG score by department" action="View ranking"><div className="department-list">{departments.map((d,i)=>{const val=[88,84,79,76][i];return <button key={d} onClick={()=>notify(`${d} drill-down opened`)}><span className="dept-rank">0{i+1}</span><div><strong>{d}</strong><span>{[134,41,58,62][i]} employees</span></div><div className="dept-bar"><i style={{width:`${val}%`}}/></div><b>{val}</b></button>})}</div></Panel></div>
    <div className="three-col"><Panel title="Policy what-if simulator" subtitle="Model decarbonization levers"><Slider label="Fleet electrification" value={fleet} set={setFleet}/><Slider label="Renewable energy" value={energy} set={setEnergy}/><div className="impact"><span>Estimated reduction</span><strong>-{Math.round(fleet*.22+energy*.18)}%</strong></div></Panel>
      <Panel title="Live energy telemetry" subtitle="Plant 01 · updates every 2 seconds"><div className="live-reading"><span className="live-dot"/><strong>{Number.isFinite(telemetry.at(-1)?.value) ? telemetry.at(-1).value.toFixed(1) : '42.8'} <small>kW</small></strong></div><div className="chart-sm"><ResponsiveContainer><LineChart data={telemetry.length?telemetry:[{value:38},{value:41},{value:39},{value:44},{value:43}]}><Line dataKey="value" stroke="#5de4a4" dot={false} strokeWidth={2}/></LineChart></ResponsiveContainer></div></Panel>
      <Panel title="Attention needed" subtitle="Items requiring action"><Action icon={AlertTriangle} color="orange" title="3 compliance issues overdue" meta="Governance · High priority"/><Action icon={FileCheck2} color="blue" title="8 participation reviews" meta="Social · Awaiting approval"/><Action icon={Target} color="violet" title="2 goals at risk" meta="Environmental · Q3 targets"/></Panel></div>
  </>;
}

function Environmental({setModal}) {
  const [tab,setTab]=useState('Overview'); const tabs=['Overview','Transactions','Emission factors','Product profiles','Goals'];
  return <Module accent="green" tabs={tabs} tab={tab} setTab={setTab} action={<button className="primary" onClick={()=>setModal('carbon')}><Plus size={17}/>New transaction</button>}>
    <div className="metric-grid compact"><MiniMetric label="YTD emissions" value="12,480" unit="tCO₂e" delta="-8.4%"/><MiniMetric label="Scope 1" value="2,140" unit="tCO₂e" delta="-5.1%"/><MiniMetric label="Scope 2" value="3,620" unit="tCO₂e" delta="-12.8%"/><MiniMetric label="Scope 3" value="6,720" unit="tCO₂e" delta="-6.2%"/></div>
    <div className="two-col"><Panel title="Emissions by scope" subtitle="Monthly operational footprint"><div className="chart-lg"><ResponsiveContainer><BarChart data={emissions}><CartesianGrid stroke="#24352f" vertical={false}/><XAxis dataKey="month"/><YAxis/><Tooltip contentStyle={tooltipStyle}/><Bar dataKey="scope1" stackId="a" fill="#34d399"/><Bar dataKey="scope2" stackId="a" fill="#38bdf8"/><Bar dataKey="scope3" stackId="a" fill="#a78bfa" radius={[4,4,0,0]}/></BarChart></ResponsiveContainer></div></Panel><Panel title="Emission mix" subtitle="Share by GHG Protocol scope"><div className="donut-wrap"><div className="donut"><ResponsiveContainer><PieChart><Pie data={[{v:17,c:'#34d399'},{v:29,c:'#38bdf8'},{v:54,c:'#a78bfa'}]} dataKey="v" innerRadius={62} outerRadius={88} paddingAngle={3}>{[0,1,2].map(i=><Cell key={i} fill={['#34d399','#38bdf8','#a78bfa'][i]}/>)}</Pie></PieChart></ResponsiveContainer><div><strong>12.4k</strong><span>tCO₂e</span></div></div><div className="legend"><span><i className="green"/>Scope 1 <b>17%</b></span><span><i className="blue"/>Scope 2 <b>29%</b></span><span><i className="violet"/>Scope 3 <b>54%</b></span></div></div></Panel></div>
    <Panel title="Environmental goals" subtitle="Progress toward approved targets" action="Manage goals"><DataTable headers={['Goal','Owner','Current / target','Progress','Deadline','Status']} rows={[[<TableTitle title="Reduce fleet emissions" sub="Logistics"/>,'Vikram Patel','390 / 500 t',<Progress value={78}/>,'31 Dec 2026',<Badge text="On track"/>],[<TableTitle title="Cut packaging waste" sub="Manufacturing"/>,'Marcus Vance','98 / 120 t',<Progress value={82}/>,'30 Sep 2026',<Badge text="At risk" type="warning"/>],[<TableTitle title="100% renewable offices" sub="Corporate HQ"/>,'Sarah Jenkins','80 / 80 t',<Progress value={100}/>,'30 Jun 2026',<Badge text="Completed" type="blue"/>]]}/></Panel>
  </Module>;
}

function Social({notify,setModal}) { const [tab,setTab]=useState('CSR activities'); const [joined,setJoined]=useState([]); const [backendActivities,setBackendActivities]=useState([]); useEffect(()=>{api('/csr-activities').then(setBackendActivities).catch(()=>{})},[]); const fallback=[['Tree plantation','24 joined','200 XP'],['Blood donation','18 joined','150 XP'],['Beach cleanup','31 joined','180 XP'],['ESG learning lab','52 joined','120 XP']]; const activities=(backendActivities.length?backendActivities.map(a=>[a.name,'Open',`${a.xp_reward} XP`,a.id]):fallback.map((a,i)=>[...a,i+1])); const join=async(a)=>{try{await api('/participations',{method:'POST',body:JSON.stringify({activity_id:a[3],employee_name:'Kashyap S.',proof_file:'self-declaration'})});setJoined(p=>[...new Set([...p,a[3]])]);notify(`Joined ${a[0]} — saved to backend`)}catch(e){notify(e.message)}}; return <Module accent="blue" tabs={['CSR activities','Participation','Diversity','Training']} tab={tab} setTab={setTab} action={<button className="primary blue" onClick={()=>setModal('activity')}><Plus size={17}/>New activity</button>}>
  <div className="hero-strip social-strip"><div><span>EMPLOYEE IMPACT</span><h2>Small actions. Measurable change.</h2><p>76% of employees took part in an ESG activity this quarter.</p></div><div className="hero-number"><strong>1,284</strong><span>community hours</span></div></div>
  <div className="activity-grid">{activities.map((a,i)=><article key={a[0]}><div className={`activity-icon c${i}`}><Users/></div><Badge text={i===3?'Learning':'Community'} type="blue"/><h3>{a[0]}</h3><p>{['17 Aug · Riverside Park','23 Aug · City Health Center','05 Sep · Marina Beach','Every Friday · Online'][i%4]}</p><div className="activity-meta"><span>{a[1]}</span><span>{a[2]}</span></div><button className={joined.includes(a[3])?'joined':'secondary'} onClick={()=>join(a)}>{joined.includes(a[3])?<><Check size={16}/>Joined</>:<><Plus size={16}/>Join activity</>}</button></article>)}</div>
  <div className="two-col"><Panel title="Participation review queue" subtitle="Evidence awaiting a decision" action="Open queue"><DataTable headers={['Employee','Activity','Submitted','Points','Decision']} rows={[[<TableTitle title="Aditi Rao" sub="Manufacturing"/>,'Tree plantation','12 Jul','50',<ReviewButtons participationId={1} notify={notify}/>],[<TableTitle title="Karan Shah" sub="Corporate HQ"/>,'ESG learning lab','11 Jul','30',<ReviewButtons participationId={2} notify={notify}/>]]}/></Panel><Panel title="Participation trend" subtitle="Employees active by month"><div className="chart-md"><ResponsiveContainer><AreaChart data={[{m:'Feb',v:42},{m:'Mar',v:49},{m:'Apr',v:58},{m:'May',v:63},{m:'Jun',v:71},{m:'Jul',v:76}]}><XAxis dataKey="m"/><YAxis/><Tooltip contentStyle={tooltipStyle}/><Area dataKey="v" stroke="#38bdf8" fill="#38bdf826"/></AreaChart></ResponsiveContainer></div></Panel></div>
  </Module> }

function Governance({setModal}) { const [tab,setTab]=useState('Overview'); const issues=[['Missing MSDS sheets','Manufacturing','High','2 days overdue'],['Late vendor disclosure','Procurement','Medium','Due today'],['Policy review pending','Corporate HQ','Low','Due in 5 days']]; return <Module accent="violet" tabs={['Overview','Policies','Acknowledgements','Audits','Issues']} tab={tab} setTab={setTab} action={<button className="primary violet" onClick={()=>setModal('audit')}><Plus size={17}/>New audit</button>}>
  <div className="metric-grid compact"><MiniMetric label="Policy compliance" value="94.2" unit="%" delta="+2.1%"/><MiniMetric label="Open issues" value="12" unit="items" delta="3 overdue" warn/><MiniMetric label="Acknowledgement" value="87" unit="%" delta="+6.0%"/><MiniMetric label="Audit readiness" value="91" unit="/100" delta="Strong"/></div>
  <div className="two-col"><Panel title="Compliance posture" subtitle="Open issues by severity"><div className="compliance-score"><div><strong>91</strong><span>Strong posture</span></div><p>Most controls are operating effectively. Three overdue items require immediate ownership.</p></div><div className="severity-bars">{[['Critical',1,15],['High',3,38],['Medium',5,64],['Low',3,38]].map(x=><div key={x[0]}><span>{x[0]} <b>{x[1]}</b></span><i><em style={{width:`${x[2]}%`}}/></i></div>)}</div></Panel><Panel title="Policy acknowledgements" subtitle="Completion by policy"><div className="policy-list">{[['Environmental commitment','96%',96],['Supplier code of conduct','89%',89],['Anti-corruption policy','82%',82],['Data & privacy standard','78%',78]].map(x=><div key={x[0]}><span><strong>{x[0]}</strong><small>Version 2.1 · Due 31 Jul</small></span><Progress value={x[2]}/><b>{x[1]}</b></div>)}</div></Panel></div>
  <Panel title="Compliance issues" subtitle="Prioritized remediation queue" action="View all"><DataTable headers={['Issue','Department','Severity','Due','Owner','Status']} rows={issues.map((x,i)=>[<TableTitle title={x[0]} sub={`CI-00${i+41}`}/>,x[1],<Badge text={x[2]} type={i===0?'danger':i===1?'warning':'neutral'}/>,x[3],['Vikram Patel','R. Iyer','Sarah Jenkins'][i],<Badge text={i===2?'In progress':'Open'} type={i===2?'blue':'danger'}/>])}/></Panel>
  </Module> }

function Gamification({notify}) { const [tab,setTab]=useState('Challenges'); const [points,setPoints]=useState(840); const [rewardsData,setRewardsData]=useState([]); useEffect(()=>{api('/balance/Kashyap%20S.').then(x=>setPoints(x.points_balance)).catch(()=>{});api('/rewards').then(setRewardsData).catch(()=>{})},[]); const rewards=rewardsData.length?rewardsData.map(r=>[r.name,r.points_required,r.stock,r.id]):[['Eco tumbler',150,25,1],['Seed notebook',80,40,2],['Paid leave day',500,5,3]]; const redeem=async r=>{try{const result=await api(`/rewards/redeem?employee_name=${encodeURIComponent('Kashyap S.')}&reward_id=${r[3]}`,{method:'POST'});setPoints(result.points_balance);setRewardsData(p=>p.map(x=>x.id===r[3]?{...x,stock:result.remaining_stock}:x));notify(result.message)}catch(e){notify(e.message)}}; return <Module accent="orange" tabs={['Challenges','Badges','Rewards','Leaderboard']} tab={tab} setTab={setTab} action={<div className="points-pill"><WalletCards size={16}/><strong>{points.toLocaleString()}</strong> points</div>}>
  <div className="hero-strip game-strip"><div><span>YOUR IMPACT JOURNEY</span><h2>Level 12 · Sustainability Champion</h2><p>640 XP until the next level</p><div className="level-track"><i/></div></div><div className="hero-number"><Award size={28}/><strong>4,820</strong><span>total XP</span></div></div>
  <div className="challenge-grid">{[['Sustainability sprint','Hard','19 Aug',72],['Recycle challenge','Easy','25 Aug',46],['Commute green week','Medium','01 Sep',18]].map((x,i)=><article key={x[0]}><div className="challenge-top"><div className={`activity-icon c${i}`}><Zap/></div><Badge text={x[1]} type={i===0?'danger':i===1?'blue':'warning'}/></div><h3>{x[0]}</h3><p>{['Reduce your team footprint by 15%','Build a perfect recycling streak','Choose low-carbon travel for a week'][i]}</p><div className="challenge-stats"><span><b>{[800,350,500][i]}</b> XP</span><span>Due {x[2]}</span></div><Progress value={x[3]}/><small>{x[3]}% completed</small><button className="secondary" onClick={()=>notify(`${x[0]} opened`)}>Continue challenge <ArrowRight size={16}/></button></article>)}</div>
  <div className="two-col"><Panel title="Rewards catalog" subtitle="Redeem your spendable points" action="View catalog"><div className="reward-list">{rewards.map((r,i)=><div key={r[0]}><div className={`reward-icon r${i}`}><Gift/></div><span><strong>{r[0]}</strong><small>{r[2]} in stock</small></span><button onClick={()=>redeem(r)}>{r[1]} pts</button></div>)}</div></Panel><Panel title="Organization leaderboard" subtitle="Top sustainability contributors"><div className="leaderboard">{[['Aditi Rao','Manufacturing','4,820'],['Karan Shah','Corporate HQ','3,910'],['Maya Chen','R&D','3,505'],['You','ESG Office','3,240']].map((x,i)=><div className={x[0]==='You'?'you':''} key={x[0]}><b>0{i+1}</b><div className="avatar small">{x[0].split(' ').map(y=>y[0]).join('')}</div><span><strong>{x[0]}</strong><small>{x[1]}</small></span><em>{x[2]} XP</em></div>)}</div></Panel></div>
  </Module> }

function Reports({notify}) { const [tab,setTab]=useState('Report library'); const [filters,setFilters]=useState([]); const generate=type=>{window.location.assign(`${API}/reports/export?report_type=${encodeURIComponent(type)}`);notify(`${type} CSV download started`);}; return <Module accent="neutral" tabs={['Report library','Custom builder','Exports']} tab={tab} setTab={setTab} action={<button className="secondary" onClick={()=>setTab('Exports')}><Download size={16}/>Export history</button>}>
  <div className="report-intro"><div><span>REPORTING CENTER</span><h2>Turn verified ESG data into decisions.</h2><p>Every report keeps its filters, source cutoff, and audit trail.</p></div><FileText size={54}/></div>
  <div className="report-grid">{[['Environmental report',Leaf,'Emissions, goals and product footprint','green'],['Social report',Users,'Participation, diversity and training','blue'],['Governance report',ShieldCheck,'Policies, audits and compliance','violet'],['ESG summary',BarChart3,'Executive scorecard and trends','lime']].map(([t,I,d,c])=><article key={t}><div className={`report-icon ${c}`}><I/></div><h3>{t}</h3><p>{d}</p><span>Updated 12 Jul 2026</span><button className="secondary" onClick={()=>generate(t)}>Generate <ArrowRight size={16}/></button></article>)}</div>
  <Panel title="Custom report builder" subtitle="Combine filters into an auditable data snapshot"><div className="filter-row">{['Date range','Department','Module','Employee','Challenge','ESG category'].map(f=><button key={f} className={filters.includes(f)?'selected':''} onClick={()=>setFilters(p=>p.includes(f)?p.filter(x=>x!==f):[...p,f])}>{f}<ChevronDown size={14}/></button>)}</div><div className="builder-bottom"><span><FileCheck2/> {filters.length || 0} filters selected · Estimated 1,284 records</span><div><button className="secondary" onClick={()=>setFilters([])}>Clear</button><button className="primary" onClick={()=>generate('Custom report')}><Download size={16}/>Run report</button></div></div></Panel>
  </Module> }

function SettingsView({notify}) { const [tab,setTab]=useState('ESG configuration'); const [sub,setSub]=useState('ESG scoring'); const [toggles,setToggles]=useState({auto:true,csr:true,badges:true,email:false}); useEffect(()=>{api('/settings').then(x=>setToggles({auto:x.auto,csr:x.csr,badges:x.badges,email:x.email})).catch(()=>{})},[]); const toggle=k=>setToggles(p=>({...p,[k]:!p[k]})); const save=async()=>{try{await api('/settings',{method:'PUT',body:JSON.stringify({...toggles,environmental_weight:40,social_weight:30,governance_weight:30})});notify('Settings saved permanently')}catch(e){notify(e.message)}}; return <Module accent="neutral" tabs={['Organization','Departments','Categories','ESG configuration','Notifications']} tab={tab} setTab={setTab} action={<button className="primary" onClick={save}><Check size={16}/>Save changes</button>}>
  <div className="settings-layout"><aside>{["ESG scoring","Automation","Evidence rules","Notification channels","Data & integrations"].map(item=><button key={item} className={sub===item?"active":""} onClick={()=>{setSub(item);notify(` settings opened`)}}>{item}</button>)}</aside><div>
  <Panel title="ESG score weights" subtitle="Pillar weights must total 100%"><div className="weight-grid"><Weight label="Environmental" value="40" color="green"/><Weight label="Social" value="30" color="blue"/><Weight label="Governance" value="30" color="violet"/></div><div className="total-weight"><CheckCircle2/> Total weight: 100% <span>Valid configuration</span></div></Panel>
  <Panel title="Operational automation" subtitle="Rules used across EcoSphere workflows"><Setting label="Automatic emission calculation" desc="Create carbon transactions from linked operational records." value={toggles.auto} set={()=>toggle('auto')}/><Setting label="Require evidence for CSR activities" desc="Participants must attach proof before review." value={toggles.csr} set={()=>toggle('csr')}/><Setting label="Auto-award eligible badges" desc="Evaluate safe unlock rules after XP changes." value={toggles.badges} set={()=>toggle('badges')}/><Setting label="Email notification delivery" desc="Also send configured events by email." value={toggles.email} set={()=>toggle('email')}/></Panel>
  </div></div>
  </Module> }

function Module({tabs,tab,setTab,action,children,accent}) { return <><div className={`module-tabs ${accent}`}>{tabs.map(t=><button className={t===tab?'active':''} onClick={()=>setTab(t)} key={t}>{t}</button>)}<div>{action}</div></div>{children}</> }
function Panel({title,subtitle,action,children}) { return <article className="panel"><div className="panel-head"><div><h3>{title}</h3>{subtitle&&<p>{subtitle}</p>}</div>{action&&<button onClick={()=>window.dispatchEvent(new CustomEvent('ecosphere-action',{detail:action}))}>{action}<ArrowRight size={15}/></button>}</div>{children}</article> }
function MiniMetric({label,value,unit,delta,warn}) { return <div className="mini-metric"><span>{label}</span><strong>{value}<small>{unit}</small></strong><b className={warn?'warn':''}>{delta}</b></div> }
function Slider({label,value,set}) { return <label className="range"><span>{label}<b>{value}%</b></span><input type="range" value={value} onChange={e=>set(+e.target.value)}/></label> }
function Progress({value}) { return <div className="progress"><i style={{width:`${value}%`}}/></div> }
function Badge({text,type='success'}) { return <span className={`badge ${type}`}>{text}</span> }
function TableTitle({title,sub}) { return <span className="table-title"><strong>{title}</strong><small>{sub}</small></span> }
function DataTable({headers,rows}) { return <div className="table-wrap"><table><thead><tr>{headers.map(h=><th key={h}>{h}</th>)}</tr></thead><tbody>{rows.map((r,i)=><tr key={i}>{r.map((c,j)=><td key={j}>{c}</td>)}</tr>)}</tbody></table></div> }
function ReviewButtons({notify,participationId}) { const [done,setDone]=useState(''); const decide=async status=>{try{await api(`/participations/${participationId}`,{method:'PATCH',body:JSON.stringify({status})});setDone(status);notify(`Participation ${status} — backend updated`)}catch(e){notify(e.message)}}; return done?<Badge text={done}/>:<div className="review"><button aria-label="Approve participation" onClick={()=>decide('approved')}><Check/></button><button aria-label="Reject participation" onClick={()=>decide('rejected')}><X/></button></div> }
function Action({icon:Icon,color,title,meta}) { return <button className="action-row"><span className={color}><Icon/></span><div><strong>{title}</strong><small>{meta}</small></div><ArrowRight/></button> }
function Weight({label,value,color}) { return <label><span>{label}</span><div><input defaultValue={value}/><b>%</b></div><i className={color}/></label> }
function Setting({label,desc,value,set}) { return <div className="setting"><div><strong>{label}</strong><p>{desc}</p></div><label className="switch"><input type="checkbox" checked={value} onChange={set}/><i/></label></div> }

function NotificationPanel({close}) { return <div className="notifications"><div><h3>Notifications</h3><button onClick={close}><X/></button></div>{[['Compliance issue overdue','High priority · 12 min ago','danger'],['CSR proof approved','Aditi Rao · 48 min ago','blue'],['Badge unlocked','Carbon Sentinel · 2h ago','green']].map(x=><button key={x[0]}><i className={x[2]}/><span><strong>{x[0]}</strong><small>{x[1]}</small></span></button>)}<button className="all">View all notifications</button></div> }
function Modal({type,close,notify}) {
  const [loading,setLoading]=useState(false);
  const titles={carbon:'Log carbon data',activity:'Create CSR activity',audit:'Schedule ESG audit'};
  const submit=async e=>{e.preventDefault();setLoading(true);const data=Object.fromEntries(new FormData(e.currentTarget));try{
    if(type==='carbon') await api('/carbon-transactions',{method:'POST',body:JSON.stringify({source_type:data.source_type,activity_amount:Number(data.activity_amount),emission_factor_id:Number(data.emission_factor_id),department_id:Number(data.department_id)})});
    if(type==='activity') await api('/csr-activities',{method:'POST',body:JSON.stringify({name:data.title,description:data.description,xp_reward:100,points_reward:50})});
    if(type==='audit') await api('/audits',{method:'POST',body:JSON.stringify({title:data.title,auditor:data.auditor,findings:'Audit scheduled; findings pending.'})});
    close();notify(`${titles[type]} saved to backend`);
  }catch(error){notify(error.message)}finally{setLoading(false)}};
  return <div className="modal-backdrop"><form className="modal" onSubmit={submit}><div className="modal-head"><div><span className="green"><Leaf/></span><div><h2>{titles[type]}</h2><p>Saved locally in the EcoSphere database</p></div></div><button type="button" aria-label="Close" onClick={close}><X/></button></div>
  {type==='carbon'?<div className="form-grid"><label>Source type<select name="source_type"><option value="fleet">Fleet fuel</option><option value="manufacturing">Grid electricity</option><option value="purchase">Purchased goods</option></select></label><label>Department<select name="department_id">{departments.map((x,i)=><option value={i+1} key={x}>{x}</option>)}</select></label><label>Activity amount<input name="activity_amount" type="number" min="0.01" step="0.01" required placeholder="e.g. 420"/></label><label>Emission factor<select name="emission_factor_id"><option value="2">Diesel · kg/L</option><option value="5">Grid electricity · kg/kWh</option><option value="3">Passenger travel · kg/km</option></select></label><label className="full">Evidence reference<input name="evidence" required placeholder="Invoice, meter or source ID"/></label></div>:<div className="form-grid"><label className="full">Title<input name="title" required placeholder={type==='audit'?'Q3 supplier compliance audit':'Community impact day'}/></label>{type==='activity'?<label className="full">Description<input name="description" required placeholder="Describe the employee activity"/></label>:<label className="full">Auditor<input name="auditor" required placeholder="Internal ESG team"/></label>}</div>}
  {type==='carbon'&&<div className="calculation"><Zap/><span><strong>Automatic calculation enabled</strong><small>The matching versioned emission factor will be applied.</small></span></div>}<div className="modal-actions"><button type="button" className="secondary" onClick={close}>Cancel</button><button className="primary" disabled={loading}>{loading?'Saving…':'Save'}</button></div></form></div>
}

const tooltipStyle={background:'#10201b',border:'1px solid #2a3c35',borderRadius:10,color:'#f4fbf7'};
export default App;
