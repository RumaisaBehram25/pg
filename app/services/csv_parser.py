
import csv
import os
from io import StringIO


def read_csv_file(file_path):

    if not os.path.exists(file_path):
        raise ValueError(f"File not found: {file_path}")

    encodings = ['utf-8-sig', 'utf-16', 'utf-8', 'latin-1']
    
    for encoding in encodings:
        try:
            with open(file_path, mode='r', encoding=encoding) as f:
                content = f.read()
                
            f_io = StringIO(content)
            reader = csv.DictReader(f_io)
            
            data = []
            
            if reader.fieldnames is None:
                return []
            
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

        except UnicodeError:
            continue
        except Exception as e:
            continue

    raise ValueError(f"Failed to read file: {file_path}. Ensure it is a valid CSV with supported encoding (UTF-8, UTF-16).")