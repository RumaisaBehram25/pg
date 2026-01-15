import { useState, useEffect } from 'react';
import { User, Mail, Shield, Settings as SettingsIcon } from 'lucide-react';
import { usersAPI } from '../utils/api';

const Settings = () => {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCurrentUser();
  }, []);

  const fetchCurrentUser = async () => {
    try {
      const response = await usersAPI.getCurrentUser();
      setCurrentUser(response.data);
    } catch (err) {
      console.error('Failed to fetch current user:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex-1 overflow-auto bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
          <p className="mt-4 text-gray-600">Loading settings...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-auto bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-8 py-6">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-primary/10 rounded-xl">
            <SettingsIcon className="w-6 h-6 text-primary" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
            <p className="text-sm text-gray-600 mt-1">Manage your account information</p>
          </div>
        </div>
      </div>

      <div className="p-8 max-w-4xl">
        {/* User Profile Section */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-6 flex items-center gap-2">
            <User className="w-5 h-5 text-primary" />
            User Profile
          </h2>
          <div className="space-y-6">
            <div className="flex items-center gap-6">
              <div className="w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center flex-shrink-0">
                <User className="w-10 h-10 text-primary" />
              </div>
              <div className="flex-1">
                <p className="text-xl font-semibold text-gray-900 mb-2">
                  {currentUser?.name || 'Admin User'}
                </p>
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-gray-600">
                    <Mail className="w-4 h-4" />
                    <span className="text-sm">{currentUser?.email || 'admin@pharmaudit.com'}</span>
                  </div>
                  <div className="flex items-center gap-2 text-gray-600">
                    <Shield className="w-4 h-4" />
                    <span className="text-sm">Role: <span className="font-medium text-primary">{currentUser?.role || 'ADMIN'}</span></span>
                  </div>
                </div>
              </div>
            </div>

            <div className="pt-6 border-t border-gray-200">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Full Name
                  </label>
                  <input
                    type="text"
                    value={currentUser?.name || 'Admin User'}
                    disabled
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-600 cursor-not-allowed"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email Address
                  </label>
                  <input
                    type="email"
                    value={currentUser?.email || 'admin@pharmaudit.com'}
                    disabled
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-600 cursor-not-allowed"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    User Role
                  </label>
                  <input
                    type="text"
                    value={currentUser?.role || 'ADMIN'}
                    disabled
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-600 cursor-not-allowed"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Account Status
                  </label>
                  <div className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg bg-gray-50">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <span className="text-sm text-gray-600 font-medium">Active</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="pt-6 border-t border-gray-200">
              <p className="text-sm text-gray-500">
                <strong>Note:</strong> To update your account information, please contact your system administrator.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;
