import { CheckCircle, FileEdit, AlertTriangle, AlertCircle } from 'lucide-react';

const activityIcons = {
  completed: CheckCircle,
  updated: FileEdit,
  flagged: AlertTriangle,
  warning: AlertCircle,
};

const activityColors = {
  completed: 'bg-green-100 text-green-600',
  updated: 'bg-blue-100 text-blue-600',
  flagged: 'bg-yellow-100 text-yellow-600',
  warning: 'bg-red-100 text-red-600',
};

const RecentActivity = ({ activities }) => {
  return (
    <div className="bg-white rounded-xl shadow-sm p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900">Recent Activity</h3>
        <button className="text-primary text-sm hover:underline">View more</button>
      </div>
      <div className="space-y-4">
        {activities.map((activity, index) => {
          const Icon = activityIcons[activity.type];
          const colorClass = activityColors[activity.type];
          
          return (
            <div key={index} className="flex items-start gap-3">
              <div className={`p-2 rounded-lg ${colorClass}`}>
                <Icon className="w-5 h-5" />
              </div>
              <div className="flex-1">
                <h4 className="text-sm font-medium text-gray-900">{activity.title}</h4>
                <p className="text-xs text-gray-500 mt-1">{activity.description}</p>
                <span className="text-xs text-gray-400 mt-1 block">{activity.time}</span>
              </div>
              {activity.badge && (
                <span className="px-2 py-1 text-xs bg-green-100 text-green-700 rounded-full">
                  {activity.badge}
                </span>
              )}
            </div>
          );
        })}
      </div>
      
      {/* Show empty state if no activities */}
      {(!activities || activities.length === 0) && (
        <div className="text-center py-8 text-gray-500">
          <p className="text-sm">No recent activity</p>
        </div>
      )}
    </div>
  );
};

export default RecentActivity;



