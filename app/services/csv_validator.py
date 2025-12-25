
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

    MAX_AMOUNT = 10000.00
    MIN_AMOUNT = 0.01
    MAX_DAYS_SUPPLY = 365
    MIN_DAYS_SUPPLY = 1
    MAX_QUANTITY = 9999
    MIN_QUANTITY = 1
    
    MAX_FIELD_LENGTH = {
        'claim_number': 100,
        'patient_id': 100,
        'drug_code': 50,
        'drug_name': 255,
    }
    
    REQUIRED_FIELDS = ['claim_number', 'patient_id', 'drug_code', 'amount']
    
    def __init__(self):
        self.seen_claim_numbers: Set[str] = set()
        self.errors: List[ValidationError] = []
    
    def validate_row(self, row: Dict[str, str], row_number: int) -> Optional[ValidationError]:

        
        # E001: Required fields validation
        error = self._validate_required_fields(row, row_number)
        if error:
            return error
        
        # E010: Field length validation
        error = self._validate_field_lengths(row, row_number)
        if error:
            return error
        
        # E002: Duplicate detection (WITHIN THIS FILE ONLY)
        error = self._validate_duplicate_claim(row, row_number)
        if error:
            return error
        
        # E003, E004, E005: Amount validation
        error = self._validate_amount(row, row_number)
        if error:
            return error
        
        # E011: Drug code format validation
        error = self._validate_drug_code(row, row_number)
        if error:
            return error
        
        # E007: Quantity validation
        error = self._validate_quantity(row, row_number)
        if error:
            return error
        
        # E008: Days supply validation
        error = self._validate_days_supply(row, row_number)
        if error:
            return error
        
        # E009, E012: Date validation
        error = self._validate_prescription_date(row, row_number)
        if error:
            return error
        
        # All validations passed
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
        claim_number = row.get('claim_number', '').strip()
        
        if claim_number in self.seen_claim_numbers:
            return ValidationError(
                row_number=row_number,
                error_code="E002",
                error_message=f"Duplicate claim_number in this file: {claim_number}",
                field_name='claim_number'
            )
        
        self.seen_claim_numbers.add(claim_number)
        return None
    
    def _validate_amount(self, row: Dict[str, str], row_number: int) -> Optional[ValidationError]:
        amount_str = row.get('amount', '').strip()
        
        # E003: Check format
        try:
            amount = float(amount_str)
        except (ValueError, TypeError):
            return ValidationError(
                row_number=row_number,
                error_code="E003",
                error_message=f"Invalid amount format: '{amount_str}' (must be a valid number)",
                field_name='amount'
            )
        
        # E004: Check if positive
        if amount <= 0:
            return ValidationError(
                row_number=row_number,
                error_code="E004",
                error_message=f"Amount must be greater than zero: ${amount:.2f}",
                field_name='amount'
            )
        
        # E005: Check if suspiciously high
        if amount > self.MAX_AMOUNT:
            return ValidationError(
                row_number=row_number,
                error_code="E005",
                error_message=f"Amount suspiciously high: ${amount:.2f} (maximum: ${self.MAX_AMOUNT:.2f})",
                field_name='amount'
            )
        
        return None
    
    def _validate_drug_code(self, row: Dict[str, str], row_number: int) -> Optional[ValidationError]:
        """Validate drug code format."""
        drug_code = row.get('drug_code', '').strip()
        
        if not drug_code:
            return None
        
        # Only alphanumeric and hyphens allowed
        if not re.match(r'^[A-Za-z0-9\-]+$', drug_code):
            return ValidationError(
                row_number=row_number,
                error_code="E011",
                error_message=f"Invalid drug code format: '{drug_code}' (only letters, numbers, and hyphens allowed)",
                field_name='drug_code'
            )
        
        return None
    
    def _validate_quantity(self, row: Dict[str, str], row_number: int) -> Optional[ValidationError]:
        """Validate quantity field (optional)."""
        quantity_str = row.get('quantity', '').strip()
        
        if not quantity_str:
            return None
        
        try:
            quantity = int(quantity_str)
            
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
            days_supply = int(days_str)
            
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
    
    def _validate_prescription_date(self, row: Dict[str, str], row_number: int) -> Optional[ValidationError]:
        date_str = row.get('prescription_date', '').strip()
        
        if not date_str:
            return None
        
        # E009: Validate date format
        try:
            prescription_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return ValidationError(
                row_number=row_number,
                error_code="E009",
                error_message=f"Invalid date format: '{date_str}' (use YYYY-MM-DD, e.g., 2024-12-25)",
                field_name='prescription_date'
            )
        
        # E012: Check if future date
        if prescription_date > date.today():
            return ValidationError(
                row_number=row_number,
                error_code="E012",
                error_message=f"Prescription date cannot be in the future: {date_str}",
                field_name='prescription_date'
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
        self.seen_claim_numbers.clear()
        self.errors.clear()