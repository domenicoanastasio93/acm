from datetime import datetime

class DateUtil:
    @staticmethod
    def format_datetime(date_str):
        """
        Formatta una stringa data/ora dal database (YYYY-MM-DD HH:MM:SS) 
        nel formato italiano leggibile (DD/MM/YYYY HH:MM).
        """
        if not date_str:
            return ""
        try:
            # Formato salvato nel database
            dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            return dt.strftime("%d/%m/%Y %H:%M")
        except ValueError:
            return date_str

    @staticmethod
    def get_current_date_italy():
        """Ritorna la data odierna nel formato DD/MM/YYYY."""
        return datetime.now().strftime("%d/%m/%Y")

    @staticmethod
    def parse_to_db_format(italy_date_str):
        """
        Converte una stringa DD/MM/YYYY nel formato DB YYYY-MM-DD HH:MM:SS.
        Mantiene l'orario corrente.
        """
        try:
            day_dt = datetime.strptime(italy_date_str, "%d/%m/%Y")
            now = datetime.now()
            # Combina la data inserita con l'orario attuale
            full_dt = day_dt.replace(hour=now.hour, minute=now.minute, second=now.second)
            return full_dt.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            return None
