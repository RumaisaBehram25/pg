import { TrendingUp, TrendingDown } from 'lucide-react';

const MetricCard = ({ title, value, change, trend }) => {
  const isPositive = trend === 'up';
  const TrendIcon = isPositive ? TrendingUp : TrendingDown;
  
  return (
    <div className="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition-shadow">
      <h3 className="text-sm text-gray-600 mb-2">{title}</h3>
      <div className="flex items-end justify-between">
        <div>
          <p className="text-3xl font-bold text-gray-900">{value}</p>
          <div className="flex items-center gap-1 mt-2">
            <TrendIcon 
              className={`w-4 h-4 ${isPositive ? 'text-green-500' : 'text-red-500'}`} 
            />
            <span className={`text-sm ${isPositive ? 'text-green-500' : 'text-red-500'}`}>
              {change}
            </span>
            <span className="text-sm text-gray-500">last week</span>
          </div>
        </div>
        <div className="w-24 h-12">
          {/* Mini sparkline visualization */}
          <svg viewBox="0 0 100 50" className="w-full h-full">
            <path
              d="M 0 40 Q 25 30, 50 25 Q 75 20, 100 15"
              fill="none"
              stroke={isPositive ? '#10b981' : '#ef4444'}
              strokeWidth="2"
              opacity="0.5"
            />
          </svg>
        </div>
      </div>
    </div>
  );
};

export default MetricCard;




