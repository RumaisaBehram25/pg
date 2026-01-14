import { useState, useEffect } from 'react';
import { Save, Plus, Trash2, X } from 'lucide-react';
import { rulesAPI } from '../utils/api';

const CreateRule = ({ onClose, editMode = false, existingRule = null }) => {
  const [mode, setMode] = useState('simple'); // 'simple' or 'json'
  const [jsonInput, setJsonInput] = useState('');
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    rule_code: '',
    category: 'PRICING',
    severity: 'FINANCIAL',
    is_active: true,
    logic_type: 'SIMPLE',
    parameters: {},
    conditions: [{ field: '', operator: '', value: '' }]
  });
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState(null);

  // Load existing rule data when in edit mode
  useEffect(() => {
    if (editMode && existingRule) {
      setFormData({
        name: existingRule.name || '',
        description: existingRule.description || '',
        rule_code: existingRule.rule_code || '',
        category: existingRule.category || 'PRICING',
        severity: existingRule.severity || 'FINANCIAL',
        is_active: existingRule.is_active !== undefined ? existingRule.is_active : true,
        conditions: existingRule.rule_definition?.conditions || [{ field: '', operator: '', value: '' }]
      });
      
      // Also populate JSON mode with the full rule
      const jsonData = {
        name: existingRule.name,
        description: existingRule.description,
        rule_code: existingRule.rule_code,
        category: existingRule.category,
        severity: existingRule.severity,
        is_active: existingRule.is_active,
        rule_definition: existingRule.rule_definition
      };
      setJsonInput(JSON.stringify(jsonData, null, 2));
    }
  }, [editMode, existingRule]);

  const fieldOptions = [
    // Claim Identifiers
    { value: 'claim_number', label: 'Claim Number' },
    { value: 'rx_number', label: 'Prescription Number' },
    
    // Patient Info
    { value: 'patient_id', label: 'Patient ID' },
    
    // Drug Info
    { value: 'drug_code', label: 'Drug Code (NDC)' },
    { value: 'drug_name', label: 'Drug Name' },
    { value: 'drug_class', label: 'Drug Class' },
    
    // Dates
    { value: 'fill_date', label: 'Fill Date' },
    { value: 'prescription_date', label: 'Prescription Date' },
    
    // Quantities
    { value: 'quantity', label: 'Quantity' },
    { value: 'days_supply', label: 'Days Supply' },
    
    // Pricing
    { value: 'allowed_amount', label: 'Allowed Amount' },
    { value: 'paid_amount', label: 'Paid Amount' },
    { value: 'plan_paid', label: 'Plan Paid Amount' },
    { value: 'copay', label: 'Copay Amount' },
    { value: 'ingredient_cost', label: 'Ingredient Cost' },
    { value: 'dispensing_fee', label: 'Dispensing Fee' },
    
    // Provider Info
    { value: 'prescriber_npi', label: 'Prescriber NPI' },
    { value: 'pharmacy_npi', label: 'Pharmacy NPI' },
    
    // Plan Info
    { value: 'plan_id', label: 'Plan ID' },
    
    // Other
    { value: 'daw_code', label: 'DAW Code' },
  ];

  const operatorOptions = [
    { value: 'gt', label: 'Greater Than (>)' },
    { value: 'lt', label: 'Less Than (<)' },
    { value: 'eq', label: 'Equals (=)' },
    { value: 'gte', label: 'Greater Than or Equal (>=)' },
    { value: 'lte', label: 'Less Than or Equal (<=)' },
    { value: 'ne', label: 'Not Equal (!=)' },
    { value: 'contains', label: 'Contains' },
    { value: 'not_contains', label: 'Does Not Contain' },
    { value: 'starts_with', label: 'Starts With' },
    { value: 'ends_with', label: 'Ends With' },
    { value: 'in_list', label: 'In List' },
    { value: 'not_in_list', label: 'Not In List' },
    { value: 'is_null', label: 'Is Null' },
    { value: 'is_not_null', label: 'Is Not Null' },
    { value: 'regex', label: 'Matches Pattern (Regex)' },
  ];

  const addCondition = () => {
    setFormData({
      ...formData,
      conditions: [...formData.conditions, { field: '', operator: '', value: '' }]
    });
  };

  const removeCondition = (index) => {
    setFormData({
      ...formData,
      conditions: formData.conditions.filter((_, i) => i !== index)
    });
  };

  const updateCondition = (index, field, value) => {
    const newConditions = [...formData.conditions];
    newConditions[index][field] = value;
    setFormData({ ...formData, conditions: newConditions });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    setSuccess(false);

    try {
      let ruleData;

      if (mode === 'json') {
        // Parse JSON input
        try {
          ruleData = JSON.parse(jsonInput);
        } catch (parseErr) {
          setError('Invalid JSON format. Please check your input.');
          setSaving(false);
          return;
        }
      } else {
        // Use form data
        const ruleDefinition = {
          logic_type: 'all',
          conditions: formData.conditions
        };

        ruleData = {
          name: formData.name,
          description: formData.description,
          rule_code: formData.rule_code || null,
          category: formData.category,
          severity: formData.severity,
          is_active: formData.is_active,
          rule_definition: ruleDefinition
        };
      }

      if (editMode && existingRule) {
        await rulesAPI.updateRule(existingRule.id, ruleData);
      } else {
        await rulesAPI.createRule(ruleData);
      }

      setSuccess(true);
      
      if (onClose) {
        setTimeout(() => onClose(), 1500);
      } else {
        setFormData({
          name: '',
          description: '',
          rule_code: '',
          category: 'PRICING',
          severity: 'FINANCIAL',
          is_active: true,
          conditions: [{ field: '', operator: '', value: '' }]
        });
        setJsonInput('');
      }
    } catch (err) {
      setError(err.response?.data?.detail || `Failed to ${editMode ? 'update' : 'create'} rule`);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className={onClose ? '' : 'flex-1 overflow-auto bg-gray-50'}>
      {!onClose && (
        <div className="bg-white border-b border-gray-200 px-8 py-4">
          <h1 className="text-2xl font-bold text-gray-900">Create New Rule</h1>
          <p className="text-sm text-gray-600 mt-1">Define fraud detection rules for pharmacy claims</p>
        </div>
      )}

      {onClose && (
        <div className="p-6 border-b border-gray-200 flex items-center justify-between">
          <h2 className="text-xl font-bold text-gray-900">{editMode ? 'Edit Rule' : 'Create New Rule'}</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X className="w-5 h-5" />
          </button>
        </div>
      )}

      <div className={onClose ? 'p-6 max-w-4xl mx-auto' : 'p-8 max-w-4xl mx-auto'}>
        {/* Mode Toggle */}
        <div className="flex gap-2 mb-6 bg-gray-100 p-1 rounded-lg w-fit">
          <button
            type="button"
            onClick={() => setMode('simple')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              mode === 'simple'
                ? 'bg-white text-primary shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Simple Form
          </button>
          <button
            type="button"
            onClick={() => setMode('json')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              mode === 'json'
                ? 'bg-white text-primary shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            JSON Editor
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {mode === 'json' ? (
            /* JSON Editor Mode */
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Rule JSON</h2>
              <p className="text-sm text-gray-600 mb-4">
                Paste your complete rule JSON below. This allows you to create rules with advanced logic types like OVERLAP, DUPLICATE_WINDOW, COUNT_WINDOW, etc.
              </p>
              
              <textarea
                value={jsonInput}
                onChange={(e) => setJsonInput(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary font-mono text-sm"
                rows="20"
                placeholder={`{
  "rule_code": "DR-033",
  "name": "Overlapping coverage by drug name",
  "description": "Patient has overlapping supplies...",
  "category": "EXTENDED_VALIDATION",
  "severity": "FINANCIAL",
  "is_active": true,
  "rule_definition": {
    "logic_type": "OVERLAP",
    "keys": ["tenant_id", "patient_id", "drug_name"],
    "date_field": "fill_date",
    "days_supply_field": "days_supply"
  }
}`}
                required
              />
              
              <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <p className="text-sm text-blue-800 font-medium mb-2">💡 Supported Logic Types:</p>
                <div className="text-xs text-blue-700 space-y-1">
                  <div>• <strong>SIMPLE/THRESHOLD</strong> - Basic field comparisons</div>
                  <div>• <strong>DUPLICATE</strong> - Find duplicate records by keys</div>
                  <div>• <strong>DUPLICATE_WINDOW</strong> - Duplicates within time window</div>
                  <div>• <strong>OVERLAP</strong> - Overlapping date ranges</div>
                  <div>• <strong>COUNT_WINDOW</strong> - Count records in time window</div>
                  <div>• <strong>EARLY_REFILL</strong> - Detect early refills</div>
                  <div>• <strong>RATIO_RANGE</strong> - Field ratio validation</div>
                  <div>• <strong>REGEX</strong> - Pattern matching</div>
                  <div>• <strong>FIELD_COMPARE</strong> - Compare two fields</div>
                  <div>• <strong>IN_LIST/NOT_IN_LIST</strong> - List validation</div>
                </div>
              </div>
            </div>
          ) : (
            /* Simple Form Mode */
            <>
              {/* Basic Information */}
              <div className="bg-white rounded-xl shadow-sm p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Basic Information</h2>
            
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Rule Name *</label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="e.g., High Dollar Amount Alert"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Rule Code</label>
                  <input
                    type="text"
                    value={formData.rule_code}
                    onChange={(e) => setFormData({ ...formData, rule_code: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="e.g., DR-001"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  rows="3"
                  placeholder="Describe what this rule detects..."
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Category *</label>
                  <select
                    value={formData.category}
                    onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                    required
                  >
                    <option value="DUPLICATE_BILLING">Duplicate Billing</option>
                    <option value="UTILIZATION">Utilization</option>
                    <option value="QTY_DAYS_SUPPLY">Quantity / Days Supply</option>
                    <option value="PRICING">Pricing</option>
                    <option value="ELIGIBILITY_NETWORK">Eligibility / Network</option>
                    <option value="DRUG_RESTRICTIONS">Drug Restrictions</option>
                    <option value="PRESCRIBER_INTEGRITY">Prescriber Integrity</option>
                    <option value="DATE_INTEGRITY">Date Integrity</option>
                    <option value="DOCUMENTATION">Documentation</option>
                    <option value="EXTENDED_VALIDATION">Extended Validation</option>
                    <option value="OTHER">Other</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Severity *</label>
                  <select
                    value={formData.severity}
                    onChange={(e) => setFormData({ ...formData, severity: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                    required
                  >
                    <option value="FINANCIAL">Financial (Recoupable)</option>
                    <option value="COMPLIANCE">Compliance (Non-Recoupable)</option>
                  </select>
                </div>
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="is_active"
                  checked={formData.is_active}
                  onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                  className="rounded border-gray-300 text-primary focus:ring-primary"
                />
                <label htmlFor="is_active" className="ml-2 text-sm text-gray-700">
                  Active (rule will be applied to new claims)
                </label>
              </div>
            </div>
          </div>

          {/* Conditions */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Conditions</h2>
              <button
                type="button"
                onClick={addCondition}
                className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-hover transition-colors"
              >
                <Plus className="w-4 h-4" />
                Add Condition
              </button>
            </div>

            <div className="space-y-4">
              {formData.conditions.map((condition, index) => (
                <div key={index} className="flex gap-3 items-start p-4 bg-gray-50 rounded-lg">
                  <div className="flex-1 grid grid-cols-1 md:grid-cols-3 gap-3">
                    <select
                      value={condition.field}
                      onChange={(e) => updateCondition(index, 'field', e.target.value)}
                      className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                      required
                    >
                      <option value="">Select Field</option>
                      {fieldOptions.map(opt => (
                        <option key={opt.value} value={opt.value}>{opt.label}</option>
                      ))}
                    </select>

                    <select
                      value={condition.operator}
                      onChange={(e) => updateCondition(index, 'operator', e.target.value)}
                      className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                      required
                    >
                      <option value="">Select Operator</option>
                      {operatorOptions.map(opt => (
                        <option key={opt.value} value={opt.value}>{opt.label}</option>
                      ))}
                    </select>

                    <input
                      type="text"
                      value={condition.value}
                      onChange={(e) => updateCondition(index, 'value', e.target.value)}
                      placeholder="Value"
                      className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                      required
                    />
                  </div>

                  {formData.conditions.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeCondition(index)}
                      className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>

            </>
          )}

          {/* Messages */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
              {error}
            </div>
          )}

          {success && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-green-800">
              Rule {editMode ? 'updated' : 'created'} successfully!
            </div>
          )}

          {/* Submit Button */}
          <div className="flex justify-end gap-3">
            {onClose && (
              <button
                type="button"
                onClick={onClose}
                disabled={saving}
                className="px-6 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
              >
                Cancel
              </button>
            )}
            {!onClose && (
              <button
                type="button"
                onClick={() => window.history.back()}
                className="px-6 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
              >
                Cancel
              </button>
            )}
            <button
              type="submit"
              disabled={saving}
              className="flex items-center gap-2 px-6 py-3 bg-primary text-white rounded-lg hover:bg-primary-hover transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Save className="w-5 h-5" />
              {saving ? 'Saving...' : (editMode ? 'Update Rule' : (mode === 'json' ? 'Create from JSON' : 'Create Rule'))}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateRule;

