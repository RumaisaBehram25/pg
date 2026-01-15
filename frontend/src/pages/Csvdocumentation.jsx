import { ArrowLeft, FileText, CheckCircle, AlertCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const CsvDocumentation = () => {
  const navigate = useNavigate();

  return (
    <div className="flex-1 overflow-auto bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-8 py-6">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/support')}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div className="flex items-center gap-3">
            <div className="p-3 bg-primary/10 rounded-xl">
              <FileText className="w-6 h-6 text-primary" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">CSV Upload Format Guide</h1>
              <p className="text-sm text-gray-600 mt-1">Required fields and data format specifications</p>
            </div>
          </div>
        </div>
      </div>

      <div className="p-8 max-w-5xl mx-auto">
        {/* Overview */}
        <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Overview</h2>
          <p className="text-gray-600 mb-4">
            PharmAudit accepts CSV files containing pharmacy claims data for fraud detection analysis. 
            This guide outlines the required format, fields, and validation rules to ensure successful data uploads.
          </p>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-sm text-blue-800">
              <strong>Important:</strong> All CSV files must be UTF-8 encoded and include a header row with exact column names as specified below.
            </p>
          </div>
        </div>

        {/* Required Fields */}
        <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Required Fields</h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Field Name</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Data Type</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Format</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Example</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                <tr>
                  <td className="px-4 py-3 font-mono text-sm text-gray-900">tenant_id</td>
                  <td className="px-4 py-3 text-sm text-gray-600">String</td>
                  <td className="px-4 py-3 text-sm text-gray-600">Tenant identifier</td>
                  <td className="px-4 py-3 text-sm font-mono text-gray-600">TENANT-001</td>
                </tr>
                <tr>
                  <td className="px-4 py-3 font-mono text-sm text-gray-900">claim_id</td>
                  <td className="px-4 py-3 text-sm text-gray-600">String</td>
                  <td className="px-4 py-3 text-sm text-gray-600">Unique claim identifier</td>
                  <td className="px-4 py-3 text-sm font-mono text-gray-600">CLM-2024-001234</td>
                </tr>
                <tr>
                  <td className="px-4 py-3 font-mono text-sm text-gray-900">patient_id</td>
                  <td className="px-4 py-3 text-sm text-gray-600">String</td>
                  <td className="px-4 py-3 text-sm text-gray-600">Patient identifier</td>
                  <td className="px-4 py-3 text-sm font-mono text-gray-600">PAT-123456</td>
                </tr>
                <tr>
                  <td className="px-4 py-3 font-mono text-sm text-gray-900">rx_number</td>
                  <td className="px-4 py-3 text-sm text-gray-600">String</td>
                  <td className="px-4 py-3 text-sm text-gray-600">Prescription number</td>
                  <td className="px-4 py-3 text-sm font-mono text-gray-600">RX-789456123</td>
                </tr>
                <tr>
                  <td className="px-4 py-3 font-mono text-sm text-gray-900">ndc</td>
                  <td className="px-4 py-3 text-sm text-gray-600">String</td>
                  <td className="px-4 py-3 text-sm text-gray-600">National Drug Code</td>
                  <td className="px-4 py-3 text-sm font-mono text-gray-600">00378-0710-93</td>
                </tr>
                <tr>
                  <td className="px-4 py-3 font-mono text-sm text-gray-900">drug_name</td>
                  <td className="px-4 py-3 text-sm text-gray-600">String</td>
                  <td className="px-4 py-3 text-sm text-gray-600">Medication name</td>
                  <td className="px-4 py-3 text-sm font-mono text-gray-600">Lisinopril 10mg</td>
                </tr>
                <tr>
                  <td className="px-4 py-3 font-mono text-sm text-gray-900">prescriber_npi</td>
                  <td className="px-4 py-3 text-sm text-gray-600">String</td>
                  <td className="px-4 py-3 text-sm text-gray-600">Prescriber NPI (10 digits)</td>
                  <td className="px-4 py-3 text-sm font-mono text-gray-600">1234567890</td>
                </tr>
                <tr>
                  <td className="px-4 py-3 font-mono text-sm text-gray-900">pharmacy_npi</td>
                  <td className="px-4 py-3 text-sm text-gray-600">String</td>
                  <td className="px-4 py-3 text-sm text-gray-600">Pharmacy NPI (10 digits)</td>
                  <td className="px-4 py-3 text-sm font-mono text-gray-600">9876543210</td>
                </tr>
                <tr>
                  <td className="px-4 py-3 font-mono text-sm text-gray-900">fill_date</td>
                  <td className="px-4 py-3 text-sm text-gray-600">Date</td>
                  <td className="px-4 py-3 text-sm text-gray-600">YYYY-MM-DD</td>
                  <td className="px-4 py-3 text-sm font-mono text-gray-600">2024-01-15</td>
                </tr>
                <tr>
                  <td className="px-4 py-3 font-mono text-sm text-gray-900">days_supply</td>
                  <td className="px-4 py-3 text-sm text-gray-600">Integer</td>
                  <td className="px-4 py-3 text-sm text-gray-600">Days of supply</td>
                  <td className="px-4 py-3 text-sm font-mono text-gray-600">30</td>
                </tr>
                <tr>
                  <td className="px-4 py-3 font-mono text-sm text-gray-900">quantity</td>
                  <td className="px-4 py-3 text-sm text-gray-600">Integer</td>
                  <td className="px-4 py-3 text-sm text-gray-600">Number of units</td>
                  <td className="px-4 py-3 text-sm font-mono text-gray-600">30</td>
                </tr>
                <tr>
                  <td className="px-4 py-3 font-mono text-sm text-gray-900">copay_amount</td>
                  <td className="px-4 py-3 text-sm text-gray-600">Decimal</td>
                  <td className="px-4 py-3 text-sm text-gray-600">Patient copayment (USD)</td>
                  <td className="px-4 py-3 text-sm font-mono text-gray-600">15.00</td>
                </tr>
                <tr>
                  <td className="px-4 py-3 font-mono text-sm text-gray-900">plan_paid_amount</td>
                  <td className="px-4 py-3 text-sm text-gray-600">Decimal</td>
                  <td className="px-4 py-3 text-sm text-gray-600">Amount paid by plan (USD)</td>
                  <td className="px-4 py-3 text-sm font-mono text-gray-600">110.50</td>
                </tr>
                <tr>
                  <td className="px-4 py-3 font-mono text-sm text-gray-900">ingredient_cost</td>
                  <td className="px-4 py-3 text-sm text-gray-600">Decimal</td>
                  <td className="px-4 py-3 text-sm text-gray-600">Drug ingredient cost (USD)</td>
                  <td className="px-4 py-3 text-sm font-mono text-gray-600">95.00</td>
                </tr>
                <tr>
                  <td className="px-4 py-3 font-mono text-sm text-gray-900">usual_and_customary</td>
                  <td className="px-4 py-3 text-sm text-gray-600">Decimal</td>
                  <td className="px-4 py-3 text-sm text-gray-600">U&C charge (USD)</td>
                  <td className="px-4 py-3 text-sm font-mono text-gray-600">145.00</td>
                </tr>
                <tr>
                  <td className="px-4 py-3 font-mono text-sm text-gray-900">plan_id</td>
                  <td className="px-4 py-3 text-sm text-gray-600">String</td>
                  <td className="px-4 py-3 text-sm text-gray-600">Insurance plan identifier</td>
                  <td className="px-4 py-3 text-sm font-mono text-gray-600">PLAN-ABC123</td>
                </tr>
                <tr>
                  <td className="px-4 py-3 font-mono text-sm text-gray-900">state</td>
                  <td className="px-4 py-3 text-sm text-gray-600">String</td>
                  <td className="px-4 py-3 text-sm text-gray-600">Two-letter state code</td>
                  <td className="px-4 py-3 text-sm font-mono text-gray-600">CA</td>
                </tr>
                <tr>
                  <td className="px-4 py-3 font-mono text-sm text-gray-900">claim_status</td>
                  <td className="px-4 py-3 text-sm text-gray-600">String</td>
                  <td className="px-4 py-3 text-sm text-gray-600">Status (e.g., paid, reversed)</td>
                  <td className="px-4 py-3 text-sm font-mono text-gray-600">paid</td>
                </tr>
                <tr>
                  <td className="px-4 py-3 font-mono text-sm text-gray-900">submitted_at</td>
                  <td className="px-4 py-3 text-sm text-gray-600">DateTime</td>
                  <td className="px-4 py-3 text-sm text-gray-600">YYYY-MM-DD HH:MM:SS</td>
                  <td className="px-4 py-3 text-sm font-mono text-gray-600">2024-01-15 14:30:00</td>
                </tr>
                <tr>
                  <td className="px-4 py-3 font-mono text-sm text-gray-900">reversal_date</td>
                  <td className="px-4 py-3 text-sm text-gray-600">Date</td>
                  <td className="px-4 py-3 text-sm text-gray-600">YYYY-MM-DD (if applicable)</td>
                  <td className="px-4 py-3 text-sm font-mono text-gray-600">2024-01-20</td>
                </tr>
                <tr>
                  <td className="px-4 py-3 font-mono text-sm text-gray-900">paid_amount</td>
                  <td className="px-4 py-3 text-sm text-gray-600">Decimal</td>
                  <td className="px-4 py-3 text-sm text-gray-600">Total paid amount (USD)</td>
                  <td className="px-4 py-3 text-sm font-mono text-gray-600">125.50</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* Example CSV */}
        <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Example CSV Format</h2>
          <div className="bg-gray-900 rounded-lg p-4 overflow-x-auto">
            <pre className="text-sm text-green-400 font-mono">
{`tenant_id,claim_id,patient_id,rx_number,ndc,drug_name,prescriber_npi,pharmacy_npi,fill_date,days_supply,quantity,copay_amount,plan_paid_amount,ingredient_cost,usual_and_customary,plan_id,state,claim_status,submitted_at,reversal_date,paid_amount
TENANT-001,CLM-2024-001234,PAT-123456,RX-789456123,00378-0710-93,Lisinopril 10mg,1234567890,9876543210,2024-01-15,30,30,15.00,110.50,95.00,145.00,PLAN-ABC123,CA,paid,2024-01-15 14:30:00,,125.50
TENANT-001,CLM-2024-001235,PAT-789012,RX-789456124,00093-0132-01,Metformin 500mg,1234567891,9876543210,2024-01-15,30,60,10.00,35.00,30.00,55.00,PLAN-ABC123,CA,paid,2024-01-15 15:45:00,,45.00
TENANT-001,CLM-2024-001236,PAT-345678,RX-789456125,00071-0156-23,Atorvastatin 20mg,1234567890,9876543211,2024-01-16,30,30,20.00,69.99,75.00,110.00,PLAN-XYZ456,NY,reversed,2024-01-16 09:20:00,2024-01-20,89.99`}
            </pre>
          </div>
        </div>

        {/* Validation Rules */}
        <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Validation Rules</h2>
          <div className="space-y-4">
            <div className="flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-medium text-gray-900">Required Fields</p>
                <p className="text-sm text-gray-600">All fields listed above must be present in every row</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-medium text-gray-900">Unique Claim IDs</p>
                <p className="text-sm text-gray-600">Each claim_id must be unique within the file</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-medium text-gray-900">Date & DateTime Formats</p>
                <p className="text-sm text-gray-600">fill_date and reversal_date must be in YYYY-MM-DD format; submitted_at must be in YYYY-MM-DD HH:MM:SS format</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-medium text-gray-900">Numeric Values</p>
                <p className="text-sm text-gray-600">quantity and days_supply must be positive integers; paid_amount must be a valid decimal</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-medium text-gray-900">No Empty Values</p>
                <p className="text-sm text-gray-600">No fields can be empty or null</p>
              </div>
            </div>
          </div>
        </div>

        {/* Common Errors */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Common Errors</h2>
          <div className="space-y-4">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-medium text-gray-900">Missing Headers</p>
                <p className="text-sm text-gray-600">Ensure the first row contains all required column names exactly as specified</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-medium text-gray-900">Incorrect Date Format</p>
                <p className="text-sm text-gray-600">Dates like "01/15/2024" or "15-Jan-2024" will be rejected. Use "2024-01-15"</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-medium text-gray-900">Extra Columns</p>
                <p className="text-sm text-gray-600">Additional columns are allowed but will be ignored during processing</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-medium text-gray-900">Empty Rows</p>
                <p className="text-sm text-gray-600">Remove any blank rows from your CSV file before upload</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CsvDocumentation;