import { useState, useEffect } from 'react';
import { Bell, User } from 'lucide-react';
import MetricCard from '../components/MetricCard';
import ProcessingStatusChart from '../components/ProcessingStatusChart';
import RecentActivity from '../components/RecentActivity';
import RecentOrdersTable from '../components/RecentOrdersTable';
import { dashboardAPI } from '../utils/api';

const Dashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [userName, setUserName] = useState('User');
  const [period, setPeriod] = useState('this_week');

  useEffect(() => {
    fetchDashboardData();
    // Get user name from localStorage if available
    const storedUserName = localStorage.getItem('userName');
    if (storedUserName) {
      setUserName(storedUserName);
    }
  }, [period]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await dashboardAPI.getStats(period);
      setDashboardData(data);
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError(err.response?.data?.detail || 'Failed to load dashboard data');
      
      // If unauthorized, show mock data for demo purposes
      if (err.response?.status === 401) {
        setError('Please login to view real data. Showing demo data.');
        setDashboardData(getMockData());
      }
    } finally {
      setLoading(false);
    }
  };

  // Fallback mock data if API fails
  const getMockData = () => ({
    metrics: [
      { title: 'Total Jobs', value: 331, change: '28% last week', trend: 'up' },
      { title: 'Pending Jobs', value: 2000, change: '20.3% last week', trend: 'up' },
      { title: 'Total Flags', value: 2855, change: '15.2% last week', trend: 'up' },
      { title: 'Completed Today', value: 189, change: '22% last week', trend: 'up' },
    ],
    processing_status: [
      { name: 'Job #2850', value: 95 },
      { name: 'Job #2851', value: 75 },
      { name: 'Job #2852', value: 60 },
      { name: 'Job #2853', value: 45 },
    ],
    recent_activity: [
      {
        type: 'completed',
        title: 'Job #2847 Completed',
        description: 'Successfully processed 334 claims from morning batch',
        time: '2 hours ago',
        badge: 'Completed'
      },
      {
        type: 'updated',
        title: 'Rule Updated',
        description: 'High Require Threshold rule modified by Sarah Kim',
        time: '4 hours ago',
      },
      {
        type: 'flagged',
        title: '45 Claims Flagged',
        description: 'Fraud detection run completed with 45 flags',
        time: '6 hours ago',
      },
    ],
    recent_orders: [
      { claimId: '#CLM-8492', patient: 'Lorem Laura', drug: 'Lipitor 20mg', amount: '1,245.00', status: 'Flagged', date: 'Nov 4, 2025' },
      { claimId: '#215', patient: 'Lorem Laura', drug: 'Metformin 500mg', amount: '89.50', status: 'Approved', date: 'Dec 23, 2025' },
      { claimId: '#31', patient: 'Lorem Laura', drug: 'Synthroid 75mcg', amount: '2,890.00', status: 'Processing', date: 'May 30, 2025' },
      { claimId: '#31', patient: 'Lorem Laura', drug: 'Metformin 500mg', amount: '89.50', status: 'Flagged', date: 'May 30, 2025' },
    ]
  });

  if (loading) {
    return (
      <div className="flex-1 overflow-auto bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  const data = dashboardData || getMockData();

  return (
    <div className="flex-1 overflow-auto bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-8 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Welcome back, {userName}</h1>
            {error && (
              <p className="text-sm text-amber-600 mt-1">{error}</p>
            )}
          </div>
          <div className="flex items-center gap-4">
            <button 
              onClick={fetchDashboardData}
              className="px-4 py-2 text-sm text-primary hover:bg-primary/10 rounded-lg transition-colors"
            >
              Refresh
            </button>
            <button className="relative p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">
              <Bell className="w-5 h-5" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></span>
            </button>
            <div className="w-10 h-10 rounded-full bg-gray-300 flex items-center justify-center overflow-hidden">
              <User className="w-6 h-6 text-gray-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="p-8">
        {/* Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {data.metrics.map((metric, index) => (
            <MetricCard key={index} {...metric} />
          ))}
        </div>

        {/* Charts and Activity Row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div className="lg:col-span-2">
            <ProcessingStatusChart 
              data={data.processing_status} 
              period={period}
              onPeriodChange={setPeriod}
            />
          </div>
          <div>
            <RecentActivity activities={data.recent_activity} />
          </div>
        </div>

        {/* Recent Orders Table */}
        <RecentOrdersTable orders={data.recent_orders} />
      </div>
    </div>
  );
};

export default Dashboard;