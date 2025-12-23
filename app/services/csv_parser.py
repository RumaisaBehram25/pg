"""
CSV Parser with multi-encoding support
Hafsa's contribution
"""
import csv
import os
from io import StringIO


def read_csv_file(file_path):
    """
    Reads a CSV file, handles encoding issues, and returns the data as a list of dictionaries.
    
    Args:
        file_path (str): The path to the CSV file.
        
    Returns:
        list: A list of dictionaries, where each dictionary represents a row.
        
    Raises:
        ValueError: If the file cannot be read or has an unsupported encoding.
    """
    if not os.path.exists(file_path):
        raise ValueError(f"File not found: {file_path}")

    # List of encodings to try
    encodings = ['utf-8-sig', 'utf-16', 'utf-8', 'latin-1']
    
    for encoding in encodings:
        try:
            with open(file_path, mode='r', encoding=encoding) as f:
                # Read the entire content to verify encoding validity
                content = f.read()
                
            # If successful, parse the content
            f_io = StringIO(content)
            reader = csv.DictReader(f_io)
            
            data = []
            
            # Handle empty files
            if reader.fieldnames is None:
                return []
            
            f_io.seek(0)
            reader = csv.DictReader(f_io)
            
            for row in reader:
                clean_row = {}
                for k, v in row.items():
                    # clean key
                    if k:
                        clean_k = k.strip()
                        # clean value
                        clean_v = v.strip() if v else v
                        clean_row[clean_k] = clean_v
                data.append(clean_row)
                
            return data

        except UnicodeError:
            continue
        except Exception as e:
            continue

    raise ValueError(f"Failed to read file: {file_path}. Ensure it is a valid CSV with supported encoding (UTF-8, UTF-16).")