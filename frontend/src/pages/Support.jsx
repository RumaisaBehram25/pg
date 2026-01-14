import { Mail, Phone, MessageCircle, FileText, ExternalLink } from 'lucide-react';

const Support = () => {
  return (
    <div className="flex-1 overflow-auto bg-gray-50">
      <div className="bg-white border-b border-gray-200 px-8 py-4">
        <h1 className="text-2xl font-bold text-gray-900">Support</h1>
        <p className="text-sm text-gray-600 mt-1">Get help and access resources</p>
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
              className="text-primary hover:text-primary-hover font-medium text-sm"
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
              className="text-primary hover:text-primary-hover font-medium text-sm"
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
            <button className="text-primary hover:text-primary-hover font-medium text-sm">
              Start Chat
            </button>
          </div>
        </div>

        {/* Documentation */}
        <div className="bg-white rounded-xl shadow-sm p-6 mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Documentation & Resources</h2>
          <div className="space-y-3">
            <a
              href="#"
              className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors group"
            >
              <div className="flex items-center gap-3">
                <FileText className="w-5 h-5 text-gray-600" />
                <div>
                  <p className="font-medium text-gray-900">Getting Started Guide</p>
                  <p className="text-sm text-gray-600">Learn the basics of PharmAudit</p>
                </div>
              </div>
              <ExternalLink className="w-5 h-5 text-gray-400 group-hover:text-primary" />
            </a>

            <a
              href="#"
              className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors group"
            >
              <div className="flex items-center gap-3">
                <FileText className="w-5 h-5 text-gray-600" />
                <div>
                  <p className="font-medium text-gray-900">CSV Upload Format</p>
                  <p className="text-sm text-gray-600">Required fields and data format</p>
                </div>
              </div>
              <ExternalLink className="w-5 h-5 text-gray-400 group-hover:text-primary" />
            </a>

            <a
              href="#"
              className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors group"
            >
              <div className="flex items-center gap-3">
                <FileText className="w-5 h-5 text-gray-600" />
                <div>
                  <p className="font-medium text-gray-900">Fraud Detection Rules</p>
                  <p className="text-sm text-gray-600">How to create and manage rules</p>
                </div>
              </div>
              <ExternalLink className="w-5 h-5 text-gray-400 group-hover:text-primary" />
            </a>

            <a
              href="#"
              className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors group"
            >
              <div className="flex items-center gap-3">
                <FileText className="w-5 h-5 text-gray-600" />
                <div>
                  <p className="font-medium text-gray-900">API Documentation</p>
                  <p className="text-sm text-gray-600">Integrate with PharmAudit API</p>
                </div>
              </div>
              <ExternalLink className="w-5 h-5 text-gray-400 group-hover:text-primary" />
            </a>
          </div>
        </div>

        {/* FAQ */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Frequently Asked Questions</h2>
          <div className="space-y-4">
            <div className="border-b border-gray-200 pb-4">
              <h3 className="font-medium text-gray-900 mb-2">How do I upload a CSV file?</h3>
              <p className="text-sm text-gray-600">
                Navigate to the "Upload new CSV" page from the sidebar, then drag and drop your CSV file or click to browse. 
                Make sure your file includes all required fields.
              </p>
            </div>

            <div className="border-b border-gray-200 pb-4">
              <h3 className="font-medium text-gray-900 mb-2">What happens after I upload claims data?</h3>
              <p className="text-sm text-gray-600">
                The system will automatically process your data, validate all fields, and run fraud detection rules. 
                You'll receive notifications when processing is complete and can review any flagged claims.
              </p>
            </div>

            <div className="border-b border-gray-200 pb-4">
              <h3 className="font-medium text-gray-900 mb-2">How do I review flagged claims?</h3>
              <p className="text-sm text-gray-600">
                Go to the "Flagged Claims" page to view all claims that triggered fraud detection rules. 
                Click on any claim to see details and mark it as reviewed after investigation.
              </p>
            </div>

            <div className="pb-4">
              <h3 className="font-medium text-gray-900 mb-2">Can I create custom fraud detection rules?</h3>
              <p className="text-sm text-gray-600">
                Yes! Use the "Create New Rule" page to define custom rules with specific conditions. 
                You can set thresholds, combine multiple conditions, and assign severity levels.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Support;




