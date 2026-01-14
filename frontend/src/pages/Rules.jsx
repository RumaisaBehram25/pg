import { useState, useEffect } from 'react';
import { Plus, Eye, Edit, Trash2, Power, Upload, Shield, Search, History, ChevronLeft, ChevronRight, Download } from 'lucide-react';
import { exportToCsv, getDateString } from '../utils/exportCsv';
import { rulesAPI, usersAPI } from '../utils/api';
import CreateRule from './CreateRule';

const Rules = () => {
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedRule, setSelectedRule] = useState(null);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showVersionsModal, setShowVersionsModal] = useState(false);
  const [ruleVersions, setRuleVersions] = useState([]);
  const [bulkUploadFile, setBulkUploadFile] = useState(null);
  const [notification, setNotification] = useState({ show: false, message: '', type: '' });
  const [currentUser, setCurrentUser] = useState(null);
  const [showAdminOnlyModal, setShowAdminOnlyModal] = useState(false);
  
  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(10);
  
  // Status filter
  const [statusFilter, setStatusFilter] = useState('all'); // 'all', 'active', 'inactive'

  useEffect(() => {
    fetchRules();
    fetchCurrentUser();
  }, []);

  const fetchCurrentUser = async () => {
    try {
      const response = await usersAPI.getCurrentUser();
      console.log('Current user:', response.data);
      setCurrentUser(response.data);
    } catch (err) {
      console.error('Failed to fetch current user:', err);
    }
  };

  const isAdmin = currentUser?.role === 'ADMIN';

  const checkAdminAccess = () => {
    // If user hasn't loaded yet, allow the action and let backend handle auth
    if (!currentUser) {
      console.log('User not loaded yet, allowing action');
      return true;
    }
    
    console.log('Checking admin access. Current user role:', currentUser?.role, 'Is admin:', isAdmin);
    
    if (!isAdmin) {
      setShowAdminOnlyModal(true);
      return false;
    }
    return true;
  };

  const fetchRules = async () => {
    try {
      setLoading(true);
      const response = await rulesAPI.getRules();
      setRules(response.data.rules || []);
    } catch (err) {
      console.error('Failed to fetch rules:', err);
    } finally {
      setLoading(false);
    }
  };

  const showNotification = (message, type = 'success') => {
    setNotification({ show: true, message, type });
    setTimeout(() => setNotification({ show: false, message: '', type: '' }), 3000);
  };

  const handleToggleRule = async (ruleId, currentStatus) => {
    if (!checkAdminAccess()) return;
    
    try {
      await rulesAPI.toggleRule(ruleId, !currentStatus);
      await fetchRules();
      showNotification(`Rule ${!currentStatus ? 'activated' : 'deactivated'} successfully`, 'success');
    } catch (err) {
      console.error('Toggle error:', err);
      showNotification(err.response?.data?.detail || 'Failed to toggle rule', 'error');
    }
  };

  const [deleteConfirm, setDeleteConfirm] = useState({ show: false, ruleId: null, ruleName: '' });

  const handleDeleteRule = async (ruleId, ruleName) => {
    if (!checkAdminAccess()) return;
    setDeleteConfirm({ show: true, ruleId, ruleName });
  };

  const confirmDelete = async () => {
    try {
      await rulesAPI.deleteRule(deleteConfirm.ruleId);
      setDeleteConfirm({ show: false, ruleId: null, ruleName: '' });
      fetchRules();
      showNotification('Rule deleted successfully', 'success');
    } catch (err) {
      showNotification(err.response?.data?.detail || 'Failed to delete rule', 'error');
      setDeleteConfirm({ show: false, ruleId: null, ruleName: '' });
    }
  };

  const handleViewDetails = async (ruleId) => {
    try {
      const response = await rulesAPI.getRule(ruleId);
      setSelectedRule(response.data);
      setShowDetailsModal(true);
    } catch (err) {
      showNotification('Failed to load rule details', 'error');
    }
  };

  const handleEditRule = async (ruleId) => {
    if (!checkAdminAccess()) return;
    
    try {
      const response = await rulesAPI.getRule(ruleId);
      setSelectedRule(response.data);
      setShowEditModal(true);
    } catch (err) {
      showNotification('Failed to load rule details', 'error');
    }
  };

  const handleViewVersions = async (ruleId) => {
    try {
      // Get the current rule details first
      const ruleResponse = await rulesAPI.getRule(ruleId);
      const currentRule = ruleResponse.data;
      
      // Get version history
      const versionsResponse = await rulesAPI.getRuleVersions(ruleId);
      
      // Store both for the modal
      setSelectedRule(currentRule);
      setRuleVersions(versionsResponse.data);
      setShowVersionsModal(true);
    } catch (err) {
      showNotification('Failed to load version history', 'error');
    }
  };

  const handleBulkUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (!checkAdminAccess()) {
      e.target.value = '';
      return;
    }

    if (!file.name.endsWith('.json')) {
      showNotification('Please upload a JSON file', 'error');
      e.target.value = '';
      return;
    }

    try {
      const result = await rulesAPI.bulkUploadRules(file);
      const created = result.data?.created || 0;
      const failed = result.data?.failed || 0;
      showNotification(`Successfully uploaded ${created} rule(s)${failed > 0 ? `, ${failed} failed` : ''}`, 'success');
      fetchRules();
      e.target.value = '';
    } catch (err) {
      showNotification(err.response?.data?.detail || 'Failed to upload rules', 'error');
      e.target.value = '';
    }
  };

  const handleCreateRuleClick = () => {
    if (!checkAdminAccess()) return;
    setShowCreateModal(true);
  };

  const getSeverityColor = (severity) => {
    switch(severity?.toUpperCase()) {
      case 'FINANCIAL': return 'bg-red-100 text-red-700';
      case 'COMPLIANCE': return 'bg-amber-100 text-amber-700';
      // Legacy support
      case 'HIGH': return 'bg-red-100 text-red-700';
      case 'MEDIUM': return 'bg-amber-100 text-amber-700';
      case 'LOW': return 'bg-yellow-100 text-yellow-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  const getCategoryColor = (category) => {
    const colors = {
      'DUPLICATE_BILLING': 'bg-orange-100 text-orange-700',
      'UTILIZATION': 'bg-purple-100 text-purple-700',
      'QTY_DAYS_SUPPLY': 'bg-green-100 text-green-700',
      'PRICING': 'bg-blue-100 text-blue-700',
      'ELIGIBILITY_NETWORK': 'bg-cyan-100 text-cyan-700',
      'DRUG_RESTRICTIONS': 'bg-pink-100 text-pink-700',
      'PRESCRIBER_INTEGRITY': 'bg-indigo-100 text-indigo-700',
      'DATE_INTEGRITY': 'bg-teal-100 text-teal-700',
      'DOCUMENTATION': 'bg-violet-100 text-violet-700',
      'EXTENDED_VALIDATION': 'bg-fuchsia-100 text-fuchsia-700',
      'OTHER': 'bg-gray-100 text-gray-700',
      // Legacy support
      'pricing': 'bg-blue-100 text-blue-700',
      'quantity': 'bg-green-100 text-green-700',
      'frequency': 'bg-purple-100 text-purple-700',
      'drug_interaction': 'bg-pink-100 text-pink-700',
      'duplicate': 'bg-orange-100 text-orange-700',
      'other': 'bg-gray-100 text-gray-700'
    };
    return colors[category] || colors['OTHER'];
  };

  const formatCategoryName = (category) => {
    if (!category) return 'Other';
    return category.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
    ).join(' ');
  };

  const formatSeverityName = (severity) => {
    if (!severity) return 'Unknown';
    return severity.charAt(0).toUpperCase() + severity.slice(1).toLowerCase();
  };

  const filteredRules = rules.filter(rule => {
    // Text search filter
    const matchesSearch = rule.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      rule.description?.toLowerCase().includes(searchTerm.toLowerCase());
    
    // Status filter
    const matchesStatus = statusFilter === 'all' || 
      (statusFilter === 'active' && rule.is_active) ||
      (statusFilter === 'inactive' && !rule.is_active);
    
    return matchesSearch && matchesStatus;
  });

  // Reset to first page when search or filter changes
  useEffect(() => {
    setCurrentPage(1);
  }, [searchTerm, statusFilter]);

  // Pagination calculations
  const totalPages = Math.ceil(filteredRules.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const paginatedRules = filteredRules.slice(startIndex, endIndex);

  const goToPage = (page) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page);
    }
  };

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
            <h1 className="text-2xl font-bold text-gray-900">Fraud Detection Rules</h1>
            <p className="text-sm text-gray-600 mt-1">Manage and monitor your audit rules</p>
          </div>
          <div className="flex gap-3">
            {rules.length > 0 && (
              <button
                onClick={() => {
                  const columns = [
                    { key: 'rule_code', header: 'Rule Code' },
                    { key: 'name', header: 'Name' },
                    { key: 'description', header: 'Description' },
                    { key: 'category', header: 'Category' },
                    { key: 'severity', header: 'Severity' },
                    { key: 'logic_type', header: 'Logic Type' },
                    { key: 'is_active', header: 'Active' },
                    { key: 'version', header: 'Version' },
                  ];
                  const exportData = rules.map(rule => ({
                    ...rule,
                    is_active: rule.is_active ? 'Yes' : 'No',
                  }));
                  exportToCsv(exportData, columns, `rules_${getDateString()}.csv`);
                }}
                className="flex items-center gap-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
              >
                <Download className="w-4 h-4" />
                Export
              </button>
            )}
            <label className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors cursor-pointer">
              <Upload className="w-4 h-4" />
              Bulk Upload
              <input
                type="file"
                accept=".json"
                onChange={handleBulkUpload}
                className="hidden"
              />
            </label>
            <button
              onClick={handleCreateRuleClick}
              className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-hover transition-colors"
            >
              <Plus className="w-4 h-4" />
              Create Rule
            </button>
          </div>
        </div>
      </div>

      <div className="p-8">
        {/* Search and Filters */}
        <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search Input */}
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search rules..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
            
            {/* Status Filter */}
            <div className="flex items-center gap-2">
              <label className="text-sm font-medium text-gray-700">Status:</label>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              >
                <option value="all">All Rules</option>
                <option value="active">Active Only</option>
                <option value="inactive">Inactive Only</option>
              </select>
            </div>
          </div>
        </div>

        {/* Rules Table */}
        <div className="bg-white rounded-xl shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rule Name</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Category</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Severity</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Version</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {loading ? (
                  <tr>
                    <td colSpan="6" className="px-6 py-12 text-center text-gray-500">
                      Loading rules...
                    </td>
                  </tr>
                ) : filteredRules.length === 0 ? (
                  <tr>
                    <td colSpan="6" className="px-6 py-12 text-center">
                      <Shield className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                      <p className="text-gray-500">No rules found. Create your first rule to get started.</p>
                    </td>
                  </tr>
                ) : (
                  paginatedRules.map((rule) => (
                    <tr key={rule.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <div>
                          <div className="flex items-center gap-2">
                            {rule.rule_code && (
                              <span className="text-xs font-mono bg-gray-100 text-gray-600 px-2 py-0.5 rounded">
                                {rule.rule_code}
                              </span>
                            )}
                            <span className="font-medium text-gray-900">{rule.name}</span>
                          </div>
                          <div className="text-sm text-gray-500 mt-1 line-clamp-1">
                            {rule.description || 'No description'}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getCategoryColor(rule.category)}`}>
                          {formatCategoryName(rule.category)}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getSeverityColor(rule.severity)}`}>
                          {formatSeverityName(rule.severity)}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-900">v{rule.version}</div>
                        <div className="text-xs text-gray-500">
                          {new Date(rule.updated_at).toLocaleDateString()}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <button
                          onClick={() => handleToggleRule(rule.id, rule.is_active)}
                          className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                            rule.is_active 
                              ? 'bg-green-100 text-green-700 hover:bg-green-200' 
                              : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                          }`}
                        >
                          <Power className="w-3.5 h-3.5" />
                          {rule.is_active ? 'Active' : 'Inactive'}
                        </button>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex gap-2">
                          <button
                            onClick={() => handleViewDetails(rule.id)}
                            className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
                            title="View Details"
                          >
                            <Eye className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleEditRule(rule.id)}
                            className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                            title="Edit Rule"
                          >
                            <Edit className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleViewVersions(rule.id)}
                            className="p-2 text-purple-600 hover:bg-purple-50 rounded-lg transition-colors"
                            title="Version History"
                          >
                            <History className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleDeleteRule(rule.id, rule.name)}
                            className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                            title="Delete Rule"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {filteredRules.length > 0 && (
            <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
              <div className="flex items-center gap-4">
                <span className="text-sm text-gray-600">
                  Showing {startIndex + 1} to {Math.min(endIndex, filteredRules.length)} of {filteredRules.length} rules
                </span>
                <select
                  value={itemsPerPage}
                  onChange={(e) => {
                    setItemsPerPage(Number(e.target.value));
                    setCurrentPage(1);
                  }}
                  className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                >
                  <option value={5}>5 per page</option>
                  <option value={10}>10 per page</option>
                  <option value={25}>25 per page</option>
                  <option value={50}>50 per page</option>
                </select>
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => goToPage(currentPage - 1)}
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
                      onClick={() => goToPage(page)}
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
                  onClick={() => goToPage(currentPage + 1)}
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

      {/* Create Rule Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <CreateRule 
              onClose={() => {
                setShowCreateModal(false);
                fetchRules();
              }}
            />
          </div>
        </div>
      )}

      {/* Rule Details Modal */}
      {showDetailsModal && selectedRule && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200 sticky top-0 bg-white flex items-center justify-between">
              <h2 className="text-xl font-bold text-gray-900">Rule Details</h2>
              <button
                onClick={() => {
                  setShowDetailsModal(false);
                  setSelectedRule(null);
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
            
            <div className="p-6 space-y-4">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{selectedRule.name}</h3>
                <p className="text-gray-600">{selectedRule.description}</p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Category</p>
                  <span className={`inline-block px-3 py-1 text-xs font-medium rounded-full ${getCategoryColor(selectedRule.category)}`}>
                    {selectedRule.category}
                  </span>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Severity</p>
                  <span className={`inline-block px-3 py-1 text-xs font-medium rounded-full ${getSeverityColor(selectedRule.severity)}`}>
                    {selectedRule.severity}
                  </span>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Status</p>
                  <span className={`inline-block px-3 py-1 text-xs font-medium rounded-full ${
                    selectedRule.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
                  }`}>
                    {selectedRule.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Version</p>
                  <p className="font-medium">{selectedRule.version}</p>
                </div>
              </div>

              {selectedRule.rule_definition && (
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-2">Rule Definition</p>
                  <pre className="bg-gray-50 p-4 rounded-lg text-xs overflow-x-auto">
                    {JSON.stringify(selectedRule.rule_definition, null, 2)}
                  </pre>
                </div>
              )}

              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-gray-600">Created</p>
                  <p className="font-medium">{new Date(selectedRule.created_at).toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-gray-600">Last Updated</p>
                  <p className="font-medium">{new Date(selectedRule.updated_at).toLocaleString()}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Edit Rule Modal */}
      {showEditModal && selectedRule && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <CreateRule 
              editMode={true}
              existingRule={selectedRule}
              onClose={() => {
                setShowEditModal(false);
                setSelectedRule(null);
                fetchRules();
              }}
            />
          </div>
        </div>
      )}

      {/* Version History Modal */}
      {showVersionsModal && selectedRule && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200 sticky top-0 bg-white flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold text-gray-900">Version History</h2>
                <p className="text-sm text-gray-600 mt-1">{selectedRule.name}</p>
              </div>
              <button
                onClick={() => {
                  setShowVersionsModal(false);
                  setRuleVersions([]);
                  setSelectedRule(null);
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
            
            <div className="p-6">
              {ruleVersions.length === 0 ? (
                <p className="text-center text-gray-500 py-8">No version history available</p>
              ) : (
                <div className="space-y-4">
                  {ruleVersions.map((version, index) => {
                    // Current version (index 0) should show the rule's current active status
                    const isCurrentVersion = index === 0;
                    const displayStatus = isCurrentVersion ? selectedRule.is_active : false;
                    
                    return (
                      <div key={version.id || index} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center gap-2">
                            <span className="font-semibold text-gray-900">Version {version.version}</span>
                            {isCurrentVersion && (
                              <span className="px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded-full font-medium">
                                Current
                              </span>
                            )}
                            <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                              displayStatus ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
                            }`}>
                              {isCurrentVersion ? (displayStatus ? 'Active' : 'Inactive') : 'Historical'}
                            </span>
                          </div>
                          <span className="text-sm text-gray-500">
                            {new Date(version.created_at).toLocaleString()}
                          </span>
                        </div>
                        
                        {version.rule_definition && (
                          <div className="bg-gray-50 rounded-lg p-3 mt-2">
                            <p className="text-xs font-medium text-gray-700 mb-1">Rule Definition:</p>
                            <pre className="text-xs text-gray-600 overflow-x-auto">
                              {JSON.stringify(version.rule_definition, null, 2)}
                            </pre>
                          </div>
                        )}
                        
                        {version.created_by && (
                          <p className="text-xs text-gray-500 mt-2">
                            Modified by: {version.created_by}
                          </p>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {deleteConfirm.show && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl max-w-md w-full p-6 shadow-2xl">
            <div className="flex items-center justify-center w-12 h-12 mx-auto mb-4 bg-red-100 rounded-full">
              <Trash2 className="w-6 h-6 text-red-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 text-center mb-2">Delete Rule</h3>
            <p className="text-gray-600 text-center mb-6">
              Are you sure you want to delete "<span className="font-semibold">{deleteConfirm.ruleName}</span>"? This action cannot be undone.
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => setDeleteConfirm({ show: false, ruleId: null, ruleName: '' })}
                className="flex-1 px-4 py-2.5 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors font-medium"
              >
                Cancel
              </button>
              <button
                onClick={confirmDelete}
                className="flex-1 px-4 py-2.5 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Notification Toast */}
      {notification.show && (
        <div className="fixed top-4 right-4 z-50 animate-slide-in">
          <div className={`rounded-xl shadow-lg px-6 py-4 flex items-center gap-3 min-w-[320px] ${
            notification.type === 'success' 
              ? 'bg-green-50 border border-green-200' 
              : 'bg-red-50 border border-red-200'
          }`}>
            <div className={`flex-shrink-0 w-5 h-5 rounded-full flex items-center justify-center ${
              notification.type === 'success' ? 'bg-green-500' : 'bg-red-500'
            }`}>
              {notification.type === 'success' ? (
                <svg className="w-3 h-3 text-white" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                  <path d="M5 13l4 4L19 7"></path>
                </svg>
              ) : (
                <span className="text-white text-xs font-bold">!</span>
              )}
            </div>
            <p className={`font-medium ${
              notification.type === 'success' ? 'text-green-800' : 'text-red-800'
            }`}>
              {notification.message}
            </p>
          </div>
        </div>
      )}

      {/* Admin Only Modal */}
      {showAdminOnlyModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl max-w-md w-full p-6 shadow-2xl">
            <div className="flex items-center justify-center w-12 h-12 mx-auto mb-4 bg-amber-100 rounded-full">
              <Shield className="w-6 h-6 text-amber-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 text-center mb-2">Admin Access Required</h3>
            <p className="text-gray-600 text-center mb-6">
              This action requires administrator privileges. Please contact your system administrator for access.
            </p>
            <button
              onClick={() => setShowAdminOnlyModal(false)}
              className="w-full px-4 py-2.5 bg-primary text-white rounded-lg hover:bg-primary-hover transition-colors font-medium"
            >
              OK
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Rules;

