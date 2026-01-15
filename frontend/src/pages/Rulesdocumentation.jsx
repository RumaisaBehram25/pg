import { ArrowLeft, Shield, AlertTriangle, AlertCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const RulesDocumentation = () => {
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
              <Shield className="w-6 h-6 text-primary" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Fraud Detection Rules Guide</h1>
              <p className="text-sm text-gray-600 mt-1">How to create and manage fraud detection rules</p>
            </div>
          </div>
        </div>
      </div>

      <div className="p-8 max-w-5xl mx-auto">
        {/* Overview */}
        <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Overview</h2>
          <p className="text-gray-600 mb-4">
            PharmAudit uses a comprehensive rule-based system to detect potential fraud, waste, and abuse in pharmacy claims. 
            Each rule is designed to identify specific patterns or anomalies that may indicate fraudulent activity.
          </p>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-sm text-blue-800">
              <strong>Important:</strong> All rules are versioned to maintain full audit traceability. When you modify a rule, 
              a new version is created automatically.
            </p>
          </div>
        </div>

        {/* Rule Components */}
        <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Rule Components</h2>
          <div className="space-y-4">
            <div className="border-l-4 border-primary pl-4">
              <h3 className="font-semibold text-gray-900 mb-2">Rule Code</h3>
              <p className="text-sm text-gray-600">
                Unique identifier (e.g., DR-001, DR-038). Must start with "DR-" followed by 3 digits.
              </p>
            </div>
            <div className="border-l-4 border-primary pl-4">
              <h3 className="font-semibold text-gray-900 mb-2">Rule Name</h3>
              <p className="text-sm text-gray-600">
                Descriptive name of the rule (e.g., "High quantity dispensed", "Early refill pattern").
              </p>
            </div>
            <div className="border-l-4 border-primary pl-4">
              <h3 className="font-semibold text-gray-900 mb-2">Description</h3>
              <p className="text-sm text-gray-600">
                Detailed explanation of what the rule detects and why it's important.
              </p>
            </div>
            <div className="border-l-4 border-primary pl-4">
              <h3 className="font-semibold text-gray-900 mb-2">Conditions</h3>
              <p className="text-sm text-gray-600">
                The specific logic that determines when a claim should be flagged (e.g., quantity &gt; 90).
              </p>
            </div>
          </div>
        </div>

        {/* Severity Levels */}
        <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Severity Levels</h2>
          <div className="space-y-3">
            <div className="flex items-start gap-3 p-4 bg-red-50 rounded-lg">
              <div className="w-3 h-3 bg-red-500 rounded-full mt-1.5 flex-shrink-0"></div>
              <div>
                <p className="font-semibold text-red-900">FINANCIAL</p>
                <p className="text-sm text-red-700">
                  Indicates direct financial impact or potential monetary fraud (e.g., excessive billing, duplicate claims).
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3 p-4 bg-amber-50 rounded-lg">
              <div className="w-3 h-3 bg-amber-500 rounded-full mt-1.5 flex-shrink-0"></div>
              <div>
                <p className="font-semibold text-amber-900">COMPLIANCE</p>
                <p className="text-sm text-amber-700">
                  Regulatory or policy violations that may not have immediate financial impact (e.g., missing documentation, 
                  non-approved drugs).
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Categories */}
        <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Rule Categories</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 border border-gray-200 rounded-lg">
              <p className="font-semibold text-gray-900 mb-2">Duplicate Billing</p>
              <p className="text-sm text-gray-600">Rules detecting duplicate or redundant claims</p>
            </div>
            <div className="p-4 border border-gray-200 rounded-lg">
              <p className="font-semibold text-gray-900 mb-2">Utilization</p>
              <p className="text-sm text-gray-600">Rules for unusual utilization patterns</p>
            </div>
            <div className="p-4 border border-gray-200 rounded-lg">
              <p className="font-semibold text-gray-900 mb-2">Quantity / Days Supply</p>
              <p className="text-sm text-gray-600">Rules related to dispensed quantities and days supply</p>
            </div>
            <div className="p-4 border border-gray-200 rounded-lg">
              <p className="font-semibold text-gray-900 mb-2">Pricing</p>
              <p className="text-sm text-gray-600">Rules for unusual pricing or cost patterns</p>
            </div>
            <div className="p-4 border border-gray-200 rounded-lg">
              <p className="font-semibold text-gray-900 mb-2">Eligibility / Network</p>
              <p className="text-sm text-gray-600">Rules for eligibility and network compliance</p>
            </div>
            <div className="p-4 border border-gray-200 rounded-lg">
              <p className="font-semibold text-gray-900 mb-2">Drug Restrictions</p>
              <p className="text-sm text-gray-600">Rules for restricted or controlled substances</p>
            </div>
            <div className="p-4 border border-gray-200 rounded-lg">
              <p className="font-semibold text-gray-900 mb-2">Prescriber Integrity</p>
              <p className="text-sm text-gray-600">Rules detecting unusual prescriber behavior</p>
            </div>
            <div className="p-4 border border-gray-200 rounded-lg">
              <p className="font-semibold text-gray-900 mb-2">Date Integrity</p>
              <p className="text-sm text-gray-600">Rules for date-related anomalies and inconsistencies</p>
            </div>
            <div className="p-4 border border-gray-200 rounded-lg">
              <p className="font-semibold text-gray-900 mb-2">Documentation</p>
              <p className="text-sm text-gray-600">Rules for missing or incomplete documentation</p>
            </div>
            <div className="p-4 border border-gray-200 rounded-lg">
              <p className="font-semibold text-gray-900 mb-2">Extended Validation</p>
              <p className="text-sm text-gray-600">Complex multi-factor validation rules</p>
            </div>
            <div className="p-4 border border-gray-200 rounded-lg">
              <p className="font-semibold text-gray-900 mb-2">Other</p>
              <p className="text-sm text-gray-600">Miscellaneous rules that don't fit other categories</p>
            </div>
          </div>
        </div>

        {/* Example Rules */}
        <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Example Rules</h2>
          <div className="space-y-4">
            <div className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="font-mono text-sm font-semibold text-primary">DR-001</span>
                <span className="px-2 py-1 bg-red-100 text-red-700 rounded text-xs font-medium">FINANCIAL</span>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">High Quantity Dispensed</h3>
              <p className="text-sm text-gray-600 mb-2">
                Flags claims where the dispensed quantity exceeds 90 units in a single fill.
              </p>
              <p className="text-xs text-gray-500 font-mono bg-gray-50 p-2 rounded">
                Condition: quantity &gt; 90
              </p>
            </div>

            <div className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="font-mono text-sm font-semibold text-primary">DR-015</span>
                <span className="px-2 py-1 bg-amber-100 text-amber-700 rounded text-xs font-medium">COMPLIANCE</span>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Excessive Days Supply</h3>
              <p className="text-sm text-gray-600 mb-2">
                Detects prescriptions with more than 90 days supply, which may violate plan limits.
              </p>
              <p className="text-xs text-gray-500 font-mono bg-gray-50 p-2 rounded">
                Condition: days_supply &gt; 90
              </p>
            </div>

            <div className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="font-mono text-sm font-semibold text-primary">DR-037</span>
                <span className="px-2 py-1 bg-amber-100 text-amber-700 rounded text-xs font-medium">COMPLIANCE</span>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Opioid Detection</h3>
              <p className="text-sm text-gray-600 mb-2">
                Identifies claims for opioid medications, which require additional scrutiny.
              </p>
              <p className="text-xs text-gray-500 font-mono bg-gray-50 p-2 rounded">
                Condition: drug_name contains "OXY" or "Hydrocodone" or "Fentanyl"
              </p>
            </div>
          </div>
        </div>

        {/* Creating Rules */}
        <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Creating Custom Rules</h2>
          <div className="space-y-4">
            <div className="flex items-start gap-3">
              <div className="w-6 h-6 bg-primary text-white rounded-full flex items-center justify-center flex-shrink-0 text-sm font-bold">
                1
              </div>
              <div>
                <p className="font-medium text-gray-900">Navigate to Rules Page</p>
                <p className="text-sm text-gray-600">Click "Rules" in the sidebar, then click "Create New Rule" button</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-6 h-6 bg-primary text-white rounded-full flex items-center justify-center flex-shrink-0 text-sm font-bold">
                2
              </div>
              <div>
                <p className="font-medium text-gray-900">Fill Basic Information</p>
                <p className="text-sm text-gray-600">Enter rule code (DR-XXX), name, and detailed description</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-6 h-6 bg-primary text-white rounded-full flex items-center justify-center flex-shrink-0 text-sm font-bold">
                3
              </div>
              <div>
                <p className="font-medium text-gray-900">Define Conditions</p>
                <p className="text-sm text-gray-600">Specify the logic that triggers the rule (supports comparisons, text matching, and date checks)</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-6 h-6 bg-primary text-white rounded-full flex items-center justify-center flex-shrink-0 text-sm font-bold">
                4
              </div>
              <div>
                <p className="font-medium text-gray-900">Set Severity and Category</p>
                <p className="text-sm text-gray-600">Choose appropriate severity level (Financial/Compliance) and category</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-6 h-6 bg-primary text-white rounded-full flex items-center justify-center flex-shrink-0 text-sm font-bold">
                5
              </div>
              <div>
                <p className="font-medium text-gray-900">Activate Rule</p>
                <p className="text-sm text-gray-600">Toggle the rule to "Active" status. Only active rules are executed during fraud detection</p>
              </div>
            </div>
          </div>
        </div>

        {/* Best Practices */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Best Practices</h2>
          <div className="space-y-3">
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-medium text-gray-900">Start with Clear Objectives</p>
                <p className="text-sm text-gray-600">Define exactly what pattern or behavior you want to detect</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-medium text-gray-900">Test with Historical Data</p>
                <p className="text-sm text-gray-600">Review how new rules perform against existing claims before full deployment</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-medium text-gray-900">Use Descriptive Names</p>
                <p className="text-sm text-gray-600">Make rule names and descriptions clear enough that any auditor can understand them</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-medium text-gray-900">Document Changes</p>
                <p className="text-sm text-gray-600">Use the description field to note why a rule was created or modified</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-medium text-gray-900">Regular Review</p>
                <p className="text-sm text-gray-600">Periodically review rule performance and adjust thresholds as needed</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RulesDocumentation;