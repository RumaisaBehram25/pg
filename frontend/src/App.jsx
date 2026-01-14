import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import UploadCSV from './pages/UploadCSV';
import FlaggedClaims from './pages/FlaggedClaims';
import Rules from './pages/Rules';
import AuditReports from './pages/AuditReports';
import ManageUsers from './pages/ManageUsers';
import AuditTrail from './pages/AuditTrail';
import Support from './pages/Support';
import './index.css';

// Placeholder components for other routes
const Settings = () => <div className="flex-1 p-8"><h1 className="text-2xl font-bold">Settings</h1></div>;

const Logout = () => {
  // Clear auth data
  localStorage.removeItem('token');
  localStorage.removeItem('userName');
  return <Navigate to="/login" replace />;
};

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const token = localStorage.getItem('token');
  
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  
  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      {children}
    </div>
  );
};

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        
        <Route path="/" element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        } />
        
        <Route path="/upload" element={
          <ProtectedRoute>
            <UploadCSV />
          </ProtectedRoute>
        } />
        
        <Route path="/flagged-claims" element={
          <ProtectedRoute>
            <FlaggedClaims />
          </ProtectedRoute>
        } />
        
        <Route path="/rules" element={
          <ProtectedRoute>
            <Rules />
          </ProtectedRoute>
        } />
        
        <Route path="/reports" element={
          <ProtectedRoute>
            <AuditReports />
          </ProtectedRoute>
        } />
        
        <Route path="/users" element={
          <ProtectedRoute>
            <ManageUsers />
          </ProtectedRoute>
        } />
        
        <Route path="/audit-trail" element={
          <ProtectedRoute>
            <AuditTrail />
          </ProtectedRoute>
        } />
        
        <Route path="/support" element={
          <ProtectedRoute>
            <Support />
          </ProtectedRoute>
        } />
        
        <Route path="/settings" element={
          <ProtectedRoute>
            <Settings />
          </ProtectedRoute>
        } />
        
        <Route path="/logout" element={<Logout />} />
      </Routes>
    </Router>
  );
}

export default App;
