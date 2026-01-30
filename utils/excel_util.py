import openpyxl
import re
import os

def get_unique_gestioni(file_path='ITQ FNO ENF.xlsx'):
    if not os.path.exists(file_path):
        return []
    
    try:
        wb = openpyxl.load_workbook(file_path, data_only=True)
        sheet = wb.active
        # GESTIÓN is assumed to be the 3rd column (index 2) based on inspection
        # Data starts from row 3 (index 2) as seen in inspection (row 1 is title, row 2 is headers)
        unique_gestioni = set()
        
        for row in sheet.iter_rows(min_row=3, values_only=True):
            gestion_value = row[2]
            if gestion_value:
                # Find all patterns like I-20, II-21, etc.
                matches = re.findall(r'I+-\d+', str(gestion_value))
                for match in matches:
                    unique_gestioni.add(match)
        
        return sorted(unique_gestioni)
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return []
