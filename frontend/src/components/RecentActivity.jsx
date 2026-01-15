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
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900">Recent Activity</h3>
      </div>
      <div className="space-y-4">
        {activities && activities.length > 0 ? (
          activities.map((activity, index) => {
            const Icon = activityIcons[activity.type];
            const colorClass = activityColors[activity.type];
            
            // Remove "Completed" from title if badge exists
            let displayTitle = activity.title;
            if (activity.badge && displayTitle.includes('Completed')) {
              displayTitle = displayTitle.replace(/\s*Completed\s*$/, '');
            }
            
            return (
              <div key={index} className="flex items-start gap-3">
                <div className={`p-2 rounded-lg ${colorClass} flex-shrink-0`}>
                  <Icon className="w-5 h-5" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <h4 className="text-sm font-medium text-gray-900">{displayTitle}</h4>
                    {activity.badge && (
                      <span className="px-2 py-1 text-xs bg-green-100 text-green-700 rounded-full whitespace-nowrap">
                        {activity.badge}
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-gray-500 mt-1">{activity.description}</p>
                  <span className="text-xs text-gray-400 mt-1 block">{activity.time}</span>
                </div>
              </div>
            );
          })
        ) : (
          <div className="text-center py-8 text-gray-500">
            <p className="text-sm">No recent activity</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default RecentActivity;