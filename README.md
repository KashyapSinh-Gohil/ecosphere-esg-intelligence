# EcoSphere ESG Intelligence Platform

EcoSphere is a comprehensive, production-ready Environmental, Social, and Governance (ESG) management platform. It combines real-time emissions tracking, gamified CSR engagement, and rigorous compliance auditing into a stunning, "Forest Night" themed glassmorphic UI.

## Key Features

1. **Environmental:** Scope 1, 2 & 3 emissions tracking and predictive "What-If" policy simulation.
2. **Social:** Gamified employee engagement, challenges, and rewards to boost CSR participation.
3. **Governance:** Automated compliance flagging and audit trails.
4. **Usability (A/B Testing):** Built-in A/B testing toggle to optimize data visualization (Area vs Stacked Bar).

## Architecture

- **Backend:** FastAPI (Python), SQLAlchemy (SQLite by default).
- **Frontend:** React, Vite, Recharts, Lucide-React.
- **Deployment:** The FastAPI backend serves the optimized React static build on the root path `/` for a unified, single-command deployment.

---

## 🚀 One-Click Quickstart (Hackathon Demo Mode)

To evaluate the platform, you only need to run a single command. The backend will automatically serve the compiled production frontend.

### Prerequisites
- Python 3.9+
- Node.js (Only required if you want to modify the frontend)

### Installation & Run

1. **Install Backend Dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Run the Unified Server:**
   ```bash
   # From the root directory or backend directory
   PYTHONPATH=. uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
   ```

3. **View the Application:**
   Open your browser and navigate to: [http://localhost:8000](http://localhost:8000)

*(Note: The database is automatically seeded with realistic test data upon the first startup.)*

---

## Frontend Development (Optional)

If you wish to run the frontend in development mode with Hot Module Reloading (HMR):

```bash
cd frontend
npm install
npm run dev
```

The development server will be available at [http://localhost:5173](http://localhost:5173).

## Environment Variables

Copy `.env.example` to `.env` to configure application variables like database URLs and secrets. By default, the system runs perfectly on local SQLite without any configuration required.
