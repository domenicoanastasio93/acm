from datetime import datetime

def get_unique_gestioni():
    """
    Generates a list of semesters (gestioni) from 2010 to the current year + 1.
    Format: I-YY, II-YY (e.g., I-10, II-10, ..., I-26, II-26)
    """
    start_year = 2010
    current_year = datetime.now().year
    end_year = current_year + 1
    
    gestioni = []
    for year in range(start_year, end_year + 1):
        yy = str(year)[-2:]
        # Chronological order: Summer -> Sem1 -> Winter -> Sem2
        gestioni.append(f"VER-{yy}")
        gestioni.append(f"I-{yy}")
        gestioni.append(f"INV-{yy}")
        gestioni.append(f"II-{yy}")
        
    return gestioni
