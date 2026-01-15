import { useState, useEffect } from 'react';
import { AlertTriangle, Eye, CheckCircle, Search, ChevronLeft, ChevronRight, FileText, ArrowLeft, Flag, RefreshCw, Download, Play } from 'lucide-react';
import { fraudAPI, claimsAPI } from '../utils/api';
import { exportToCsv, getDateString } from '../utils/exportCsv';

const FlaggedClaims = () => {
  // View mode: 'jobs' or 'claims'
  const [viewMode, setViewMode] = useState('jobs');
  const [selectedJob, setSelectedJob] = useState(null);
  
  // Jobs data
  const [jobs, setJobs] = useState([]);
  const [loadingJobs, setLoadingJobs] = useState(true);
  
  // Claims data
  const [flaggedClaims, setFlaggedClaims] = useState([]);
  const [loadingClaims, setLoadingClaims] = useState(false);
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedClaim, setSelectedClaim] = useState(null);
  
  // Overall stats
  const [stats, setStats] = useState({ total: 0, reviewed: 0, unreviewed: 0 });
  
  // Pagination for jobs
  const [jobsPage, setJobsPage] = useState(1);
  const [jobsPerPage, setJobsPerPage] = useState(10);
  
  // Pagination for claims
  const [claimsPage, setClaimsPage] = useState(1);
  const [claimsPerPage, setClaimsPerPage] = useState(10);

  useEffect(() => {
    fetchJobs();
    fetchOverallStats();
  }, []);

  const fetchJobs = async () => {
    try {
      setLoadingJobs(true);
      const response = await claimsAPI.getJobs();
      // Filter jobs that have flags
      const jobsWithFlags = response.data.jobs.filter(job => job.fraud_flags_count > 0);
      setJobs(jobsWithFlags);
    } catch (err) {
      console.error('Failed to fetch jobs:', err);
    } finally {
      setLoadingJobs(false);
    }
  };

  const fetchOverallStats = async () => {
    try {
      const response = await fraudAPI.getStats();
      setStats({
        total: response.data.total_flags || 0,
        reviewed: response.data.total_reviewed || 0,
        unreviewed: response.data.total_unreviewed || 0
      });
    } catch (err) {
      console.error('Failed to fetch stats:', err);
    }
  };

  const fetchFlaggedClaimsForJob = async (jobId) => {
    try {
      setLoadingClaims(true);
      const params = { job_id: jobId, limit: 10000 };
      if (filter === 'reviewed') params.reviewed = true;
      if (filter === 'unreviewed') params.reviewed = false;

      const response = await fraudAPI.getFlagged(params);
      setFlaggedClaims(response.data.flagged_claims);
    } catch (err) {
      console.error('Failed to fetch flagged claims:', err);
    } finally {
      setLoadingClaims(false);
    }
  };

  const handleViewJobFlags = (job) => {
    setSelectedJob(job);
    setViewMode('claims');
    setClaimsPage(1);
    setFilter('all');
    setSearchTerm('');
    fetchFlaggedClaimsForJob(job.job_id);
  };

  const handleBackToJobs = () => {
    setViewMode('jobs');
    setSelectedJob(null);
    setFlaggedClaims([]);
  };

  const handleReview = async (flagId, notes) => {
    try {
      await fraudAPI.reviewFlag(flagId, { reviewer_notes: notes });
      if (selectedJob) {
        fetchFlaggedClaimsForJob(selectedJob.job_id);
      }
      fetchOverallStats();
      setSelectedClaim(null);
    } catch (err) {
      console.error('Failed to review claim:', err);
    }
  };

  // Re-fetch when filter changes
  useEffect(() => {
    if (viewMode === 'claims' && selectedJob) {
      fetchFlaggedClaimsForJob(selectedJob.job_id);
    }
  }, [filter]);

  const getSeverityColor = (severity) => {
    switch (severity?.toLowerCase()) {
      case 'high': case 'financial': return 'bg-red-100 text-red-700';
      case 'medium': case 'compliance': return 'bg-amber-100 text-amber-700';
      case 'low': return 'bg-yellow-100 text-yellow-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  const filteredClaims = flaggedClaims.filter(claim =>
    claim.claim_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    claim.rule_name?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Reset claims page when search changes
  useEffect(() => {
    setClaimsPage(1);
  }, [searchTerm, filter]);

  // Pagination for jobs
  const totalJobsPages = Math.ceil(jobs.length / jobsPerPage);
  const jobsStartIndex = (jobsPage - 1) * jobsPerPage;
  const paginatedJobs = jobs.slice(jobsStartIndex, jobsStartIndex + jobsPerPage);

  // Pagination for claims
  const totalClaimsPages = Math.ceil(filteredClaims.length / claimsPerPage);
  const claimsStartIndex = (claimsPage - 1) * claimsPerPage;
  const paginatedClaims = filteredClaims.slice(claimsStartIndex, claimsStartIndex + claimsPerPage);

  const getPageNumbers = (currentPage, totalPages) => {
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

  const PaginationControls = ({ currentPage, totalPages, totalItems, itemsPerPage, setPage, setPerPage, itemName }) => {
    if (totalItems === 0) return null;
    const startIdx = (currentPage - 1) * itemsPerPage;
    const endIdx = Math.min(startIdx + itemsPerPage, totalItems);
    
    return (
      <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-600">
            Showing {startIdx + 1} to {endIdx} of {totalItems} {itemName}
          </span>
          <select
            value={itemsPerPage}
            onChange={(e) => {
              setPerPage(Number(e.target.value));
              setPage(1);
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
            onClick={() => setPage(currentPage - 1)}
            disabled={currentPage === 1}
            className="p-2 rounded-lg border border-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>

          {getPageNumbers(currentPage, totalPages).map((page, index) => (
            page === '...' ? (
              <span key={`ellipsis-${index}`} className="px-2 text-gray-500">...</span>
            ) : (
              <button
                key={page}
                onClick={() => setPage(page)}
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
            onClick={() => setPage(currentPage + 1)}
            disabled={currentPage === totalPages}
            className="p-2 rounded-lg border border-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    );
  };

  return (
    <div className="flex-1 overflow-auto bg-gray-50">
      <div className="bg-white border-b border-gray-200 px-8 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            {viewMode === 'claims' && (
              <button
                onClick={handleBackToJobs}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <ArrowLeft className="w-5 h-5" />
              </button>
            )}
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                {viewMode === 'jobs' ? 'Flagged Claims' : `Flags for ${selectedJob?.file_name}`}
              </h1>
              <p className="text-sm text-gray-600 mt-1">
                {viewMode === 'jobs' 
                  ? 'Select a job to review its flagged claims' 
                  : `${flaggedClaims.length} fraud flags in this job`}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            {viewMode === 'claims' && flaggedClaims.length > 0 && (
              <button
                onClick={() => {
                  const columns = [
                    { key: 'claim_number', header: 'Claim Number' },
                    { key: 'patient_id', header: 'Patient ID' },
                    { key: 'drug_name', header: 'Drug Name' },
                    { key: 'rule_code', header: 'Rule Code' },
                    { key: 'rule_name', header: 'Rule Name' },
                    { key: 'severity', header: 'Severity' },
                    { key: 'category', header: 'Category' },
                    { key: 'flagged_at', header: 'Flagged At' },
                    { key: 'reviewed', header: 'Reviewed' },
                    { key: 'reviewer_notes', header: 'Review Notes' },
                  ];
                  const exportData = flaggedClaims.map(claim => ({
                    claim_number: claim.claim_number || '',
                    patient_id: claim.patient_id || '',
                    drug_name: claim.drug_name || '',
                    rule_code: claim.rule_code || '',
                    rule_name: claim.rule_name || '',
                    severity: claim.severity || '',
                    category: claim.category || '',
                    flagged_at: claim.flagged_at,
                    reviewed: claim.reviewed ? 'Yes' : 'No',
                    reviewer_notes: claim.reviewer_notes || '',
                  }));
                  exportToCsv(exportData, columns, `flagged_claims_${selectedJob?.file_name || 'export'}_${getDateString()}.csv`);
                }}
                className="px-4 py-2 text-sm text-primary hover:bg-primary/10 rounded-lg transition-colors"
              >
                Export CSV
              </button>
            )}
            <button
              onClick={() => {
                fetchJobs();
                fetchOverallStats();
              }}
              className="px-4 py-2 text-sm text-primary hover:bg-primary/10 rounded-lg transition-colors"
            >
              Refresh
            </button>
          </div>
        </div>
      </div>

      <div className="p-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <div className="bg-white rounded-xl shadow-sm p-6">
            <p className="text-sm text-gray-600 mb-1">
              {viewMode === 'claims' ? 'Job Total Flags' : 'Total Flags'}
            </p>
            <p className="text-3xl font-bold text-gray-900">
              {viewMode === 'claims' ? flaggedClaims.length : stats.total}
            </p>
            <p className="text-xs text-gray-500 mt-1">
              {viewMode === 'claims' ? 'Flags in this job' : 'All fraud flags'}
            </p>
          </div>
          <div className="bg-white rounded-xl shadow-sm p-6">
            <p className="text-sm text-gray-600 mb-1">Unreviewed Flags</p>
            <p className="text-3xl font-bold text-amber-600">
              {viewMode === 'claims' 
                ? flaggedClaims.filter(c => !c.reviewed).length 
                : stats.unreviewed}
            </p>
            <p className="text-xs text-gray-500 mt-1">Pending review</p>
          </div>
          <div className="bg-white rounded-xl shadow-sm p-6">
            <p className="text-sm text-gray-600 mb-1">Reviewed Flags</p>
            <p className="text-3xl font-bold text-green-600">
              {viewMode === 'claims' 
                ? flaggedClaims.filter(c => c.reviewed).length 
                : stats.reviewed}
            </p>
            <p className="text-xs text-gray-500 mt-1">Completed</p>
          </div>
        </div>

        {viewMode === 'jobs' ? (
          /* Jobs List View */
          <div className="bg-white rounded-xl shadow-sm overflow-hidden">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Jobs with Flagged Claims ({jobs.length})</h2>
            </div>
            
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Job ID</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">File Name</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total Claims</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Flagged</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {loadingJobs ? (
                    <tr>
                      <td colSpan="6" className="px-6 py-12 text-center text-gray-500">
                        Loading jobs...
                      </td>
                    </tr>
                  ) : jobs.length === 0 ? (
                    <tr>
                      <td colSpan="6" className="px-6 py-12 text-center text-gray-500">
                        <Flag className="w-12 h-12 mx-auto mb-3 text-gray-400" />
                        No jobs with flagged claims found
                      </td>
                    </tr>
                  ) : (
                    paginatedJobs.map((job) => (
                      <tr key={job.job_id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 text-sm font-mono text-gray-900">
                          #{job.job_id.substring(0, 8)}
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-2">
                            <FileText className="w-4 h-4 text-gray-400" />
                            <span className="text-sm text-gray-900">{job.file_name}</span>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-600">
                          {job.success_count}/{job.total_rows}
                        </td>
                        <td className="px-6 py-4">
                          <span className="inline-flex items-center gap-1 px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm font-medium">
                            <AlertTriangle className="w-3.5 h-3.5" />
                            {job.fraud_flags_count}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-600">
                          {new Date(job.created_at).toLocaleDateString()}
                        </td>
                        <td className="px-6 py-4">
                          <button
                            onClick={() => handleViewJobFlags(job)}
                            className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-hover transition-colors text-sm"
                          >
                            <Eye className="w-4 h-4" />
                            View Flags
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>

            <PaginationControls
              currentPage={jobsPage}
              totalPages={totalJobsPages}
              totalItems={jobs.length}
              itemsPerPage={jobsPerPage}
              setPage={setJobsPage}
              setPerPage={setJobsPerPage}
              itemName="jobs"
            />
          </div>
        ) : (
          /* Claims View for Selected Job */
          <>
            {/* Filters and Search */}
            <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
              <div className="flex flex-col md:flex-row gap-4 items-center justify-between">
                <div className="flex gap-2">
                  <button
                    onClick={() => setFilter('all')}
                    className={`px-4 py-2 rounded-lg transition-colors ${
                      filter === 'all'
                        ? 'bg-primary text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    All
                  </button>
                  <button
                    onClick={() => setFilter('unreviewed')}
                    className={`px-4 py-2 rounded-lg transition-colors ${
                      filter === 'unreviewed'
                        ? 'bg-primary text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    Unreviewed
                  </button>
                  <button
                    onClick={() => setFilter('reviewed')}
                    className={`px-4 py-2 rounded-lg transition-colors ${
                      filter === 'reviewed'
                        ? 'bg-primary text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    Reviewed
                  </button>
                </div>

                <div className="relative w-full md:w-64">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search claims..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>
              </div>
            </div>

            {/* Flagged Claims Table */}
            <div className="bg-white rounded-xl shadow-sm overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 border-b border-gray-200">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Claim ID</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rule</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Severity</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Flagged At</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {loadingClaims ? (
                      <tr>
                        <td colSpan="6" className="px-6 py-12 text-center text-gray-500">
                          Loading flagged claims...
                        </td>
                      </tr>
                    ) : filteredClaims.length === 0 ? (
                      <tr>
                        <td colSpan="6" className="px-6 py-12 text-center text-gray-500">
                          No flagged claims found
                        </td>
                      </tr>
                    ) : (
                      paginatedClaims.map((claim) => (
                        <tr key={claim.id} className="hover:bg-gray-50">
                          <td className="px-6 py-4 text-sm font-medium text-gray-900">
                            {claim.claim_number}
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-600">{claim.rule_name}</td>
                          <td className="px-6 py-4">
                            <span className={`px-3 py-1 text-xs font-medium rounded-full ${getSeverityColor(claim.severity)}`}>
                              {claim.severity || 'Medium'}
                            </span>
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-600">
                            {new Date(claim.flagged_at).toLocaleDateString()}
                          </td>
                          <td className="px-6 py-4">
                            {claim.reviewed ? (
                              <span className="flex items-center gap-1 text-sm text-green-600">
                                <CheckCircle className="w-4 h-4" />
                                Reviewed
                              </span>
                            ) : (
                              <span className="flex items-center gap-1 text-sm text-amber-600">
                                <AlertTriangle className="w-4 h-4" />
                                Pending
                              </span>
                            )}
                          </td>
                          <td className="px-6 py-4">
                            <button
                              onClick={() => setSelectedClaim(claim)}
                              className="flex items-center gap-1 text-primary hover:text-primary-hover"
                            >
                              <Eye className="w-4 h-4" />
                              View
                            </button>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>

              <PaginationControls
                currentPage={claimsPage}
                totalPages={totalClaimsPages}
                totalItems={filteredClaims.length}
                itemsPerPage={claimsPerPage}
                setPage={setClaimsPage}
                setPerPage={setClaimsPerPage}
                itemName="claims"
              />
            </div>
          </>
        )}
      </div>

      {/* Claim Detail Modal */}
      {selectedClaim && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-bold text-gray-900">Claim Details</h2>
            </div>
            <div className="p-6 space-y-4">
              <div>
                <p className="text-sm text-gray-600">Claim Number</p>
                <p className="text-lg font-semibold">{selectedClaim.claim_number}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Rule Triggered</p>
                <p className="font-medium">{selectedClaim.rule_name}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Explanation</p>
                <p className="text-gray-700">{selectedClaim.explanation?.summary || 'No explanation provided'}</p>
              </div>
              
              {/* Run Traceability */}
              {selectedClaim.run_id && (
                <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Play className="w-4 h-4 text-purple-600" />
                    <span className="font-medium text-purple-800">Audit Run Traceability</span>
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-gray-600">Run ID</p>
                      <p className="font-mono text-xs text-purple-700">{selectedClaim.run_id}</p>
                    </div>
                    <div>
                      <p className="text-gray-600">Rule Version</p>
                      <p className="font-medium">v{selectedClaim.rule_version}</p>
                    </div>
                    {selectedClaim.rule_code && (
                      <div>
                        <p className="text-gray-600">Rule Code</p>
                        <p className="font-medium">{selectedClaim.rule_code}</p>
                      </div>
                    )}
                    {selectedClaim.category && (
                      <div>
                        <p className="text-gray-600">Category</p>
                        <p className="font-medium">{selectedClaim.category}</p>
                      </div>
                    )}
                  </div>
                </div>
              )}
              
              {/* Show review info if already reviewed */}
              {selectedClaim.reviewed ? (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-3">
                    <CheckCircle className="w-5 h-5 text-green-600" />
                    <span className="font-medium text-green-800">Reviewed</span>
                  </div>
                  {selectedClaim.reviewed_at && (
                    <div className="mb-2">
                      <p className="text-sm text-gray-600">Reviewed At</p>
                      <p className="text-sm font-medium">{new Date(selectedClaim.reviewed_at).toLocaleString()}</p>
                    </div>
                  )}
                  {selectedClaim.reviewer_notes && (
                    <div>
                      <p className="text-sm text-gray-600">Review Notes</p>
                      <p className="text-sm text-gray-800 mt-1 whitespace-pre-wrap">{selectedClaim.reviewer_notes}</p>
                    </div>
                  )}
                  {!selectedClaim.reviewer_notes && (
                    <p className="text-sm text-gray-500 italic">No review notes provided</p>
                  )}
                </div>
              ) : (
                <div>
                  <label className="block text-sm text-gray-600 mb-2">Review Notes</label>
                  <textarea
                    id="reviewNotes"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                    rows="4"
                    placeholder="Add your review notes..."
                  />
                </div>
              )}
            </div>
            <div className="p-6 border-t border-gray-200 flex gap-3 justify-end">
              <button
                onClick={() => setSelectedClaim(null)}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
              >
                Close
              </button>
              {!selectedClaim.reviewed && (
                <button
                  onClick={() => {
                    const notes = document.getElementById('reviewNotes').value;
                    handleReview(selectedClaim.id, notes);
                  }}
                  className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-hover"
                >
                  Mark as Reviewed
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FlaggedClaims;