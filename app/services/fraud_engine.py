from typing import Dict, List, Tuple, Any
from datetime import datetime, date
from decimal import Decimal

from app.models.claim import Claim, Rule


class FraudEngine:

    
    def evaluate_claim(self, claim: Claim, rule: Rule) -> Tuple[bool, Dict[str, Any]]:

        rule_def = rule.rule_definition
        logic = rule_def.get('logic', 'AND')
        conditions = rule_def.get('conditions', [])
        
        if not conditions:
            return False, {"error": "No conditions in rule"}
        
     
        condition_results = []
        matched_conditions = []
        
        for idx, condition in enumerate(conditions):
            is_match = self._evaluate_condition(claim, condition)
            condition_results.append(is_match)
            
            if is_match:
   
                actual_value = self._get_claim_field_value(claim, condition.get('field'))
                if isinstance(actual_value, Decimal):
                    actual_value = float(actual_value)
                
                matched_conditions.append({
                    "condition_index": idx,
                    "field": condition.get('field'),
                    "operator": condition.get('operator'),
                    "expected_value": condition.get('value'),
                    "actual_value": actual_value 
                })
        
  
        if logic == 'AND':
            overall_match = all(condition_results)
        elif logic == 'OR':
            overall_match = any(condition_results)
        else:
            return False, {"error": f"Unknown logic type: {logic}"}
        
       
        explanation = self._generate_explanation(
            claim=claim,
            rule=rule,
            matched_conditions=matched_conditions,
            overall_match=overall_match,
            logic=logic
        )
        
        return overall_match, explanation
    
    def _evaluate_condition(self, claim: Claim, condition: Dict[str, Any]) -> bool:
       
        field = condition.get('field')
        operator = condition.get('operator')
        expected_value = condition.get('value')
        
     
        actual_value = self._get_claim_field_value(claim, field)
        
        
        if actual_value is None:
            return False
        
        try:
            return self._apply_operator(actual_value, operator, expected_value)
        except Exception as e:
            print(f"Error evaluating condition: {e}")
            return False
    
    def _get_claim_field_value(self, claim: Claim, field: str) -> Any:
        field_map = {
            'claim_number': claim.claim_number,
            'patient_id': claim.patient_id,
            'drug_code': claim.drug_code,
            'drug_name': claim.drug_name,
            'amount': claim.amount,
            'quantity': claim.quantity,
            'days_supply': claim.days_supply,
            'prescription_date': claim.prescription_date
        }
        
        return field_map.get(field)
    
    def _apply_operator(self, actual_value: Any, operator: str, expected_value: Any) -> bool:

        if isinstance(actual_value, Decimal):
            actual_value = float(actual_value)
        
        # Handle date comparisons
        if isinstance(actual_value, (date, datetime)):
            if isinstance(expected_value, str):
                try:
                    expected_value = datetime.strptime(expected_value, '%Y-%m-%d').date()
                except:
                    return False
        
        string_fields = ['patient_id', 'drug_code', 'drug_name', 'claim_number']
        is_string_value = isinstance(actual_value, str)
        
        if operator == 'CONTAINS':
            if not is_string_value:
                print(f"CONTAINS operator requires string field, got: {type(actual_value)}")
                return False
            return str(expected_value).lower() in str(actual_value).lower()
        
        elif operator == 'STARTS_WITH':
            if not is_string_value:
                print(f"STARTS_WITH operator requires string field, got: {type(actual_value)}")
                return False
            return str(actual_value).lower().startswith(str(expected_value).lower())
        
        elif operator == '=':
            if is_string_value:
                return str(actual_value).lower() == str(expected_value).lower()
            else:
                return actual_value == expected_value
        
        
        elif operator == '!=':
            if is_string_value:
                return str(actual_value).lower() != str(expected_value).lower()
            else:
                return actual_value != expected_value
        
        elif operator == 'IN':
            if isinstance(expected_value, list):
                if is_string_value:
                    return str(actual_value).lower() in [str(v).lower() for v in expected_value]
                else:
                    return actual_value in expected_value
            return False
        
        elif operator == 'NOT_IN':
            if isinstance(expected_value, list):
                if is_string_value:
                    return str(actual_value).lower() not in [str(v).lower() for v in expected_value]
                else:
                    return actual_value not in expected_value
            return True
        
        
        elif operator == '>':
            return actual_value > expected_value
        elif operator == '<':
            return actual_value < expected_value
        elif operator == '>=':
            return actual_value >= expected_value
        elif operator == '<=':
            return actual_value <= expected_value
        
        else:
            print(f"Unknown operator: {operator}")
            return False
    
    def _generate_explanation(
        self,
        claim: Claim,
        rule: Rule,
        matched_conditions: List[Dict],
        overall_match: bool,
        logic: str
    ) -> Dict[str, Any]:
        
        
        serializable_matched_conditions = []
        for mc in matched_conditions:
            mc_copy = mc.copy()
            if isinstance(mc_copy.get('actual_value'), Decimal):
                mc_copy['actual_value'] = float(mc_copy['actual_value'])
            serializable_matched_conditions.append(mc_copy)
        
        explanation = {
            "rule_id": str(rule.id),
            "rule_name": rule.name,
            "rule_version": rule.version,
            "claim_number": claim.claim_number,
            "flagged": overall_match,
            "logic": logic,
            "matched_conditions": serializable_matched_conditions,  
            "total_conditions": len(rule.rule_definition.get('conditions', [])),
            "matched_count": len(matched_conditions)
        }
        
        if overall_match:
            if logic == 'AND':
                explanation["message"] = (
                    f"Claim {claim.claim_number} flagged by rule '{rule.name}': "
                    f"All {len(matched_conditions)} conditions matched."
                )
            else: 
                explanation["message"] = (
                    f"Claim {claim.claim_number} flagged by rule '{rule.name}': "
                    f"{len(matched_conditions)} of {explanation['total_conditions']} conditions matched."
                )
            
            details = []
            for mc in serializable_matched_conditions:
                operator = mc['operator']
                field = mc['field']
                expected = mc['expected_value']
                actual = mc['actual_value']
                
                if operator == 'CONTAINS':
                    detail = f"{field} contains '{expected}' (actual: {actual})"
                elif operator == 'STARTS_WITH':
                    detail = f"{field} starts with '{expected}' (actual: {actual})"
                elif operator == 'IN':
                    detail = f"{field} in {expected} (actual: {actual})"
                elif operator == 'NOT_IN':
                    detail = f"{field} not in {expected} (actual: {actual})"
                else:
                    detail = (
                        f"{field} {operator} {expected} "
                        f"(actual: {actual})"
                    )
                details.append(detail)
            
            explanation["details"] = details
        else:
            explanation["message"] = f"Claim {claim.claim_number} did not match rule '{rule.name}'."
            explanation["details"] = []
        
        return explanation


fraud_engine = FraudEngine()