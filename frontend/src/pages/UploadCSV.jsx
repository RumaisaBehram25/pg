import { useState, useEffect } from 'react';
import { Upload, FileText, CheckCircle, AlertCircle, Loader, Eye, Trash2, RefreshCw, X, ChevronLeft, ChevronRight } from 'lucide-react';
import { claimsAPI } from '../utils/api';

const UploadCSV = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [error, setError] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  
  // Jobs list
  const [jobs, setJobs] = useState([]);
  const [loadingJobs, setLoadingJobs] = useState(true);
  const [selectedJob, setSelectedJob] = useState(null);
  const [jobDetails, setJobDetails] = useState(null);
  const [jobErrors, setJobErrors] = useState(null);
  const [loadingDetails, setLoadingDetails] = useState(false);
  
  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(10);
  
  // Delete confirmation modal
  const [deleteConfirmJob, setDeleteConfirmJob] = useState(null);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    fetchJobs();
    const interval = setInterval(fetchJobs, 5000); // Auto-refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchJobs = async () => {
    try {
      const response = await claimsAPI.getJobs();
      setJobs(response.data.jobs);
    } catch (err) {
      console.error('Failed to fetch jobs:', err);
    } finally {
      setLoadingJobs(false);
    }
  };

  const fetchJobDetails = async (jobId) => {
    setLoadingDetails(true);
    try {
      const [detailsRes, errorsRes] = await Promise.all([
        claimsAPI.getJobStatus(jobId),
        claimsAPI.getJobErrors(jobId).catch(() => ({ data: { errors: [] } }))
      ]);
      setJobDetails(detailsRes.data);
      setJobErrors(errorsRes.data);
      setSelectedJob(jobId);
    } catch (err) {
      console.error('Failed to fetch job details:', err);
    } finally {
      setLoadingDetails(false);
    }
  };

  const handleDeleteJob = (job) => {
    setDeleteConfirmJob(job);
  };

  const confirmDeleteJob = async () => {
    if (!deleteConfirmJob) return;
    
    setDeleting(true);
    try {
      await claimsAPI.deleteJob(deleteConfirmJob.job_id);
      setJobs(jobs.filter(j => j.job_id !== deleteConfirmJob.job_id));
      if (selectedJob === deleteConfirmJob.job_id) {
        setSelectedJob(null);
        setJobDetails(null);
      }
      setDeleteConfirmJob(null);
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to delete job');
    } finally {
      setDeleting(false);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.name.endsWith('.csv')) {
        setSelectedFile(file);
        setError(null);
      } else {
        setError('Please upload a CSV file');
      }
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (file.name.endsWith('.csv')) {
        setSelectedFile(file);
        setError(null);
      } else {
        setError('Please upload a CSV file');
      }
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploading(true);
    setError(null);
    setUploadResult(null);

    try {
      const result = await claimsAPI.uploadCSV(selectedFile);
      setUploadResult(result.data);
      setSelectedFile(null);
      fetchJobs(); // Refresh jobs list
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const getStatusColor = (status) => {
    switch(status) {
      case 'completed': return 'bg-green-100 text-green-700';
      case 'processing': return 'bg-blue-100 text-blue-700';
      case 'pending': return 'bg-yellow-100 text-yellow-700';
      case 'failed': return 'bg-red-100 text-red-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  // Pagination calculations
  const totalPages = Math.ceil(jobs.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const paginatedJobs = jobs.slice(startIndex, endIndex);

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
            <h1 className="text-2xl font-bold text-gray-900">Upload & Manage CSV Files</h1>
            <p className="text-sm text-gray-600 mt-1">Upload claims data and track processing status</p>
          </div>
          <button
            onClick={fetchJobs}
            className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
        </div>
      </div>

      <div className="p-8 space-y-6">
        {/* Upload Section */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Upload New File</h2>
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors max-w-xl mx-auto ${
              dragActive
                ? 'border-primary bg-primary/5'
                : 'border-gray-300 hover:border-primary'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <Upload className={`w-12 h-12 mx-auto mb-3 ${dragActive ? 'text-primary' : 'text-gray-400'}`} />
            
            {!selectedFile ? (
              <>
                <p className="text-sm text-gray-600 mb-3">Drop CSV here or</p>
                <label className="inline-block">
                  <input
                    type="file"
                    accept=".csv"
                    onChange={handleFileChange}
                    className="hidden"
                  />
                  <span className="px-4 py-2 bg-primary text-white rounded-lg cursor-pointer hover:bg-primary-hover transition-colors inline-block text-sm">
                    Browse Files
                  </span>
                </label>
              </>
            ) : (
              <div className="space-y-3">
                <FileText className="w-12 h-12 mx-auto text-primary" />
                <div>
                  <p className="text-sm font-semibold text-gray-900">{selectedFile.name}</p>
                  <p className="text-xs text-gray-600">{(selectedFile.size / 1024).toFixed(2)} KB</p>
                </div>
                <div className="flex gap-2 justify-center">
                  <button
                    onClick={handleUpload}
                    disabled={uploading}
                    className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-hover transition-colors disabled:opacity-50 text-sm flex items-center gap-2"
                  >
                    {uploading ? <><Loader className="w-4 h-4 animate-spin" />Uploading...</> : 'Upload'}
                  </button>
                  <button
                    onClick={() => setSelectedFile(null)}
                    disabled={uploading}
                    className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-sm"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            )}
          </div>

          {error && (
            <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2 max-w-xl mx-auto">
              <AlertCircle className="w-4 h-4 text-red-600 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          {uploadResult && (
            <div className="mt-3 p-3 bg-green-50 border border-green-200 rounded-lg flex items-start gap-2 max-w-xl mx-auto">
              <CheckCircle className="w-4 h-4 text-green-600 flex-shrink-0 mt-0.5" />
              <div className="text-sm">
                <p className="text-green-800 font-medium">{uploadResult.message}</p>
                <p className="text-green-700 mt-1">Job ID: {uploadResult.job_id?.substring(0, 8)}</p>
              </div>
            </div>
          )}
        </div>

        {/* Jobs List */}
        <div>
          <div className="bg-white rounded-xl shadow-sm overflow-hidden">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Processing Jobs ({jobs.length})</h2>
            </div>
            
            <div className="overflow-x-auto max-h-[600px] overflow-y-auto">
              <table className="w-full">
                <thead className="bg-gray-50 sticky top-0">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Job ID</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">File</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Claims</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Flags</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {loadingJobs ? (
                    <tr>
                      <td colSpan="6" className="px-4 py-8 text-center text-gray-500">
                        <Loader className="w-6 h-6 animate-spin mx-auto mb-2" />
                        Loading jobs...
                      </td>
                    </tr>
                  ) : jobs.length === 0 ? (
                    <tr>
                      <td colSpan="6" className="px-4 py-8 text-center text-gray-500">
                        No jobs yet. Upload a CSV to get started.
                      </td>
                    </tr>
                  ) : (
                    paginatedJobs.map((job) => (
                      <tr key={job.job_id} className="hover:bg-gray-50">
                        <td className="px-4 py-3 text-xs font-mono text-gray-900">
                          #{job.job_id.substring(0, 8)}
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-600 max-w-xs truncate">
                          {job.file_name}
                        </td>
                        <td className="px-4 py-3 text-sm">
                          <div className="text-gray-900">{job.success_count}/{job.total_rows}</div>
                          {job.error_count > 0 && (
                            <div className="text-xs text-red-600">{job.error_count} errors</div>
                          )}
                        </td>
                        <td className="px-4 py-3">
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(job.status)}`}>
                            {job.status}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-900">
                          {job.fraud_flags_count > 0 ? (
                            <span className="text-red-600 font-medium">{job.fraud_flags_count}</span>
                          ) : (
                            '-'
                          )}
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-1">
                            <button
                              onClick={() => fetchJobDetails(job.job_id)}
                              className="p-1.5 text-primary hover:bg-primary/10 rounded transition-colors"
                              title="View Details"
                            >
                              <Eye className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => handleDeleteJob(job)}
                              className="p-1.5 text-red-600 hover:bg-red-50 rounded transition-colors"
                              title="Delete Job"
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
            {jobs.length > 0 && (
              <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <span className="text-sm text-gray-600">
                    Showing {startIndex + 1} to {Math.min(endIndex, jobs.length)} of {jobs.length} jobs
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
      </div>

      {/* Delete Confirmation Modal */}
      {deleteConfirmJob && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl max-w-md w-full p-6 shadow-xl">
            <div className="flex items-center gap-4 mb-4">
              <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center flex-shrink-0">
                <AlertCircle className="w-6 h-6 text-red-600" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-gray-900">Delete Job</h3>
                <p className="text-sm text-gray-600">This action cannot be undone</p>
              </div>
            </div>
            
            <div className="bg-gray-50 rounded-lg p-4 mb-6">
              <p className="text-sm text-gray-700">
                Are you sure you want to delete <span className="font-semibold">{deleteConfirmJob.file_name}</span>?
              </p>
              <p className="text-xs text-gray-500 mt-2">
                This will permanently remove the job and all associated claims and flagged results.
              </p>
            </div>
            
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => setDeleteConfirmJob(null)}
                disabled={deleting}
                className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                onClick={confirmDeleteJob}
                disabled={deleting}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50 flex items-center gap-2"
              >
                {deleting ? (
                  <>
                    <Loader className="w-4 h-4 animate-spin" />
                    Deleting...
                  </>
                ) : (
                  <>
                    <Trash2 className="w-4 h-4" />
                    Delete Job
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Job Details Modal */}
      {selectedJob && jobDetails && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200 flex items-center justify-between sticky top-0 bg-white">
              <h2 className="text-xl font-bold text-gray-900">Job Details</h2>
              <button
                onClick={() => {
                  setSelectedJob(null);
                  setJobDetails(null);
                  setJobErrors(null);
                }}
                className="p-2 hover:bg-gray-100 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            {loadingDetails ? (
              <div className="p-12 text-center">
                <Loader className="w-8 h-8 animate-spin mx-auto mb-4 text-primary" />
                <p className="text-gray-600">Loading details...</p>
              </div>
            ) : (
              <div className="p-6 space-y-6">
                {/* Job Info */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-600">Job ID</p>
                    <p className="font-mono text-sm">#{jobDetails.job_id.substring(0, 8)}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">File Name</p>
                    <p className="font-medium">{jobDetails.file_name}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Status</p>
                    <span className={`inline-block px-3 py-1 text-xs font-medium rounded-full ${getStatusColor(jobDetails.status)}`}>
                      {jobDetails.status}
                    </span>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Fraud Status</p>
                    <span className={`inline-block px-3 py-1 text-xs font-medium rounded-full ${getStatusColor(jobDetails.fraud_status)}`}>
                      {jobDetails.fraud_status}
                    </span>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Total Rows</p>
                    <p className="font-medium">{jobDetails.total_rows}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Success</p>
                    <p className="font-medium text-green-600">{jobDetails.success_count}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Errors</p>
                    <p className="font-medium text-red-600">{jobDetails.error_count}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Flagged Claims</p>
                    <p className="font-medium text-amber-600">{jobDetails.fraud_flags_count}</p>
                  </div>
                </div>

                {/* Job-level Error (row_number = 0) */}
                {jobErrors && jobErrors.errors && jobErrors.errors.some(e => e.row_number === 0) && (
                  <div className="p-4 bg-red-100 border border-red-300 rounded-lg">
                    <div className="flex items-start gap-3">
                      <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                      <div>
                        <p className="font-semibold text-red-800">Job Failed</p>
                        <p className="text-sm text-red-700 mt-1">
                          {jobErrors.errors.find(e => e.row_number === 0)?.error_message}
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {/* Row-level Errors */}
                {jobErrors && jobErrors.errors && jobErrors.errors.filter(e => e.row_number !== 0).length > 0 && (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-3">
                      Row Errors ({jobErrors.errors.filter(e => e.row_number !== 0).length})
                    </h3>
                    <div className="space-y-2 max-h-60 overflow-y-auto">
                      {jobErrors.errors.filter(e => e.row_number !== 0).map((error, idx) => (
                        <div key={idx} className="p-3 bg-red-50 border border-red-200 rounded-lg">
                          <p className="text-sm font-medium text-red-900">Row {error.row_number}</p>
                          <p className="text-xs text-red-700 mt-1">{error.error_message}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default UploadCSV;
