import { useState, useEffect } from 'react';
import { 
  FileText, 
  Calendar, 
  CheckCircle, 
  XCircle, 
  Clock, 
  Download, 
  Eye,
  ChevronLeft,
  ChevronRight,
  Play,
  Shield,
  Flag,
  AlertTriangle,
  BarChart3,
  ArrowLeft
} from 'lucide-react';
import { runsAPI, fraudAPI } from '../utils/api';
import { exportToCsv, getDateString } from '../utils/exportCsv';

const AuditReports = () => {
  const [viewMode, setViewMode] = useState('list'); // 'list' or 'detail'
  const [runs, setRuns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedRun, setSelectedRun] = useState(null);
  const [runDetails, setRunDetails] = useState(null);
  const [runClaims, setRunClaims] = useState([]);
  const [loadingDetails, setLoadingDetails] = useState(false);
  
  // Pagination
  const [page, setPage] = useState(1);
  const [perPage, setPerPage] = useState(10);

  useEffect(() => {
    fetchRuns();
  }, []);

  const fetchRuns = async () => {
    try {
      setLoading(true);
      const response = await runsAPI.getRuns({ limit: 100 });
      setRuns(response.data.runs || []);
    } catch (err) {
      console.error('Failed to fetch runs:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleViewRun = async (run) => {
    setSelectedRun(run);
    setViewMode('detail');
    setLoadingDetails(true);
    
    try {
      const [detailsRes, claimsRes] = await Promise.all([
        runsAPI.getRunDetails(run.id),
        fraudAPI.getFlagged({ run_id: run.id, limit: 10000 })
      ]);
      setRunDetails(detailsRes.data);
      setRunClaims(claimsRes.data.flagged_claims || []);
    } catch (err) {
      console.error('Failed to fetch run details:', err);
    } finally {
      setLoadingDetails(false);
    }
  };

  const handleBackToList = () => {
    setViewMode('list');
    setSelectedRun(null);
    setRunDetails(null);
    setRunClaims([]);
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

  const getSeverityColor = (severity) => {
    switch (severity?.toUpperCase()) {
      case 'FINANCIAL': return 'bg-red-100 text-red-700';
      case 'COMPLIANCE': return 'bg-amber-100 text-amber-700';
      case 'CLINICAL': return 'bg-purple-100 text-purple-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  // Pagination
  const totalPages = Math.ceil(runs.length / perPage);
  const startIndex = (page - 1) * perPage;
  const paginatedRuns = runs.slice(startIndex, startIndex + perPage);

  const exportRunReport = () => {
    if (!runDetails || !runClaims) return;
    
    const columns = [
      { key: 'claim_number', header: 'Claim Number' },
      { key: 'patient_id', header: 'Patient ID' },
      { key: 'drug_name', header: 'Drug Name' },
      { key: 'rule_code', header: 'Rule Code' },
      { key: 'rule_name', header: 'Rule Name' },
      { key: 'rule_version', header: 'Rule Version' },
      { key: 'severity', header: 'Severity' },
      { key: 'category', header: 'Category' },
      { key: 'flagged_at', header: 'Flagged At' },
      { key: 'reviewed', header: 'Reviewed' },
      { key: 'reviewer_notes', header: 'Review Notes' },
    ];
    
    const exportData = runClaims.map(claim => ({
      claim_number: claim.claim_number || '',
      patient_id: claim.patient_id || '',
      drug_name: claim.drug_name || '',
      rule_code: claim.rule_code || '',
      rule_name: claim.rule_name || '',
      rule_version: claim.rule_version || '',
      severity: claim.severity || '',
      category: claim.category || '',
      flagged_at: claim.flagged_at,
      reviewed: claim.reviewed ? 'Yes' : 'No',
      reviewer_notes: claim.reviewer_notes || '',
    }));
    
    const runName = selectedRun?.job_name || selectedRun?.id?.substring(0, 8);
    exportToCsv(exportData, columns, `audit_report_${runName}_${getDateString()}.csv`);
  };

  // Runs List View
  if (viewMode === 'list') {
    return (
      <div className="flex-1 overflow-auto bg-gray-50">
        <div className="bg-white border-b border-gray-200 px-8 py-6">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-primary/10 rounded-xl">
              <FileText className="w-6 h-6 text-primary" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Audit Reports</h1>
              <p className="text-sm text-gray-600 mt-1">
                View detailed reports for each audit run with full rule traceability
              </p>
            </div>
          </div>
        </div>

        <div className="p-8">
          <div className="bg-white rounded-xl shadow-sm overflow-hidden">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">
                Audit Run History ({runs.length} runs)
              </h2>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Run ID</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Dataset</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Run Date</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Claims</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rules</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Flags</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {loading ? (
                    <tr>
                      <td colSpan="8" className="px-6 py-12 text-center text-gray-500">
                        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary mb-2"></div>
                        <p>Loading audit runs...</p>
                      </td>
                    </tr>
                  ) : runs.length === 0 ? (
                    <tr>
                      <td colSpan="8" className="px-6 py-12 text-center text-gray-500">
                        <Play className="w-12 h-12 mx-auto mb-3 text-gray-400" />
                        <p className="font-medium">No audit runs found</p>
                        <p className="text-sm mt-1">Upload a CSV and run fraud detection to create audit runs</p>
                      </td>
                    </tr>
                  ) : (
                    paginatedRuns.map((run) => (
                      <tr key={run.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4">
                          <span className="font-mono text-sm text-gray-900">
                            #{run.id.substring(0, 8)}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-2">
                            <FileText className="w-4 h-4 text-gray-400" />
                            <span className="text-sm text-gray-900">
                              {run.job_name || 'All Claims'}
                            </span>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-600">
                          <div className="flex items-center gap-1">
                            <Calendar className="w-4 h-4 text-gray-400" />
                            {formatDate(run.run_date)}
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          {getStatusBadge(run.status)}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-900 font-medium">
                          {run.claims_processed}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-900 font-medium">
                          {run.rules_executed}
                        </td>
                        <td className="px-6 py-4">
                          <span className="inline-flex items-center gap-1 px-2 py-1 bg-red-50 text-red-700 rounded text-sm font-medium">
                            <Flag className="w-3.5 h-3.5" />
                            {run.flags_generated}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <button
                            onClick={() => handleViewRun(run)}
                            className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors text-sm"
                          >
                            <Eye className="w-4 h-4" />
                            View Report
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {runs.length > 0 && (
              <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
                <span className="text-sm text-gray-600">
                  Showing {startIndex + 1} to {Math.min(startIndex + perPage, runs.length)} of {runs.length} runs
                </span>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setPage(p => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="p-2 rounded-lg border border-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <ChevronLeft className="w-4 h-4" />
                  </button>
                  <span className="px-3 py-1 text-sm">
                    Page {page} of {totalPages || 1}
                  </span>
                  <button
                    onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                    disabled={page === totalPages || totalPages === 0}
                    className="p-2 rounded-lg border border-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <ChevronRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Run Detail View
  return (
    <div className="flex-1 overflow-auto bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-8 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={handleBackToList}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div className="flex items-center gap-3">
              <div className="p-3 bg-primary/10 rounded-xl">
                <BarChart3 className="w-6 h-6 text-primary" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  Audit Report: {selectedRun?.job_name || `Run #${selectedRun?.id?.substring(0, 8)}`}
                </h1>
                <p className="text-sm text-gray-600 mt-1">
                  {formatDate(selectedRun?.run_date)}
                </p>
              </div>
            </div>
          </div>
          <button
            onClick={exportRunReport}
            disabled={!runDetails}
            className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50"
          >
            <Download className="w-4 h-4" />
            Export Report (CSV)
          </button>
        </div>
      </div>

      {loadingDetails ? (
        <div className="p-8 flex items-center justify-center">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary mb-4"></div>
            <p className="text-gray-600">Loading report...</p>
          </div>
        </div>
      ) : (
        <div className="p-8 space-y-6">
          {/* Executive Summary */}
          <div className="bg-white rounded-xl shadow-sm overflow-hidden">
            <div className="bg-gradient-to-r from-primary/10 to-purple-100 px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-bold text-gray-900">Executive Summary</h2>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 divide-x divide-gray-200">
              <div className="p-6 text-center">
                <div className="flex items-center justify-center gap-2 text-gray-600 mb-2">
                  <FileText className="w-5 h-5" />
                  <span className="text-sm font-medium">Claims Processed</span>
                </div>
                <p className="text-3xl font-bold text-gray-900">
                  {runDetails?.run?.claims_processed || 0}
                </p>
              </div>
              <div className="p-6 text-center">
                <div className="flex items-center justify-center gap-2 text-gray-600 mb-2">
                  <Shield className="w-5 h-5" />
                  <span className="text-sm font-medium">Rules Applied</span>
                </div>
                <p className="text-3xl font-bold text-gray-900">
                  {runDetails?.run?.rules_executed || 0}
                </p>
              </div>
              <div className="p-6 text-center">
                <div className="flex items-center justify-center gap-2 text-gray-600 mb-2">
                  <Flag className="w-5 h-5" />
                  <span className="text-sm font-medium">Flags Generated</span>
                </div>
                <p className="text-3xl font-bold text-amber-600">
                  {runDetails?.run?.flags_generated || 0}
                </p>
              </div>
              <div className="p-6 text-center">
                <div className="flex items-center justify-center gap-2 text-gray-600 mb-2">
                  <AlertTriangle className="w-5 h-5" />
                  <span className="text-sm font-medium">Flag Rate</span>
                </div>
                <p className="text-3xl font-bold text-gray-900">
                  {runDetails?.run?.claims_processed > 0 
                    ? ((runDetails?.run?.flags_generated / runDetails?.run?.claims_processed) * 100).toFixed(1) + '%'
                    : '0%'}
                </p>
              </div>
            </div>
          </div>

          {/* Rules Applied with Versions */}
          <div className="bg-white rounded-xl shadow-sm overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                <Shield className="w-5 h-5 text-primary" />
                Rules Applied (with Versions)
              </h2>
              <p className="text-sm text-gray-600 mt-1">
                Exact rule versions used during this audit run for traceability
              </p>
            </div>
            <div className="p-6">
              {runDetails?.rules_applied?.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {runDetails.rules_applied.map((rule, idx) => (
                    <div
                      key={idx}
                      className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200"
                    >
                      <div>
                        <p className="font-medium text-gray-900">{rule.rule_code}</p>
                        <p className="text-sm text-gray-600 truncate max-w-[200px]">{rule.rule_name}</p>
                      </div>
                      <span className="px-3 py-1 bg-primary/10 text-primary rounded-full text-sm font-bold">
                        v{rule.version}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-center py-4">No rules applied in this run</p>
              )}
            </div>
          </div>

          {/* Breakdown by Severity and Category */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* By Severity */}
            <div className="bg-white rounded-xl shadow-sm overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-lg font-bold text-gray-900">Flags by Severity</h2>
              </div>
              <div className="p-6">
                {Object.entries(runDetails?.flags_by_severity || {}).length > 0 ? (
                  <div className="space-y-3">
                    {Object.entries(runDetails?.flags_by_severity || {}).map(([sev, count]) => (
                      <div key={sev} className="flex items-center justify-between">
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${getSeverityColor(sev)}`}>
                          {sev}
                        </span>
                        <span className="text-lg font-bold text-gray-900">{count}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-center">No flags</p>
                )}
              </div>
            </div>

            {/* By Category */}
            <div className="bg-white rounded-xl shadow-sm overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-lg font-bold text-gray-900">Flags by Category</h2>
              </div>
              <div className="p-6">
                {Object.entries(runDetails?.flags_by_category || {}).length > 0 ? (
                  <div className="space-y-3">
                    {Object.entries(runDetails?.flags_by_category || {}).map(([cat, count]) => (
                      <div key={cat} className="flex items-center justify-between">
                        <span className="text-sm text-gray-700 truncate max-w-[200px]">{cat}</span>
                        <span className="text-lg font-bold text-gray-900">{count}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-center">No flags</p>
                )}
              </div>
            </div>
          </div>

          {/* Rule Performance */}
          <div className="bg-white rounded-xl shadow-sm overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
              <div>
                <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                  <BarChart3 className="w-5 h-5 text-primary" />
                  Rule Performance
                </h2>
                <p className="text-sm text-gray-600 mt-1">
                  How each rule performed during this audit run
                </p>
              </div>
              {runDetails?.flags_by_rule?.length > 0 && (
                <button
                  onClick={() => {
                    const columns = [
                      { key: 'rule_code', header: 'Rule Code' },
                      { key: 'rule_name', header: 'Rule Name' },
                      { key: 'count', header: 'Flags Generated' },
                      { key: 'hit_rate', header: 'Hit Rate (%)' },
                    ];
                    const exportData = runDetails.flags_by_rule.map(rule => ({
                      rule_code: rule.rule_code,
                      rule_name: rule.rule_name,
                      count: rule.count,
                      hit_rate: runDetails?.run?.claims_processed > 0 
                        ? ((rule.count / runDetails.run.claims_processed) * 100).toFixed(2)
                        : '0',
                    }));
                    const runName = selectedRun?.job_name || selectedRun?.id?.substring(0, 8);
                    exportToCsv(exportData, columns, `rule_performance_${runName}_${getDateString()}.csv`);
                  }}
                  className="flex items-center gap-2 px-3 py-1.5 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                >
                  <Download className="w-4 h-4" />
                  Export
                </button>
              )}
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rule Code</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rule Name</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Flags Generated</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Hit Rate</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {(runDetails?.flags_by_rule || []).length === 0 ? (
                    <tr>
                      <td colSpan="4" className="px-6 py-8 text-center text-gray-500">
                        No rule performance data
                      </td>
                    </tr>
                  ) : (
                    (runDetails?.flags_by_rule || [])
                      .sort((a, b) => b.count - a.count)
                      .map((rule, idx) => (
                        <tr key={idx} className="hover:bg-gray-50">
                          <td className="px-6 py-4">
                            <span className="font-mono text-sm font-medium text-primary">
                              {rule.rule_code}
                            </span>
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-900">
                            {rule.rule_name}
                          </td>
                          <td className="px-6 py-4">
                            <span className="inline-flex items-center gap-1 px-2 py-1 bg-red-50 text-red-700 rounded text-sm font-medium">
                              <Flag className="w-3.5 h-3.5" />
                              {rule.count}
                            </span>
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-600">
                            {runDetails?.run?.claims_processed > 0 
                              ? ((rule.count / runDetails.run.claims_processed) * 100).toFixed(2) + '%'
                              : '0%'}
                          </td>
                        </tr>
                      ))
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* Flagged Claims for this Run */}
          <div className="bg-white rounded-xl shadow-sm overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-bold text-gray-900">
                Flagged Claims ({runClaims.length})
              </h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Claim #</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Patient</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Drug</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rule</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Version</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Severity</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {runClaims.length === 0 ? (
                    <tr>
                      <td colSpan="7" className="px-6 py-8 text-center text-gray-500">
                        No flagged claims in this run
                      </td>
                    </tr>
                  ) : (
                    runClaims.slice(0, 50).map((claim) => (
                      <tr key={claim.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 text-sm font-medium text-gray-900">
                          {claim.claim_number}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-600">
                          {claim.patient_id || '-'}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-600">
                          {claim.drug_name || '-'}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-600">
                          <span className="font-mono">{claim.rule_code}</span>
                        </td>
                        <td className="px-6 py-4">
                          <span className="px-2 py-1 bg-primary/10 text-primary rounded text-xs font-bold">
                            v{claim.rule_version}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <span className={`px-2 py-1 rounded text-xs font-medium ${getSeverityColor(claim.severity)}`}>
                            {claim.severity || 'N/A'}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          {claim.reviewed ? (
                            <span className="flex items-center gap-1 text-sm text-green-600">
                              <CheckCircle className="w-4 h-4" />
                              Reviewed
                            </span>
                          ) : (
                            <span className="flex items-center gap-1 text-sm text-amber-600">
                              <Clock className="w-4 h-4" />
                              Pending
                            </span>
                          )}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
            {runClaims.length > 50 && (
              <div className="px-6 py-4 border-t border-gray-200 text-center text-sm text-gray-600">
                Showing first 50 of {runClaims.length} flagged claims. Export CSV for full list.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default AuditReports;

