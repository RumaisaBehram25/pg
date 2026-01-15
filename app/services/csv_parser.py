import csv
import os
from io import StringIO


def read_csv_file(file_path=None, csv_content=None):
    """
    Read CSV from either file path OR csv_content string
    
    Args:
        file_path: Path to CSV file (legacy support)
        csv_content: CSV content as string (new method for Koyeb)
    """
    
    # NEW: If csv_content is provided, use it directly
    if csv_content is not None:
        return _parse_csv_content(csv_content)
    
    # OLD: Fallback to file reading (for local development)
    if file_path:
        if not os.path.exists(file_path):
            raise ValueError(f"File not found: {file_path}")
        
        encodings = ['utf-8-sig', 'utf-16', 'utf-8', 'latin-1']
        
        for encoding in encodings:
            try:
                with open(file_path, mode='r', encoding=encoding) as f:
                    content = f.read()
                return _parse_csv_content(content)
            except UnicodeError:
                continue
            except Exception as e:
                continue
        
        raise ValueError(f"Failed to read file: {file_path}. Ensure it is a valid CSV with supported encoding (UTF-8, UTF-16).")
    
    raise ValueError("Must provide either file_path or csv_content")


def _parse_csv_content(content):
    """
    Parse CSV content string into list of dicts
    
    Args:
        content: CSV content as string
    
    Returns:
        List of dicts with cleaned data
    """
    encodings_to_try = ['utf-8-sig', 'utf-16', 'utf-8', 'latin-1']
    
    for encoding in encodings_to_try:
        try:
            # If content is bytes, decode it
            if isinstance(content, bytes):
                content = content.decode(encoding)
            
            f_io = StringIO(content)
            reader = csv.DictReader(f_io)
            
            if reader.fieldnames is None:
                return []
            
            data = []
            f_io.seek(0)
            reader = csv.DictReader(f_io)
            
            for row in reader:
                clean_row = {}
                for k, v in row.items():
                    if k:
                        clean_k = k.strip()
                        clean_v = v.strip() if v else v
                        clean_row[clean_k] = clean_v
                data.append(clean_row)
            
            return data
            
        except (UnicodeError, UnicodeDecodeError):
            continue
        except Exception as e:
            continue
    
    raise ValueError("Failed to parse CSV content. Ensure it is valid CSV with supported encoding.")