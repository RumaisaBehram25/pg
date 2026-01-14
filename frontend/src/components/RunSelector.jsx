import { useState, useEffect } from 'react';
import { Play, Calendar, CheckCircle, XCircle, Clock, ChevronDown } from 'lucide-react';
import { runsAPI } from '../utils/api';

const RunSelector = ({ selectedRun, onSelectRun, showAllOption = true }) => {
  const [runs, setRuns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    fetchRuns();
  }, []);

  const fetchRuns = async () => {
    try {
      setLoading(true);
      const response = await runsAPI.getRuns({ limit: 50 });
      setRuns(response.data.runs || []);
    } catch (err) {
      console.error('Failed to fetch runs:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-500" />;
      case 'processing':
        return <Clock className="w-4 h-4 text-amber-500 animate-pulse" />;
      default:
        return <Play className="w-4 h-4 text-gray-400" />;
    }
  };

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const getSelectedLabel = () => {
    if (!selectedRun) return 'All Runs (Aggregate)';
    const run = runs.find(r => r.id === selectedRun);
    if (!run) return 'Select Run...';
    return `Run: ${run.job_name || run.id.substring(0, 8)} - ${formatDate(run.run_date)}`;
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-4 py-2.5 bg-white border border-gray-300 rounded-lg hover:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20 transition-colors min-w-[300px]"
      >
        <Play className="w-4 h-4 text-primary" />
        <span className="flex-1 text-left text-sm font-medium text-gray-700 truncate">
          {loading ? 'Loading runs...' : getSelectedLabel()}
        </span>
        <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setIsOpen(false)} />
          <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-50 max-h-80 overflow-y-auto">
            {showAllOption && (
              <button
                onClick={() => {
                  onSelectRun(null);
                  setIsOpen(false);
                }}
                className={`w-full px-4 py-3 text-left hover:bg-gray-50 flex items-center gap-3 border-b border-gray-100 ${
                  !selectedRun ? 'bg-primary/5' : ''
                }`}
              >
                <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
                  <Play className="w-4 h-4 text-gray-500" />
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">All Runs (Aggregate)</p>
                  <p className="text-xs text-gray-500">View combined data from all runs</p>
                </div>
              </button>
            )}

            {runs.length === 0 && !loading && (
              <div className="px-4 py-6 text-center text-gray-500 text-sm">
                No audit runs found
              </div>
            )}

            {runs.map((run) => (
              <button
                key={run.id}
                onClick={() => {
                  onSelectRun(run.id);
                  setIsOpen(false);
                }}
                className={`w-full px-4 py-3 text-left hover:bg-gray-50 flex items-center gap-3 border-b border-gray-50 ${
                  selectedRun === run.id ? 'bg-primary/5' : ''
                }`}
              >
                <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
                  {getStatusIcon(run.status)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {run.job_name || `Run #${run.id.substring(0, 8)}`}
                    </p>
                    <span className={`px-1.5 py-0.5 text-xs rounded ${
                      run.status === 'completed' ? 'bg-green-100 text-green-700' :
                      run.status === 'failed' ? 'bg-red-100 text-red-700' :
                      'bg-amber-100 text-amber-700'
                    }`}>
                      {run.status}
                    </span>
                  </div>
                  <div className="flex items-center gap-3 text-xs text-gray-500 mt-0.5">
                    <span className="flex items-center gap-1">
                      <Calendar className="w-3 h-3" />
                      {formatDate(run.run_date)}
                    </span>
                    <span>{run.flags_generated} flags</span>
                    <span>{run.claims_processed} claims</span>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
};

export default RunSelector;


