import { 
  LayoutDashboard, 
  Upload, 
  FileText, 
  FileBarChart, 
  Users, 
  HelpCircle, 
  Settings, 
  LogOut,
  Pill,
  AlertTriangle,
  History
} from 'lucide-react';
import { Link, useLocation, useNavigate } from 'react-router-dom';

const Sidebar = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  const navItems = [
    { icon: LayoutDashboard, label: 'Dashboard', path: '/' },
    { icon: Upload, label: 'Upload new CSV', path: '/upload' },
    { icon: AlertTriangle, label: 'Flagged Claims', path: '/flagged-claims' },
    { icon: FileText, label: 'Rules', path: '/rules' },
    { icon: History, label: 'Audit Trail', path: '/audit-trail' },
    { icon: FileBarChart, label: 'Audit Reports', path: '/reports' },
    { icon: Users, label: 'Manage Users', path: '/users' },
    { icon: HelpCircle, label: 'Support', path: '/support' },
  ];


  return (
    <div className="w-64 bg-white h-screen flex flex-col shadow-lg overflow-hidden">
      {/* Logo */}
      <div className="p-6 flex items-center gap-3 shrink-0">
        <div className="bg-primary rounded-lg p-2">
          <Pill className="w-6 h-6 text-white" />
        </div>
        <span className="text-xl font-bold text-gray-800">PharmAudit</span>
      </div>

      {/* Navigation Items - Scrollable */}
      <nav className="flex-1 px-3 py-4 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 px-4 py-2.5 mb-1 rounded-lg transition-colors ${
                isActive
                  ? 'bg-gray-100 text-gray-900 font-medium'
                  : 'text-gray-600 hover:bg-gray-50'
              }`}
            >
              <Icon className="w-5 h-5" />
              <span className="text-sm">{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* Bottom Items - Always visible */}
      <div className="px-3 py-3 border-t border-gray-200 shrink-0 bg-white">
        <Link
          to="/settings"
          className="flex items-center gap-3 px-4 py-2.5 mb-1 rounded-lg text-gray-600 hover:bg-gray-50 transition-colors"
        >
          <Settings className="w-5 h-5" />
          <span className="text-sm">Settings</span>
        </Link>
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-3 px-4 py-2.5 rounded-lg text-red-600 hover:bg-red-50 transition-colors"
        >
          <LogOut className="w-5 h-5" />
          <span className="text-sm font-medium">Log out</span>
        </button>
      </div>
    </div>
  );
};

export default Sidebar;

