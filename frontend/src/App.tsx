import { Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Overview from './pages/Overview';
import AgentVersions from './pages/AgentVersions';
import WorkflowExplorer from './pages/WorkflowExplorer';
import Recommendations from './pages/Recommendations';
import TraceExplorer from './pages/TraceExplorer';

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Navigate to="/overview" replace />} />
        <Route path="/overview" element={<Overview />} />
        <Route path="/agent-versions" element={<AgentVersions />} />
        <Route path="/workflow-explorer" element={<WorkflowExplorer />} />
        <Route path="/recommendations" element={<Recommendations />} />
        <Route path="/trace-explorer" element={<TraceExplorer />} />
      </Routes>
    </Layout>
  );
}