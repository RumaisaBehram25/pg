
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
        
        if isinstance(actual_value, (date, datetime)):
            if isinstance(expected_value, str):
                try:
                    expected_value = datetime.strptime(expected_value, '%Y-%m-%d').date()
                except:
                    return False
        
        if operator == '>':
            return actual_value > expected_value
        elif operator == '<':
            return actual_value < expected_value
        elif operator == '>=':
            return actual_value >= expected_value
        elif operator == '<=':
            return actual_value <= expected_value
        elif operator == '=':
            return actual_value == expected_value
        elif operator == '!=':
            return actual_value != expected_value
        elif operator == 'IN':
            if isinstance(expected_value, list):
                return actual_value in expected_value
            return False
        elif operator == 'NOT_IN':
            if isinstance(expected_value, list):
                return actual_value not in expected_value
            return True
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
            "matched_conditions": serializable_matched_conditions,  # ✅ All Decimals converted
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
                detail = (
                    f"{mc['field']} {mc['operator']} {mc['expected_value']} "
                    f"(actual: {mc['actual_value']})"
                )
                details.append(detail)
            
            explanation["details"] = details
        else:
            explanation["message"] = f"Claim {claim.claim_number} did not match rule '{rule.name}'."
            explanation["details"] = []
        
        return explanation


fraud_engine = FraudEngine()