import { useState, useEffect } from 'react';
import { 
  Play, 
  Calendar, 
  CheckCircle, 
  XCircle, 
  Clock, 
  Shield, 
  FileText, 
  Flag,
  AlertTriangle,
  Info
} from 'lucide-react';
import { runsAPI } from '../utils/api';

const RunSummaryPanel = ({ runId }) => {
  const [runDetails, setRunDetails] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (runId) {
      fetchRunDetails();
    } else {
      setRunDetails(null);
      setLoading(false);
    }
  }, [runId]);

  const fetchRunDetails = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await runsAPI.getRunDetails(runId);
      setRunDetails(response.data);
    } catch (err) {
      console.error('Failed to fetch run details:', err);
      setError('Failed to load run details');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    const date = new Date(dateStr);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };

  const getStatusBadge = (status) => {
    const styles = {
      completed: 'bg-green-100 text-green-700 border-green-200',
      failed: 'bg-red-100 text-red-700 border-red-200',
      processing: 'bg-amber-100 text-amber-700 border-amber-200',
    };
    const icons = {
      completed: <CheckCircle className="w-3.5 h-3.5" />,
      failed: <XCircle className="w-3.5 h-3.5" />,
      processing: <Clock className="w-3.5 h-3.5 animate-pulse" />,
    };
    return (
      <span className={`inline-flex items-center gap-1 px-2 py-1 text-xs font-medium rounded-full border ${styles[status] || 'bg-gray-100 text-gray-700'}`}>
        {icons[status]}
        {status?.charAt(0).toUpperCase() + status?.slice(1)}
      </span>
    );
  };

  if (!runId) {
    return (
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-4 mb-6">
        <div className="flex items-start gap-3">
          <div className="p-2 bg-blue-100 rounded-lg">
            <Info className="w-5 h-5 text-blue-600" />
          </div>
          <div>
            <h3 className="font-semibold text-blue-900">Viewing Aggregate Data</h3>
            <p className="text-sm text-blue-700 mt-1">
              Select a specific audit run above to view run-scoped metrics with full rule traceability.
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-sm p-6 mb-6 animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-48 mb-4"></div>
        <div className="grid grid-cols-4 gap-4">
          <div className="h-20 bg-gray-200 rounded"></div>
          <div className="h-20 bg-gray-200 rounded"></div>
          <div className="h-20 bg-gray-200 rounded"></div>
          <div className="h-20 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (error || !runDetails) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-6">
        <p className="text-red-700">{error || 'Run not found'}</p>
      </div>
    );
  }

  const { run, rules_applied, flags_by_severity, flags_by_category } = runDetails;

  return (
    <div className="bg-white rounded-xl shadow-sm overflow-hidden mb-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-primary/10 to-purple-100 px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-white rounded-lg shadow-sm">
              <Play className="w-5 h-5 text-primary" />
            </div>
            <div>
              <h3 className="font-bold text-gray-900">
                Audit Run: {run.job_name || `#${run.id.substring(0, 8)}`}
              </h3>
              <p className="text-sm text-gray-600 flex items-center gap-2 mt-0.5">
                <Calendar className="w-3.5 h-3.5" />
                {formatDate(run.run_date)}
              </p>
            </div>
          </div>
          {getStatusBadge(run.status)}
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 divide-x divide-gray-200">
        <div className="p-4 text-center">
          <div className="flex items-center justify-center gap-2 text-gray-600 mb-1">
            <FileText className="w-4 h-4" />
            <span className="text-xs font-medium uppercase">Claims Processed</span>
          </div>
          <p className="text-2xl font-bold text-gray-900">{run.claims_processed}</p>
        </div>
        <div className="p-4 text-center">
          <div className="flex items-center justify-center gap-2 text-gray-600 mb-1">
            <Shield className="w-4 h-4" />
            <span className="text-xs font-medium uppercase">Rules Applied</span>
          </div>
          <p className="text-2xl font-bold text-gray-900">{run.rules_executed}</p>
        </div>
        <div className="p-4 text-center">
          <div className="flex items-center justify-center gap-2 text-gray-600 mb-1">
            <Flag className="w-4 h-4" />
            <span className="text-xs font-medium uppercase">Flags Generated</span>
          </div>
          <p className="text-2xl font-bold text-amber-600">{run.flags_generated}</p>
        </div>
        <div className="p-4 text-center">
          <div className="flex items-center justify-center gap-2 text-gray-600 mb-1">
            <AlertTriangle className="w-4 h-4" />
            <span className="text-xs font-medium uppercase">Flag Rate</span>
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {run.claims_processed > 0 
              ? ((run.flags_generated / run.claims_processed) * 100).toFixed(1) + '%'
              : '0%'}
          </p>
        </div>
      </div>

      {/* Rule Versions Applied */}
      {rules_applied && rules_applied.length > 0 && (
        <div className="px-6 py-4 border-t border-gray-200 bg-gray-50">
          <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <Shield className="w-4 h-4" />
            Rules Applied (with versions)
          </h4>
          <div className="flex flex-wrap gap-2">
            {rules_applied.map((rule, idx) => (
              <span
                key={idx}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-white border border-gray-200 rounded-full text-xs font-medium"
              >
                <span className="text-gray-900">{rule.rule_code}</span>
                <span className="text-gray-400">|</span>
                <span className="text-gray-600">{rule.rule_name}</span>
                <span className="text-gray-400">|</span>
                <span className="text-primary font-semibold">v{rule.version}</span>
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Severity & Category Breakdown */}
      <div className="grid grid-cols-2 divide-x divide-gray-200 border-t border-gray-200">
        {/* By Severity */}
        <div className="p-4">
          <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">By Severity</h4>
          <div className="space-y-1">
            {Object.entries(flags_by_severity || {}).map(([sev, count]) => (
              <div key={sev} className="flex items-center justify-between">
                <span className={`text-sm font-medium ${
                  sev === 'FINANCIAL' ? 'text-red-600' :
                  sev === 'COMPLIANCE' ? 'text-amber-600' :
                  sev === 'CLINICAL' ? 'text-purple-600' :
                  'text-gray-600'
                }`}>{sev}</span>
                <span className="text-sm text-gray-900 font-semibold">{count}</span>
              </div>
            ))}
            {Object.keys(flags_by_severity || {}).length === 0 && (
              <p className="text-sm text-gray-400">No flags</p>
            )}
          </div>
        </div>

        {/* By Category */}
        <div className="p-4">
          <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">By Category</h4>
          <div className="space-y-1">
            {Object.entries(flags_by_category || {}).slice(0, 5).map(([cat, count]) => (
              <div key={cat} className="flex items-center justify-between">
                <span className="text-sm text-gray-600 truncate max-w-[150px]">{cat}</span>
                <span className="text-sm text-gray-900 font-semibold">{count}</span>
              </div>
            ))}
            {Object.keys(flags_by_category || {}).length === 0 && (
              <p className="text-sm text-gray-400">No flags</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default RunSummaryPanel;


