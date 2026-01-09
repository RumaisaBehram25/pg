"""
Fraud Detection Engine - Core logic for evaluating claims against rules
"""
from sqlalchemy.orm import Session
from sqlalchemy import text, and_, or_
from datetime import datetime, timedelta
from typing import List, Dict, Any
import re
import uuid as uuid_module
from app.models.claim import Claim, Rule, FlaggedClaim
from app.models.blocked_ndc import BlockedNDC


class FraudDetectionEngine:
    
    FIELD_MAPPING = {
        'claim_number': 'claim_id',
        'drug_code': 'ndc',
        'copay': 'copay_amount',
        'plan_paid': 'plan_paid_amount',
        'claim_id': 'claim_id',
        'ndc': 'ndc',
        'copay_amount': 'copay_amount',
        'plan_paid_amount': 'plan_paid_amount',
        'patient_id': 'patient_id',
        'rx_number': 'rx_number',
        'fill_date': 'fill_date',
        'days_supply': 'days_supply',
        'quantity': 'quantity',
        'ingredient_cost': 'ingredient_cost',
        'prescriber_npi': 'prescriber_npi',
        'pharmacy_npi': 'pharmacy_npi',
        'drug_name': 'drug_name',
        'amount': 'amount',
        'prescription_date': 'prescription_date',
        'paid_amount': 'paid_amount',
        'allowed_amount': 'allowed_amount',
        'dispensing_fee': 'dispensing_fee',
    }
    
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        if isinstance(tenant_id, str):
            self.tenant_id = uuid_module.UUID(tenant_id)
        else:
            self.tenant_id = tenant_id
    
    def _map_field(self, field_name: str) -> str:
        return self.FIELD_MAPPING.get(field_name, field_name)
    
    def _get_field_value(self, claim: Claim, field_name: str):
        value = getattr(claim, field_name, None)
        if value is not None:
            return value
        
        mapped_name = self._map_field(field_name)
        if mapped_name != field_name:
            value = getattr(claim, mapped_name, None)
        
        return value
    
    def evaluate_claim(self, claim: Claim, rule: Rule) -> Dict[str, Any]:
        logic_type = rule.logic_type or "THRESHOLD"
        
        evaluators = {
            "THRESHOLD": self._evaluate_threshold,
            "DUPLICATE": self._evaluate_duplicate,
            "DUPLICATE_WINDOW": self._evaluate_duplicate_window,
            "EARLY_REFILL": self._evaluate_early_refill,
            "OVERLAP": self._evaluate_overlap,
            "COUNT_WINDOW": self._evaluate_count_window,
            "RATIO_RANGE": self._evaluate_ratio_range,
            "EXPRESSION_TOLERANCE": self._evaluate_expression_tolerance,
            "FIELD_COMPARE": self._evaluate_field_compare,
            "REGEX": self._evaluate_regex,
            "DATE_COMPARE_TODAY": self._evaluate_date_compare_today,
            "IN_LIST": self._evaluate_in_list,
            "NOT_IN_LIST": self._evaluate_not_in_list,
            "JOIN_EXISTS": self._evaluate_join_exists,
            "CUSTOM_SQL": self._evaluate_custom_sql,
            "ANY_OF": self._evaluate_any_of,
            "JOIN_DATE_RANGE": self._evaluate_join_date_range,
            "JOIN_IN_LIST": self._evaluate_join_in_list,
        }
        
        evaluator = evaluators.get(logic_type)
        if not evaluator:
            return {
                "matched": False, 
                "reason": f"Unknown logic type: {logic_type}",
                "explanation": {
                    "summary": f"Unknown logic type: {logic_type}",
                    "rule_name": rule.name,
                    "logic_type": logic_type
                }
            }
        
        result = evaluator(claim, rule)
        
        if "explanation" in result and isinstance(result["explanation"], str):
            result["explanation"] = {
                "summary": result["explanation"],
                "rule_name": rule.name,
                "logic_type": logic_type
            }
        elif "explanation" not in result:
            result["explanation"] = {
                "summary": f"Rule '{rule.name}' evaluated",
                "rule_name": rule.name,
                "logic_type": logic_type
            }
        
        return result
    
    def _evaluate_threshold(self, claim: Claim, rule: Rule) -> Dict[str, Any]:
        params = rule.parameters if rule.parameters is not None else {}
        rule_def = rule.rule_definition if rule.rule_definition is not None else {}
        
        if not isinstance(params, dict):
            params = {}
        if not isinstance(rule_def, dict):
            rule_def = {}
        
        params_to_use = None
        if params.get("field") and params.get("op") is not None and params.get("value") is not None:
            params_to_use = params
        elif rule_def.get("field") and rule_def.get("op") is not None and rule_def.get("value") is not None:
            params_to_use = rule_def
        
        if params_to_use:
            field = params_to_use.get("field")
            op = params_to_use.get("op")
            value = params_to_use.get("value")
            
            field_value = self._get_field_value(claim, field)
            if field_value is None:
                return {
                    "matched": False,
                    "reason": f"Field {field} is missing",
                    "explanation": {
                        "summary": f"Field {field} is missing",
                        "rule_name": rule.name,
                        "field": field,
                        "matched": False
                    }
                }
            
            try:
                field_value = float(field_value)
                value = float(value)
            except (ValueError, TypeError):
                field_value = str(field_value)
                value = str(value)
            
            if op == ">":
                matched = field_value > value
            elif op == "<":
                matched = field_value < value
            elif op == ">=":
                matched = field_value >= value
            elif op == "<=":
                matched = field_value <= value
            elif op == "==":
                matched = field_value == value
            elif op == "!=":
                matched = field_value != value
            else:
                matched = False
            
            explanation = {
                "summary": f"{rule.name}: {field} ({field_value}) {op} {value}",
                "rule_name": rule.name,
                "field": field,
                "operator": op,
                "threshold": value,
                "actual_value": field_value,
                "matched": matched
            }
            
            return {
                "matched": matched,
                "explanation": explanation
            }
        
        if rule_def.get("field") and rule_def.get("op") is not None and rule_def.get("value") is not None:
            return {
                "matched": False,
                "reason": "Parameters format detected but not evaluated correctly",
                "explanation": {
                    "summary": f"Rule '{rule.name}' has parameters format but evaluation failed",
                    "rule_name": rule.name,
                    "matched": False
                }
            }
        
        logic = rule_def.get("logic", "AND")
        conditions = rule_def.get("conditions", [])
        
        if not isinstance(conditions, list):
            conditions = []
        
        if not conditions:
            return {
                "matched": False,
                "reason": "No conditions defined",
                "explanation": {
                    "summary": f"Rule '{rule.name}' has no conditions",
                    "rule_name": rule.name,
                    "matched": False
                }
            }
        
        results = []
        for condition in conditions:
            if "conditions" in condition:
                nested_result = self._evaluate_nested_conditions(claim, condition)
                results.append(nested_result)
            else:
                result = self._evaluate_single_condition(claim, condition)
                results.append(result)
        
        if logic == "AND":
            matched = all(results)
        elif logic == "OR":
            matched = any(results)
        else:
            matched = False
        
        explanation = {
            "summary": f"Rule '{rule.name}' evaluated",
            "rule_name": rule.name,
            "conditions": conditions,
            "matched": matched
        }
        
        return {
            "matched": matched,
            "conditions": conditions,
            "explanation": explanation
        }
    
    def _evaluate_single_condition(self, claim: Claim, condition: Dict) -> bool:
        field = condition.get("field")
        operator = condition.get("operator")
        value = condition.get("value")
        
        claim_value = self._get_field_value(claim, field)
        if claim_value is None:
            return False
        
        if operator == "CONTAINS":
            return str(value).lower() in str(claim_value).lower()
        elif operator == "STARTS_WITH":
            return str(claim_value).lower().startswith(str(value).lower())
        elif operator == "IN":
            return str(claim_value).lower() in [str(v).lower() for v in value if v]
        elif operator == "NOT_IN":
            return str(claim_value).lower() not in [str(v).lower() for v in value if v]
        elif operator == ">":
            return float(claim_value) > float(value)
        elif operator == "<":
            return float(claim_value) < float(value)
        elif operator == ">=":
            return float(claim_value) >= float(value)
        elif operator == "<=":
            return float(claim_value) <= float(value)
        elif operator == "==":
            return claim_value == value
        elif operator == "!=":
            return claim_value != value
        
        return False
    
    def _evaluate_nested_conditions(self, claim: Claim, condition: Dict) -> bool:
        logic = condition.get("logic", "AND")
        sub_conditions = condition.get("conditions", [])
        
        results = [self._evaluate_single_condition(claim, c) for c in sub_conditions]
        
        if logic == "AND":
            return all(results)
        elif logic == "OR":
            return any(results)
        return False
    
    def _evaluate_duplicate(self, claim: Claim, rule: Rule) -> Dict[str, Any]:
        params = rule.parameters or {}
        keys = params.get("keys", [])
        
        filters = [Claim.tenant_id == self.tenant_id, Claim.id != claim.id]
        
        valid_key_count = 0
        missing_keys = []
        
        for key in keys:
            if key == "tenant_id":
                continue
            mapped_key = self._map_field(key)
            claim_value = self._get_field_value(claim, key)
            if claim_value is not None and claim_value != "":
                filters.append(getattr(Claim, mapped_key) == claim_value)
                valid_key_count += 1
            else:
                missing_keys.append(key)
        
        if valid_key_count == 0:
            return {
                "matched": False,
                "reason": f"Missing key values: {', '.join(missing_keys)}",
                "explanation": {
                    "summary": f"Cannot check duplicates - missing required field values",
                    "rule_name": rule.name,
                    "missing_keys": missing_keys,
                    "matched": False
                }
            }
        
        duplicates = self.db.query(Claim).filter(and_(*filters)).all()
        
        matched = len(duplicates) > 0
        
        return {
            "matched": matched,
            "duplicate_count": len(duplicates),
            "duplicate_ids": [str(d.id) for d in duplicates[:5]],
            "explanation": {
                "summary": f"Found {len(duplicates)} duplicate claim(s)",
                "rule_name": rule.name,
                "duplicate_count": len(duplicates),
                "matching_keys": keys,
                "matched": matched
            }
        }
    
    def _evaluate_duplicate_window(self, claim: Claim, rule: Rule) -> Dict[str, Any]:
        params = rule.parameters or {}
        keys = params.get("keys", [])
        date_field = params.get("date_field", "fill_date")
        window_days = params.get("window_days", 7)
        
        mapped_date_field = self._map_field(date_field)
        claim_date = self._get_field_value(claim, date_field)
        if not claim_date:
            return {
                "matched": False, 
                "reason": f"No {date_field} on claim",
                "explanation": {
                    "summary": f"Cannot check duplicates - missing {date_field}",
                    "rule_name": rule.name,
                    "matched": False
                }
            }
        
        start_date = claim_date - timedelta(days=window_days)
        
        filters = [
            Claim.tenant_id == self.tenant_id,
            Claim.id != claim.id,
            getattr(Claim, mapped_date_field) > start_date,
            getattr(Claim, mapped_date_field) < claim_date
        ]
        
        valid_key_count = 0
        missing_keys = []
        
        for key in keys:
            if key not in ["tenant_id", date_field]:
                mapped_key = self._map_field(key)
                claim_value = self._get_field_value(claim, key)
                if claim_value is not None and claim_value != "":
                    filters.append(getattr(Claim, mapped_key) == claim_value)
                    valid_key_count += 1
                else:
                    missing_keys.append(key)
        
        if valid_key_count == 0 and len([k for k in keys if k not in ["tenant_id", date_field]]) > 0:
            return {
                "matched": False,
                "reason": f"Missing key values: {', '.join(missing_keys)}",
                "explanation": {
                    "summary": f"Cannot check duplicates - missing required field values",
                    "rule_name": rule.name,
                    "missing_keys": missing_keys,
                    "matched": False
                }
            }
        
        duplicates = self.db.query(Claim).filter(and_(*filters)).all()
        
        matched = len(duplicates) > 0
        
        return {
            "matched": matched,
            "duplicate_count": len(duplicates),
            "window_days": window_days,
            "explanation": {
                "summary": f"Found {len(duplicates)} duplicate(s) within {window_days} days",
                "rule_name": rule.name,
                "duplicate_count": len(duplicates),
                "window_days": window_days,
                "matched": matched
            }
        }
    
    def _evaluate_early_refill(self, claim: Claim, rule: Rule) -> Dict[str, Any]:
        params = rule.parameters or {}
        keys = params.get("keys", [])
        date_field = params.get("date_field", "fill_date")
        days_supply_field = params.get("days_supply_field", "days_supply")
        pct = params.get("pct", 0.8)
        
        mapped_date_field = self._map_field(date_field)
        mapped_days_field = self._map_field(days_supply_field)
        
        claim_date = self._get_field_value(claim, date_field)
        if not claim_date:
            return {
                "matched": False, 
                "reason": f"No {date_field}",
                "explanation": {
                    "summary": f"Cannot check early refill - missing {date_field}",
                    "rule_name": rule.name,
                    "matched": False
                }
            }
        
        filters = [
            Claim.tenant_id == self.tenant_id,
            Claim.id != claim.id,
            getattr(Claim, mapped_date_field) < claim_date
        ]
        
        valid_key_count = 0
        missing_keys = []
        
        for key in keys:
            if key not in ["tenant_id", date_field]:
                mapped_key = self._map_field(key)
                claim_value = self._get_field_value(claim, key)
                if claim_value is not None and claim_value != "":
                    filters.append(getattr(Claim, mapped_key) == claim_value)
                    valid_key_count += 1
                else:
                    missing_keys.append(key)
        
        if valid_key_count == 0 and len([k for k in keys if k not in ["tenant_id", date_field]]) > 0:
            return {
                "matched": False,
                "reason": f"Missing key values: {', '.join(missing_keys)}",
                "explanation": {
                    "summary": f"Cannot check early refill - missing required field values",
                    "rule_name": rule.name,
                    "missing_keys": missing_keys,
                    "matched": False
                }
            }
        
        last_fill = (self.db.query(Claim)
                    .filter(and_(*filters))
                    .order_by(getattr(Claim, mapped_date_field).desc())
                    .first())
        
        if not last_fill:
            return {
                "matched": False, 
                "reason": "No previous fill found",
                "explanation": {
                    "summary": "No previous fill found for comparison",
                    "rule_name": rule.name,
                    "matched": False
                }
            }
        
        last_fill_date = self._get_field_value(last_fill, date_field)
        last_days_supply = self._get_field_value(last_fill, days_supply_field) or 30
        
        days_elapsed = (claim_date - last_fill_date).days
        required_days = last_days_supply * pct
        
        matched = days_elapsed < required_days
        
        return {
            "matched": matched,
            "days_elapsed": days_elapsed,
            "required_days": required_days,
            "last_fill_date": str(last_fill_date),
            "explanation": {
                "summary": f"Early refill: {days_elapsed} days elapsed, required {required_days:.0f} days",
                "rule_name": rule.name,
                "days_elapsed": days_elapsed,
                "required_days": required_days,
                "last_fill_date": str(last_fill_date),
                "matched": matched
            }
        }
    
    def _evaluate_overlap(self, claim: Claim, rule: Rule) -> Dict[str, Any]:
        params = rule.parameters or {}
        keys = params.get("keys", [])
        date_field = params.get("date_field", "fill_date")
        days_supply_field = params.get("days_supply_field", "days_supply")
        
        mapped_date_field = self._map_field(date_field)
        mapped_days_field = self._map_field(days_supply_field)
        
        claim_date = self._get_field_value(claim, date_field)
        claim_days = self._get_field_value(claim, days_supply_field) or 0
        
        if not claim_date or not claim_days:
            return {
                "matched": False, 
                "reason": "Missing date or days_supply",
                "explanation": {
                    "summary": f"Cannot check overlap - missing {date_field} or {days_supply_field}",
                    "rule_name": rule.name,
                    "matched": False
                }
            }
        
        claim_end_date = claim_date + timedelta(days=claim_days)
        
        filters = [
            Claim.tenant_id == self.tenant_id,
            Claim.id != claim.id
        ]
        
        valid_key_count = 0
        missing_keys = []
        
        for key in keys:
            if key not in ["tenant_id", date_field, days_supply_field]:
                mapped_key = self._map_field(key)
                claim_value = self._get_field_value(claim, key)
                if claim_value is not None and claim_value != "":
                    filters.append(getattr(Claim, mapped_key) == claim_value)
                    valid_key_count += 1
                else:
                    missing_keys.append(key)
        
        if valid_key_count == 0 and len([k for k in keys if k not in ["tenant_id", date_field, days_supply_field]]) > 0:
            return {
                "matched": False,
                "reason": f"Missing key values: {', '.join(missing_keys)}",
                "explanation": {
                    "summary": f"Cannot check overlap - missing required field values",
                    "rule_name": rule.name,
                    "missing_keys": missing_keys,
                    "matched": False
                }
            }
        
        potential_overlaps = self.db.query(Claim).filter(and_(*filters)).all()
        
        overlaps = []
        for other in potential_overlaps:
            other_date = self._get_field_value(other, date_field)
            other_days = self._get_field_value(other, days_supply_field) or 0
            
            if not other_date or not other_days:
                continue
            
            other_end_date = other_date + timedelta(days=other_days)
            
            if not (claim_end_date <= other_date or claim_date >= other_end_date):
                overlaps.append(other)
        
        matched = len(overlaps) > 0
        
        return {
            "matched": matched,
            "overlap_count": len(overlaps),
            "explanation": {
                "summary": f"Found {len(overlaps)} overlapping prescription(s)",
                "rule_name": rule.name,
                "overlap_count": len(overlaps),
                "matched": matched
            }
        }
    
    def _evaluate_count_window(self, claim: Claim, rule: Rule) -> Dict[str, Any]:
        params = rule.parameters or {}
        keys = params.get("keys", [])
        date_field = params.get("date_field", "fill_date")
        window_days = params.get("window_days", 90)
        max_count = params.get("max_count", 3)
        
        mapped_date_field = self._map_field(date_field)
        
        claim_date = self._get_field_value(claim, date_field)
        if not claim_date:
            return {
                "matched": False, 
                "reason": f"No {date_field}",
                "explanation": {
                    "summary": f"Cannot count fills - missing {date_field}",
                    "rule_name": rule.name,
                    "matched": False
                }
            }
        
        start_date = claim_date - timedelta(days=window_days)
        
        filters = [
            Claim.tenant_id == self.tenant_id,
            getattr(Claim, mapped_date_field) >= start_date,
            getattr(Claim, mapped_date_field) <= claim_date
        ]
        
        valid_key_count = 0
        missing_keys = []
        
        for key in keys:
            if key not in ["tenant_id", date_field]:
                mapped_key = self._map_field(key)
                claim_value = self._get_field_value(claim, key)
                if claim_value is not None and claim_value != "":
                    filters.append(getattr(Claim, mapped_key) == claim_value)
                    valid_key_count += 1
                else:
                    missing_keys.append(key)
        
        if valid_key_count == 0 and len([k for k in keys if k not in ["tenant_id", date_field]]) > 0:
            return {
                "matched": False,
                "reason": f"Missing key values: {', '.join(missing_keys)}",
                "explanation": {
                    "summary": f"Cannot count fills - missing required field values",
                    "rule_name": rule.name,
                    "missing_keys": missing_keys,
                    "matched": False
                }
            }
        
        count = self.db.query(Claim).filter(and_(*filters)).count()
        
        matched = count > max_count
        
        return {
            "matched": matched,
            "count": count,
            "max_count": max_count,
            "window_days": window_days,
            "explanation": {
                "summary": f"Found {count} fill(s) in {window_days} days, max allowed {max_count}",
                "rule_name": rule.name,
                "count": count,
                "max_count": max_count,
                "window_days": window_days,
                "matched": matched
            }
        }
    
    
    def _evaluate_ratio_range(self, claim: Claim, rule: Rule) -> Dict[str, Any]:
        params = rule.parameters or {}
        numerator = params.get("numerator", "quantity")
        denominator = params.get("denominator", "days_supply")
        min_ratio = params.get("min", 0.1)
        max_ratio = params.get("max", 20.0)
        
        num_value = self._get_field_value(claim, numerator)
        den_value = self._get_field_value(claim, denominator)
        
        if not num_value or not den_value or den_value == 0:
            return {"matched": False, "reason": "Missing or zero denominator"}
        
        ratio = float(num_value) / float(den_value)
        matched = ratio < min_ratio or ratio > max_ratio
        
        return {
            "matched": matched,
            "ratio": ratio,
            "min_ratio": min_ratio,
            "max_ratio": max_ratio,
            "explanation": {
                "summary": f"Ratio {ratio:.2f} outside range [{min_ratio}, {max_ratio}]",
                "rule_name": rule.name,
                "ratio": ratio,
                "min_ratio": min_ratio,
                "max_ratio": max_ratio,
                "numerator": numerator,
                "denominator": denominator,
                "matched": matched
            }
        }
    
    def _evaluate_expression_tolerance(self, claim: Claim, rule: Rule) -> Dict[str, Any]:
        params = rule.parameters or {}
        lhs = params.get("lhs", "paid_amount")
        rhs = params.get("rhs", ["plan_paid", "copay"])
        rhs_op = params.get("rhs_op", "+")
        tolerance = params.get("tolerance", 0.01)
        
        lhs_value = self._get_field_value(claim, lhs)
        if lhs_value is None:
            return {"matched": False, "reason": f"Missing {lhs}"}
        
        rhs_value = 0
        for field in rhs:
            field_value = self._get_field_value(claim, field) or 0
            if rhs_op == "+":
                rhs_value += float(field_value)
            elif rhs_op == "-":
                rhs_value -= float(field_value)
        
        difference = abs(float(lhs_value) - rhs_value)
        matched = difference > tolerance
        
        return {
            "matched": matched,
            "lhs_value": float(lhs_value),
            "rhs_value": rhs_value,
            "difference": difference,
            "tolerance": tolerance,
            "explanation": {
                "summary": f"{lhs} ({lhs_value}) vs calculated ({rhs_value:.2f}), difference: {difference:.2f} (tolerance: {tolerance})",
                "rule_name": rule.name,
                "lhs": lhs,
                "lhs_value": float(lhs_value),
                "rhs": rhs,
                "rhs_value": rhs_value,
                "difference": difference,
                "tolerance": tolerance,
                "matched": matched
            }
        }
    
    def _evaluate_field_compare(self, claim: Claim, rule: Rule) -> Dict[str, Any]:
        params = rule.parameters or {}
        left = params.get("left", "copay")
        right = params.get("right", "allowed_amount")
        op = params.get("op", ">")
        
        left_value = self._get_field_value(claim, left)
        right_value = self._get_field_value(claim, right)
        
        if left_value is None or right_value is None:
            return {"matched": False, "reason": "Missing field values"}
        
        left_value = float(left_value)
        right_value = float(right_value)
        
        if op == ">":
            matched = left_value > right_value
        elif op == "<":
            matched = left_value < right_value
        elif op == ">=":
            matched = left_value >= right_value
        elif op == "<=":
            matched = left_value <= right_value
        elif op == "==":
            matched = left_value == right_value
        elif op == "!=":
            matched = left_value != right_value
        else:
            matched = False
        
        return {
            "matched": matched,
            "left_value": left_value,
            "right_value": right_value,
            "operator": op,
            "explanation": {
                "summary": f"{left} ({left_value}) {op} {right} ({right_value})",
                "rule_name": rule.name,
                "left_field": left,
                "left_value": left_value,
                "right_field": right,
                "right_value": right_value,
                "operator": op,
                "matched": matched
            }
        }
    
    def _evaluate_regex(self, claim: Claim, rule: Rule) -> Dict[str, Any]:
        params = rule.parameters or {}
        field = params.get("field", "prescriber_npi")
        pattern = params.get("pattern", "^[0-9]{10}$")
        null_is_fail = params.get("null_is_fail", False)
        case_insensitive = params.get("case_insensitive", False)
        
        # Smart default for match_means_valid:
        # If null_is_fail is True, this is likely a validation rule (checking required format)
        # If pattern starts with ^ and ends with $, it's a format validation pattern
        # In both cases, default match_means_valid to True
        if "match_means_valid" in params:
            match_means_valid = params.get("match_means_valid")
        else:
            # Auto-detect: validation rules should flag when pattern DOESN'T match
            is_format_validation = (pattern.startswith("^") and pattern.endswith("$")) or null_is_fail
            match_means_valid = is_format_validation
        
        field_value = self._get_field_value(claim, field)
        
        # Handle null/empty values
        if field_value is None or str(field_value).strip() == "":
            matched = null_is_fail
            return {
                "matched": matched,
                "reason": f"{field} is null/empty",
                "explanation": {
                    "summary": f"{field} is null/empty, null_is_fail={null_is_fail}",
                    "rule_name": rule.name,
                    "field": field,
                    "field_value": None,
                    "pattern": pattern,
                    "null_is_fail": null_is_fail,
                    "matched": matched
                }
            }
        
        # Check pattern match
        flags = re.IGNORECASE if case_insensitive else 0
        regex_match = re.search(pattern, str(field_value), flags)
        pattern_matched = bool(regex_match)
        
        # Determine if claim should be flagged
        if match_means_valid:
            # Validation mode: flag when pattern DOESN'T match (invalid format)
            matched = not pattern_matched
        else:
            # Monitoring mode: flag when pattern MATCHES (suspicious content)
            matched = pattern_matched
        
        return {
            "matched": matched,
            "field_value": str(field_value),
            "pattern": pattern,
            "pattern_matched": pattern_matched,
            "match_means_valid": match_means_valid,
            "explanation": {
                "summary": f"{field} '{field_value}' {'matches' if pattern_matched else 'does not match'} pattern, match_means_valid={match_means_valid}, flagged={matched}",
                "rule_name": rule.name,
                "field": field,
                "field_value": str(field_value),
                "pattern": pattern,
                "pattern_matched": pattern_matched,
                "match_means_valid": match_means_valid,
                "matched": matched
            }
        }
    
    def _evaluate_date_compare_today(self, claim: Claim, rule: Rule) -> Dict[str, Any]:
        params = rule.parameters or {}
        field = params.get("field", "fill_date")
        op = params.get("op", ">")
        allowed_future_days = params.get("allowed_future_days", 0)
        
        field_value = self._get_field_value(claim, field)
        if not field_value:
            return {"matched": False, "reason": f"No {field}"}
        
        today = datetime.now().date()
        if isinstance(field_value, datetime):
            field_value = field_value.date()
        
        max_allowed_date = today + timedelta(days=allowed_future_days)
        
        if op == ">":
            matched = field_value > max_allowed_date
        elif op == "<":
            matched = field_value < today
        elif op == ">=":
            matched = field_value >= max_allowed_date
        elif op == "<=":
            matched = field_value <= today
        else:
            matched = False
        
        return {
            "matched": matched,
            "field_value": str(field_value),
            "today": str(today),
            "operator": op,
            "explanation": {
                "summary": f"{field} ({field_value}) {op} today ({today})",
                "rule_name": rule.name,
                "field": field,
                "field_value": str(field_value),
                "today": str(today),
                "operator": op,
                "allowed_future_days": allowed_future_days,
                "matched": matched
            }
        }
    
    def _evaluate_in_list(self, claim: Claim, rule: Rule) -> Dict[str, Any]:
        params = rule.parameters or {}
        field = params.get("field", "drug_code")
        list_ref = params.get("list_ref", "blocked_ndc")
        
        field_value = self._get_field_value(claim, field)
        if not field_value:
            return {"matched": False, "reason": f"No {field}"}
        
        if list_ref == "blocked_ndc":
            exists = self.db.query(BlockedNDC).filter(
                BlockedNDC.tenant_id == self.tenant_id,
                BlockedNDC.drug_code == field_value
            ).first()
            
            matched = exists is not None
            
            return {
                "matched": matched,
                "field_value": field_value,
                "list_ref": list_ref,
                "explanation": {
                    "summary": f"{field} '{field_value}' {'found' if matched else 'not found'} in {list_ref}",
                    "rule_name": rule.name,
                    "field": field,
                    "field_value": field_value,
                    "list_ref": list_ref,
                    "matched": matched
                }
            }
        
        return {"matched": False, "reason": f"Unknown list_ref: {list_ref}"}
    
    def _evaluate_not_in_list(self, claim: Claim, rule: Rule) -> Dict[str, Any]:
        params = rule.parameters or {}
        field = params.get("field", "plan_id")
        allowed_values = params.get("allowed_values", [])
        null_is_fail = params.get("null_is_fail", True)
        
        field_value = self._get_field_value(claim, field)
        
        if not field_value:
            if null_is_fail:
                return {
                    "matched": True,
                    "field_value": None,
                    "allowed_values": allowed_values,
                    "explanation": {
                        "summary": f"{field} is empty/null and not in allowed values",
                        "rule_name": rule.name,
                        "field": field,
                        "field_value": None,
                        "allowed_values": allowed_values,
                        "matched": True
                    }
                }
            else:
                return {"matched": False, "reason": f"No {field} (null_is_fail=False)"}
        
        field_value_upper = str(field_value).upper().strip()
        allowed_values_upper = [str(v).upper().strip() for v in allowed_values]
        
        is_in_list = field_value_upper in allowed_values_upper
        matched = not is_in_list
        
        return {
            "matched": matched,
            "field_value": field_value,
            "allowed_values": allowed_values,
            "explanation": {
                "summary": f"{field} '{field_value}' {'not in' if matched else 'in'} allowed list",
                "rule_name": rule.name,
                "field": field,
                "field_value": field_value,
                "allowed_values": allowed_values,
                "is_allowed": is_in_list,
                "matched": matched
            }
        }
    
    def _evaluate_join_exists(self, claim: Claim, rule: Rule) -> Dict[str, Any]:
        params = rule.parameters or {}
        lookup_table = params.get("lookup_table")
        join_keys = params.get("join_keys", [])
        
        return {
            "matched": False,
            "reason": "JOIN_EXISTS not fully implemented in Phase 1 (requires eligibility/network tables)",
            "explanation": {
                "summary": f"JOIN_EXISTS to {lookup_table} not implemented",
                "rule_name": rule.name,
                "lookup_table": lookup_table,
                "matched": False
            }
        }
    
    def _evaluate_custom_sql(self, claim: Claim, rule: Rule) -> Dict[str, Any]:
        params = rule.parameters or {}
        sql = params.get("sql", "")
        
        return {
            "matched": False,
            "reason": "CUSTOM_SQL disabled for security (Phase 1)",
            "explanation": {
                "summary": "CUSTOM_SQL rules are disabled in Phase 1 for security",
                "rule_name": rule.name,
                "note": "Enable this rule manually after validating SQL query",
                "matched": False
            }
        }
    
    def _evaluate_any_of(self, claim: Claim, rule: Rule) -> Dict[str, Any]:
        params = rule.parameters or {}
        conditions = params.get("conditions", [])
        
        if not conditions:
            return {
                "matched": False,
                "reason": "No conditions defined",
                "explanation": {
                    "summary": f"Rule '{rule.name}' has no conditions",
                    "rule_name": rule.name,
                    "matched": False
                }
            }
        
        matched_conditions = []
        
        for condition in conditions:
            field = condition.get("field")
            op = condition.get("op")
            value = condition.get("value")
            
            field_value = self._get_field_value(claim, field)
            
            condition_matched = False
            if op == "=":
                condition_matched = field_value == value
            elif op == "IS_NULL":
                condition_matched = (field_value is None) == value
            elif op == ">":
                condition_matched = field_value and float(field_value) > float(value)
            elif op == "<":
                condition_matched = field_value and float(field_value) < float(value)
            
            if condition_matched:
                matched_conditions.append({
                    "field": field,
                    "operator": op,
                    "expected": value,
                    "actual": field_value
                })
        
        matched = len(matched_conditions) > 0
        
        return {
            "matched": matched,
            "matched_conditions": matched_conditions,
            "total_conditions": len(conditions),
            "explanation": {
                "summary": f"{len(matched_conditions)} of {len(conditions)} conditions matched",
                "rule_name": rule.name,
                "matched_conditions": matched_conditions,
                "matched": matched
            }
        }
    
    def _evaluate_join_date_range(self, claim: Claim, rule: Rule) -> Dict[str, Any]:
        params = rule.parameters or {}
        lookup_table = params.get("lookup_table")
        join_keys = params.get("join_keys", [])
        date_field = params.get("date_field", "fill_date")
        start_field = params.get("start_field", "eligibility_start")
        end_field = params.get("end_field", "eligibility_end")
        
        return {
            "matched": False,
            "reason": "JOIN_DATE_RANGE not implemented in Phase 1 (requires eligibility table)",
            "explanation": {
                "summary": f"JOIN_DATE_RANGE to {lookup_table} not implemented",
                "rule_name": rule.name,
                "lookup_table": lookup_table,
                "matched": False
            }
        }
    
    def _evaluate_join_in_list(self, claim: Claim, rule: Rule) -> Dict[str, Any]:
        params = rule.parameters or {}
        lookup_table = params.get("lookup_table")
        join_keys = params.get("join_keys", [])
        value_field = params.get("value_field")
        claim_field = params.get("claim_field")
        
        return {
            "matched": False,
            "reason": "JOIN_IN_LIST not implemented in Phase 1 (requires authorization tables)",
            "explanation": {
                "summary": f"JOIN_IN_LIST to {lookup_table} not implemented",
                "rule_name": rule.name,
                "lookup_table": lookup_table,
                "matched": False
            }
        }


def fraud_engine(db: Session, tenant_id: str):
    return FraudDetectionEngine(db, tenant_id)