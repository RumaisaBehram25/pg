import { Mail, Phone, MessageCircle, HelpCircle, FileText, ExternalLink } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const Support = () => {
  const navigate = useNavigate();

  return (
    <div className="flex-1 overflow-auto bg-gray-50">
      <div className="bg-white border-b border-gray-200 px-8 py-6">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-primary/10 rounded-xl">
            <HelpCircle className="w-6 h-6 text-primary" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Support</h1>
            <p className="text-sm text-gray-600 mt-1">Get help and access resources</p>
          </div>
        </div>
      </div>

      <div className="p-8 max-w-6xl mx-auto">
        {/* Contact Options */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition-shadow">
            <div className="p-3 bg-blue-100 rounded-lg w-fit mb-4">
              <Mail className="w-6 h-6 text-blue-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Email Support</h3>
            <p className="text-sm text-gray-600 mb-4">
              Get help via email within 24 hours
            </p>
            <a
              href="mailto:support@pharmaudit.com"
              className="text-primary hover:text-primary/80 font-medium text-sm"
            >
              support@pharmaudit.com
            </a>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition-shadow">
            <div className="p-3 bg-green-100 rounded-lg w-fit mb-4">
              <Phone className="w-6 h-6 text-green-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Phone Support</h3>
            <p className="text-sm text-gray-600 mb-4">
              Speak with our team directly
            </p>
            <a
              href="tel:+18005551234"
              className="text-primary hover:text-primary/80 font-medium text-sm"
            >
              1-800-555-1234
            </a>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6 hover:shadow-md transition-shadow">
            <div className="p-3 bg-purple-100 rounded-lg w-fit mb-4">
              <MessageCircle className="w-6 h-6 text-purple-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Live Chat</h3>
            <p className="text-sm text-gray-600 mb-4">
              Chat with us in real-time
            </p>
            <button 
              onClick={() => alert('Live chat feature coming soon!')}
              className="text-primary hover:text-primary/80 font-medium text-sm"
            >
              Start Chat
            </button>
          </div>
        </div>

        {/* Documentation */}
        <div className="bg-white rounded-xl shadow-sm p-6 mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Documentation & Resources</h2>
          <div className="space-y-3">
            <button
              onClick={() => navigate('/docs/csv-format')}
              className="w-full flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors group text-left"
            >
              <div className="flex items-center gap-3">
                <FileText className="w-5 h-5 text-gray-600" />
                <div>
                  <p className="font-medium text-gray-900">CSV Upload Format</p>
                  <p className="text-sm text-gray-600">Required fields and data format specifications</p>
                </div>
              </div>
              <ExternalLink className="w-5 h-5 text-gray-400 group-hover:text-primary" />
            </button>

            <button
              onClick={() => navigate('/docs/fraud-rules')}
              className="w-full flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors group text-left"
            >
              <div className="flex items-center gap-3">
                <FileText className="w-5 h-5 text-gray-600" />
                <div>
                  <p className="font-medium text-gray-900">Fraud Detection Rules</p>
                  <p className="text-sm text-gray-600">How to create and manage fraud detection rules</p>
                </div>
              </div>
              <ExternalLink className="w-5 h-5 text-gray-400 group-hover:text-primary" />
            </button>
          </div>
        </div>

        {/* FAQ */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-6">Frequently Asked Questions</h2>
          <div className="space-y-6">
            <div className="pb-6 border-b border-gray-200">
              <h3 className="font-semibold text-gray-900 mb-2 text-base">How do I upload a CSV file?</h3>
              <p className="text-sm text-gray-600 leading-relaxed">
                Navigate to the "Upload new CSV" page from the sidebar, then drag and drop your CSV file or click to browse. 
                Make sure your file includes all required fields: claim_number, patient_id, drug_name, quantity, days_supply, 
                prescriber_id, pharmacy_id, fill_date, and paid_amount.
              </p>
            </div>

            <div className="pb-6 border-b border-gray-200">
              <h3 className="font-semibold text-gray-900 mb-2 text-base">What happens after I upload claims data?</h3>
              <p className="text-sm text-gray-600 leading-relaxed">
                The system will automatically process your data, validate all fields, and run all active fraud detection rules 
                against your claims. You can monitor the progress in real-time, and once complete, you'll be able to review 
                any flagged claims in the "Flagged Claims" section.
              </p>
            </div>

            <div className="pb-6 border-b border-gray-200">
              <h3 className="font-semibold text-gray-900 mb-2 text-base">How do I review flagged claims?</h3>
              <p className="text-sm text-gray-600 leading-relaxed">
                Go to the "Flagged Claims" page to view all claims that triggered fraud detection rules. Each flagged claim 
                shows which rule was violated, the severity level, and detailed information. Click on any claim to see full 
                details and mark it as reviewed after your investigation.
              </p>
            </div>

            <div className="pb-6 border-b border-gray-200">
              <h3 className="font-semibold text-gray-900 mb-2 text-base">Can I create custom fraud detection rules?</h3>
              <p className="text-sm text-gray-600 leading-relaxed">
                Yes! Navigate to the "Rules" page and click "Create New Rule". You can define custom rules with specific 
                conditions, set thresholds, assign severity levels (Financial, Compliance, or Clinical), and categorize 
                them appropriately. All rules are versioned for full audit traceability.
              </p>
            </div>

            <div className="pb-6 border-b border-gray-200">
              <h3 className="font-semibold text-gray-900 mb-2 text-base">How can I export my data?</h3>
              <p className="text-sm text-gray-600 leading-relaxed">
                Most pages include export functionality. You can export flagged claims, audit reports, rule performance data, 
                and audit trail logs to CSV format. Look for the "Export" buttons on each page to download your data.
              </p>
            </div>

            <div className="pb-6 border-b border-gray-200">
              <h3 className="font-semibold text-gray-900 mb-2 text-base">What is the Audit Trail?</h3>
              <p className="text-sm text-gray-600 leading-relaxed">
                The Audit Trail maintains a complete history of all actions performed in the system, including user logins, 
                CSV uploads, rule changes, and claim reviews. This ensures full compliance and accountability for all 
                operations in PharmAudit.
              </p>
            </div>

            <div>
              <h3 className="font-semibold text-gray-900 mb-2 text-base">How do I manage users?</h3>
              <p className="text-sm text-gray-600 leading-relaxed">
                Admin users can access the "Manage Users" page to create new users, assign roles (Admin, Auditor, or Viewer), 
                and manage user permissions. Each user role has specific access levels to ensure proper security controls.
              </p>
            </div>
          </div>
        </div>

        {/* System Info */}
        <div className="bg-gradient-to-r from-primary/10 to-purple-100 rounded-xl p-6 mt-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-2">Need Additional Help?</h2>
          <p className="text-sm text-gray-600 mb-4">
            Our support team is available Monday-Friday, 9 AM - 6 PM EST. We typically respond to emails within 24 hours.
          </p>
          <p className="text-sm text-gray-600">
            For urgent issues, please call our phone support line directly.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Support;
