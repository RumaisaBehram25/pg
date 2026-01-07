from datetime import datetime, date
from typing import Dict, Optional, List, Set
from dataclasses import dataclass
import re


@dataclass
class ValidationError:
    row_number: int
    error_code: str
    error_message: str
    field_name: Optional[str] = None


class CSVValidator:
    
    MAX_AMOUNT = 100000.00
    MIN_AMOUNT = 0.00
    MAX_DAYS_SUPPLY = 365
    MIN_DAYS_SUPPLY = 1
    MAX_QUANTITY = 99999
    MIN_QUANTITY = 1
    
    MAX_FIELD_LENGTH = {
        'claim_id': 100,
        'patient_id': 100,
        'ndc': 50,
        'drug_name': 255,
        'rx_number': 50,
        'prescriber_npi': 10,
        'pharmacy_npi': 10,
        'plan_id': 100,
        'state': 2,
    }
    
    REQUIRED_FIELDS = ['claim_id', 'patient_id', 'ndc', 'fill_date', 'days_supply', 'quantity']
    
    VALID_CLAIM_STATUSES = {'PAID', 'REVERSED'}
    
    VALID_STATES = {
        'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
        'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
        'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
        'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
        'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY',
        'DC', 'PR', 'VI', 'GU', 'AS', 'MP'
    }
    
    def __init__(self):
        self.seen_claim_ids: Set[str] = set()
        self.errors: List[ValidationError] = []
    
    def validate_row(self, row: Dict[str, str], row_number: int) -> Optional[ValidationError]:
        
        error = self._validate_required_fields(row, row_number)
        if error:
            return error
        
        error = self._validate_field_lengths(row, row_number)
        if error:
            return error
        
        error = self._validate_duplicate_claim(row, row_number)
        if error:
            return error
        
        error = self._validate_quantity(row, row_number)
        if error:
            return error
        
        error = self._validate_days_supply(row, row_number)
        if error:
            return error
        
        error = self._validate_fill_date(row, row_number)
        if error:
            return error
        
        error = self._validate_ndc(row, row_number)
        if error:
            return error
        
        error = self._validate_npi_fields(row, row_number)
        if error:
            return error
        
        error = self._validate_claim_status(row, row_number)
        if error:
            return error
        
        error = self._validate_state(row, row_number)
        if error:
            return error
        
        error = self._validate_amounts(row, row_number)
        if error:
            return error
        
        return None
    
    def _validate_required_fields(self, row: Dict[str, str], row_number: int) -> Optional[ValidationError]:
        for field in self.REQUIRED_FIELDS:
            value = row.get(field, '').strip()
            if not value:
                return ValidationError(
                    row_number=row_number,
                    error_code="E001",
                    error_message=f"Required field missing or empty: {field}",
                    field_name=field
                )
        return None
    
    def _validate_duplicate_claim(self, row: Dict[str, str], row_number: int) -> Optional[ValidationError]:
        claim_id = row.get('claim_id', '').strip()
        
        if claim_id in self.seen_claim_ids:
            return ValidationError(
                row_number=row_number,
                error_code="E002",
                error_message=f"Duplicate claim_id in this file: {claim_id}",
                field_name='claim_id'
            )
        
        self.seen_claim_ids.add(claim_id)
        return None
    
    def _validate_ndc(self, row: Dict[str, str], row_number: int) -> Optional[ValidationError]:
        ndc = row.get('ndc', '').strip()
        
        if not ndc:
            return None
        
        ndc_pattern = r'^(\d{4,5}-\d{3,4}-\d{1,2}|\d{10,11})$'
        
        if not re.match(ndc_pattern, ndc):
            return ValidationError(
                row_number=row_number,
                error_code="E011",
                error_message=f"Invalid NDC format: '{ndc}' (expected format: XXXXX-XXXX-XX or 11 digits)",
                field_name='ndc'
            )
        
        return None
    
    def _validate_quantity(self, row: Dict[str, str], row_number: int) -> Optional[ValidationError]:
        quantity_str = row.get('quantity', '').strip()
        
        if not quantity_str:
            return None
        
        try:
            quantity = int(float(quantity_str))
            
            if quantity < self.MIN_QUANTITY:
                return ValidationError(
                    row_number=row_number,
                    error_code="E007",
                    error_message=f"Quantity must be at least {self.MIN_QUANTITY}: {quantity}",
                    field_name='quantity'
                )
            
            if quantity > self.MAX_QUANTITY:
                return ValidationError(
                    row_number=row_number,
                    error_code="E007",
                    error_message=f"Quantity too high: {quantity} (maximum: {self.MAX_QUANTITY})",
                    field_name='quantity'
                )
            
        except (ValueError, TypeError):
            return ValidationError(
                row_number=row_number,
                error_code="E007",
                error_message=f"Invalid quantity: '{quantity_str}' (must be a whole number)",
                field_name='quantity'
            )
        
        return None
    
    def _validate_days_supply(self, row: Dict[str, str], row_number: int) -> Optional[ValidationError]:
        days_str = row.get('days_supply', '').strip()
        
        if not days_str:
            return None
        
        try:
            days_supply = int(float(days_str))
            
            if days_supply < self.MIN_DAYS_SUPPLY:
                return ValidationError(
                    row_number=row_number,
                    error_code="E008",
                    error_message=f"Days supply must be at least {self.MIN_DAYS_SUPPLY}: {days_supply}",
                    field_name='days_supply'
                )
            
            if days_supply > self.MAX_DAYS_SUPPLY:
                return ValidationError(
                    row_number=row_number,
                    error_code="E008",
                    error_message=f"Days supply too high: {days_supply} (maximum: {self.MAX_DAYS_SUPPLY})",
                    field_name='days_supply'
                )
            
        except (ValueError, TypeError):
            return ValidationError(
                row_number=row_number,
                error_code="E008",
                error_message=f"Invalid days_supply: '{days_str}' (must be a whole number)",
                field_name='days_supply'
            )
        
        return None
    
    def _validate_fill_date(self, row: Dict[str, str], row_number: int) -> Optional[ValidationError]:
        date_str = row.get('fill_date', '').strip()
        
        if not date_str:
            return None
        
        parsed_date = None
        for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%m/%d/%Y', '%d/%m/%Y']:
            try:
                parsed_date = datetime.strptime(date_str, fmt).date()
                break
            except ValueError:
                continue
        
        if parsed_date is None:
            return ValidationError(
                row_number=row_number,
                error_code="E009",
                error_message=f"Invalid date format: '{date_str}' (use YYYY-MM-DD, e.g., 2025-12-25)",
                field_name='fill_date'
            )
        
        return None
    
    def _validate_npi_fields(self, row: Dict[str, str], row_number: int) -> Optional[ValidationError]:
        return None
    
    def _validate_claim_status(self, row: Dict[str, str], row_number: int) -> Optional[ValidationError]:
        status = row.get('claim_status', '').strip().upper()
        
        if not status:
            return None
        
        if status not in self.VALID_CLAIM_STATUSES:
            return ValidationError(
                row_number=row_number,
                error_code="E014",
                error_message=f"Invalid claim_status: '{status}' (must be PAID or REVERSED)",
                field_name='claim_status'
            )
        
        return None
    
    def _validate_state(self, row: Dict[str, str], row_number: int) -> Optional[ValidationError]:
        state = row.get('state', '').strip().upper()
        
        if not state:
            return None
        
        if state not in self.VALID_STATES:
            return ValidationError(
                row_number=row_number,
                error_code="E015",
                error_message=f"Invalid state code: '{state}' (must be valid US state)",
                field_name='state'
            )
        
        return None
    
    def _validate_amounts(self, row: Dict[str, str], row_number: int) -> Optional[ValidationError]:
        
        amount_fields = ['copay_amount', 'plan_paid_amount', 'ingredient_cost', 'usual_and_customary']
        
        for field in amount_fields:
            amount_str = row.get(field, '').strip()
            
            if not amount_str:
                continue
            
            try:
                amount = float(amount_str)
                
                if amount > self.MAX_AMOUNT:
                    return ValidationError(
                        row_number=row_number,
                        error_code="E016",
                        error_message=f"Amount too high for {field}: ${amount:.2f} (maximum: ${self.MAX_AMOUNT:.2f})",
                        field_name=field
                    )
                
            except (ValueError, TypeError):
                return ValidationError(
                    row_number=row_number,
                    error_code="E016",
                    error_message=f"Invalid {field} format: '{amount_str}' (must be a valid number)",
                    field_name=field
                )
        
        return None
    
    def _validate_field_lengths(self, row: Dict[str, str], row_number: int) -> Optional[ValidationError]:
        for field, max_length in self.MAX_FIELD_LENGTH.items():
            value = row.get(field, '').strip()
            
            if len(value) > max_length:
                return ValidationError(
                    row_number=row_number,
                    error_code="E010",
                    error_message=f"Field '{field}' too long: {len(value)} characters (maximum: {max_length})",
                    field_name=field
                )
        
        return None
    
    def reset(self):
        self.seen_claim_ids.clear()
        self.errors.clear()
