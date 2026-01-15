import { useState, useEffect } from 'react';
import { 
  History, 
  Search, 
  ChevronLeft, 
  ChevronRight, 
  RefreshCw,
  User,
  Shield,
  FileText,
  Flag,
  LogIn,
  UserPlus,
  Edit,
  Trash2,
  Power,
  CheckCircle,
  Eye,
  X,
  Upload,
  Download
} from 'lucide-react';
import { auditAPI } from '../utils/api';
import { exportToCsv, getDateString } from '../utils/exportCsv';

const AuditTrail = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  
  // Filters
  const [searchTerm, setSearchTerm] = useState('');
  const [actionFilter, setActionFilter] = useState('');
  const [resourceFilter, setResourceFilter] = useState('');
  
  // Selected log for detail view
  const [selectedLog, setSelectedLog] = useState(null);
  
  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(25);
  
  // Filter options
  const [actionTypes, setActionTypes] = useState([]);
  const [resourceTypes, setResourceTypes] = useState([]);

  useEffect(() => {
    fetchActionTypes();
  }, []);

  useEffect(() => {
    fetchLogs();
  }, [currentPage, itemsPerPage, actionFilter, resourceFilter]);

  const fetchActionTypes = async () => {
    try {
      const response = await auditAPI.getActionTypes();
      setActionTypes(response.data.actions || []);
      setResourceTypes(response.data.resource_types || []);
    } catch (err) {
      console.error('Failed to fetch action types:', err);
    }
  };

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const params = {
        skip: (currentPage - 1) * itemsPerPage,
        limit: itemsPerPage,
      };
      
      if (actionFilter) params.action = actionFilter;
      if (resourceFilter) params.resource_type = resourceFilter;
      
      const response = await auditAPI.getLogs(params);
      setLogs(response.data.logs || []);
      setTotal(response.data.total || 0);
    } catch (err) {
      console.error('Failed to fetch audit logs:', err);
    } finally {
      setLoading(false);
    }
  };

  // Reset page when filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [actionFilter, resourceFilter, searchTerm]);

  const getActionIcon = (action) => {
    if (action.includes('LOGIN')) return <LogIn className="w-4 h-4" />;
    if (action.includes('USER_CREATED')) return <UserPlus className="w-4 h-4" />;
    if (action.includes('USER_')) return <User className="w-4 h-4" />;
    if (action.includes('RULE_CREATED') || action.includes('RULE_UPDATED')) return <Edit className="w-4 h-4" />;
    if (action.includes('RULE_DELETED')) return <Trash2 className="w-4 h-4" />;
    if (action.includes('RULE_TOGGLED')) return <Power className="w-4 h-4" />;
    if (action.includes('RULE')) return <Shield className="w-4 h-4" />;
    if (action.includes('CSV') || action.includes('JOB')) return <FileText className="w-4 h-4" />;
    if (action.includes('CLAIM') || action.includes('FLAG')) return <Flag className="w-4 h-4" />;
    if (action.includes('REVIEWED')) return <CheckCircle className="w-4 h-4" />;
    return <History className="w-4 h-4" />;
  };

  const getActionColor = (action) => {
    if (action.includes('LOGIN_FAILED')) return 'bg-red-100 text-red-700';
    if (action.includes('LOGIN')) return 'bg-blue-100 text-blue-700';
    if (action.includes('CREATED')) return 'bg-green-100 text-green-700';
    if (action.includes('DELETED')) return 'bg-red-100 text-red-700';
    if (action.includes('UPDATED') || action.includes('TOGGLED')) return 'bg-amber-100 text-amber-700';
    if (action.includes('REVIEWED')) return 'bg-purple-100 text-purple-700';
    if (action.includes('UPLOADED')) return 'bg-cyan-100 text-cyan-700';
    return 'bg-gray-100 text-gray-700';
  };

  const formatAction = (action) => {
    // Extract just the action type (before the colon if there are details)
    const actionType = action.split(':')[0];
    return actionType.replace(/_/g, ' ');
  };

  const getActionDetails = (action) => {
    // Extract details after the colon
    const parts = action.split(': ');
    return parts.length > 1 ? parts.slice(1).join(': ') : null;
  };

  // Filter logs by search term
  const filteredLogs = logs.filter(log => {
    if (!searchTerm) return true;
    const search = searchTerm.toLowerCase();
    return (
      log.action?.toLowerCase().includes(search) ||
      log.user_email?.toLowerCase().includes(search) ||
      log.resource_type?.toLowerCase().includes(search)
    );
  });

  // Pagination
  const totalPages = Math.ceil(total / itemsPerPage);

  const getPageNumbers = () => {
    const pages = [];
    const maxVisiblePages = 5;
    
    if (totalPages <= maxVisiblePages) {
      for (let i = 1; i <= totalPages; i++) pages.push(i);
    } else {
      if (currentPage <= 3) {
        for (let i = 1; i <= 4; i++) pages.push(i);
        pages.push('...');
        pages.push(totalPages);
      } else if (currentPage >= totalPages - 2) {
        pages.push(1);
        pages.push('...');
        for (let i = totalPages - 3; i <= totalPages; i++) pages.push(i);
      } else {
        pages.push(1);
        pages.push('...');
        for (let i = currentPage - 1; i <= currentPage + 1; i++) pages.push(i);
        pages.push('...');
        pages.push(totalPages);
      }
    }
    return pages;
  };

  return (
    <div className="flex-1 overflow-auto bg-gray-50">
      <div className="bg-white border-b border-gray-200 px-8 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Audit Trail</h1>
            <p className="text-sm text-gray-600 mt-1">Track all actions and changes in the system</p>
          </div>
          <div className="flex items-center gap-2">
            {logs.length > 0 && (
              <button
                onClick={() => {
                  const columns = [
                    { key: 'timestamp', header: 'Timestamp' },
                    { key: 'user_email', header: 'User' },
                    { key: 'action', header: 'Action' },
                    { key: 'resource_type', header: 'Resource Type' },
                    { key: 'resource_id', header: 'Resource ID' },
                    { key: 'ip_address', header: 'IP Address' },
                  ];
                  exportToCsv(logs, columns, `audit_trail_${getDateString()}.csv`);
                }}
                className="px-4 py-2 text-sm text-primary hover:bg-primary/10 rounded-lg transition-colors"
              >
             
                Export CSV
              </button>
            )}
            <button
              onClick={fetchLogs}
              className="px-4 py-2 text-sm text-primary hover:bg-primary/10 rounded-lg transition-color"
            >
              Refresh
            </button>
          </div>
        </div>
      </div>

      <div className="p-8">
        {/* Filters */}
        <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search */}
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search logs..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>

            {/* Action Filter */}
            <select
              value={actionFilter}
              onChange={(e) => setActionFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="">All Actions</option>
              {actionTypes.map(action => (
                <option key={action.value} value={action.value}>{action.label}</option>
              ))}
            </select>

            {/* Resource Filter */}
            <select
              value={resourceFilter}
              onChange={(e) => setResourceFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="">All Resources</option>
              {resourceTypes.map(resource => (
                <option key={resource.value} value={resource.value}>{resource.label}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Audit Logs Table */}
        <div className="bg-white rounded-xl shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Timestamp</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">User</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Action</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Details</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Resource</th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {loading ? (
                  <tr>
                    <td colSpan="5" className="px-6 py-12 text-center text-gray-500">
                      <div className="flex items-center justify-center gap-2">
                        <RefreshCw className="w-5 h-5 animate-spin" />
                        Loading audit logs...
                      </div>
                    </td>
                  </tr>
                ) : filteredLogs.length === 0 ? (
                  <tr>
                    <td colSpan="5" className="px-6 py-12 text-center text-gray-500">
                      <History className="w-12 h-12 mx-auto mb-3 text-gray-400" />
                      No audit logs found
                    </td>
                  </tr>
                ) : (
                  filteredLogs.map((log) => (
                    <tr key={log.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 text-sm text-gray-600 whitespace-nowrap">
                        <div>{new Date(log.timestamp).toLocaleDateString()}</div>
                        <div className="text-xs text-gray-400">
                          {new Date(log.timestamp).toLocaleTimeString()}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <div className="w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center">
                            <User className="w-4 h-4 text-primary" />
                          </div>
                          <span className="text-sm text-gray-900">{log.user_email || 'System'}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium ${getActionColor(log.action)}`}>
                          {getActionIcon(log.action)}
                          {formatAction(log.action)}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600 max-w-xs truncate">
                        {getActionDetails(log.action) || '-'}
                      </td>
                      <td className="px-6 py-4">
                        {log.resource_type && (
                          <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs font-medium">
                            {log.resource_type}
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 text-center">
                        <button
                          onClick={() => setSelectedLog(log)}
                          className="p-1.5 text-primary hover:bg-primary/10 rounded transition-colors"
                          title="View Details"
                        >
                          <Eye className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {total > 0 && (
            <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
              <div className="flex items-center gap-4">
                <span className="text-sm text-gray-600">
                  Showing {((currentPage - 1) * itemsPerPage) + 1} to {Math.min(currentPage * itemsPerPage, total)} of {total} logs
                </span>
                <select
                  value={itemsPerPage}
                  onChange={(e) => {
                    setItemsPerPage(Number(e.target.value));
                    setCurrentPage(1);
                  }}
                  className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                >
                  <option value={10}>10 per page</option>
                  <option value={25}>25 per page</option>
                  <option value={50}>50 per page</option>
                  <option value={100}>100 per page</option>
                </select>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                  className="p-2 rounded-lg border border-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>

                {getPageNumbers().map((page, index) => (
                  page === '...' ? (
                    <span key={`ellipsis-${index}`} className="px-2 text-gray-500">...</span>
                  ) : (
                    <button
                      key={page}
                      onClick={() => setCurrentPage(page)}
                      className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                        currentPage === page
                          ? 'bg-primary text-white'
                          : 'border border-gray-300 hover:bg-gray-50'
                      }`}
                    >
                      {page}
                    </button>
                  )
                ))}

                <button
                  onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                  disabled={currentPage === totalPages}
                  className="p-2 rounded-lg border border-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Log Details Modal */}
      {selectedLog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-xl">
            <div className="p-6 border-b border-gray-200 flex items-center justify-between sticky top-0 bg-white">
              <div className="flex items-center gap-3">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center ${getActionColor(selectedLog.action)}`}>
                  {getActionIcon(selectedLog.action)}
                </div>
                <h2 className="text-xl font-bold text-gray-900">Audit Log Details</h2>
              </div>
              <button
                onClick={() => setSelectedLog(null)}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="p-6 space-y-6">
              {/* Action Badge */}
              <div className="flex items-center gap-3">
                <span className={`inline-flex items-center gap-1.5 px-4 py-2 rounded-full text-sm font-medium ${getActionColor(selectedLog.action)}`}>
                  {getActionIcon(selectedLog.action)}
                  {formatAction(selectedLog.action)}
                </span>
                {selectedLog.resource_type && (
                  <span className="px-3 py-1.5 bg-gray-100 text-gray-700 rounded-full text-sm font-medium">
                    {selectedLog.resource_type}
                  </span>
                )}
              </div>

              {/* Details Grid */}
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-xs text-gray-500 uppercase font-medium mb-1">Timestamp</p>
                  <p className="text-sm font-medium text-gray-900">
                    {new Date(selectedLog.timestamp).toLocaleDateString()}
                  </p>
                  <p className="text-sm text-gray-600">
                    {new Date(selectedLog.timestamp).toLocaleTimeString()}
                  </p>
                </div>
                
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-xs text-gray-500 uppercase font-medium mb-1">User</p>
                  <div className="flex items-center gap-2">
                    <div className="w-6 h-6 bg-primary/10 rounded-full flex items-center justify-center">
                      <User className="w-3 h-3 text-primary" />
                    </div>
                    <p className="text-sm font-medium text-gray-900">{selectedLog.user_email || 'System'}</p>
                  </div>
                </div>

                {selectedLog.resource_id && (
                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="text-xs text-gray-500 uppercase font-medium mb-1">Resource ID</p>
                    <p className="text-sm font-mono text-gray-900 break-all">{selectedLog.resource_id}</p>
                  </div>
                )}

                {selectedLog.ip_address && (
                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="text-xs text-gray-500 uppercase font-medium mb-1">IP Address</p>
                    <p className="text-sm font-mono text-gray-900">{selectedLog.ip_address}</p>
                  </div>
                )}
              </div>

              {/* Full Details */}
              {getActionDetails(selectedLog.action) && (
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-xs text-gray-500 uppercase font-medium mb-2">Full Details</p>
                  <p className="text-sm text-gray-900 whitespace-pre-wrap break-words">
                    {getActionDetails(selectedLog.action)}
                  </p>
                </div>
              )}

              {/* Raw Action */}
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-xs text-gray-500 uppercase font-medium mb-2">Raw Action</p>
                <p className="text-sm font-mono text-gray-700 break-all">{selectedLog.action}</p>
              </div>
            </div>

            <div className="p-6 border-t border-gray-200 bg-gray-50">
              <button
                onClick={() => setSelectedLog(null)}
                className="w-full px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors font-medium"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AuditTrail;


