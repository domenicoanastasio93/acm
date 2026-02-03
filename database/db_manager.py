import sqlite3
from datetime import datetime
import os
import sys

class DatabaseManager:
    def _parse_gestion_items(self, gestion_str):
        import re
        if not gestion_str:
            return []
        pattern = r'((?:II|I|VER|INV)-\d+)(?:\s*\(?[xX](\d+)\)?)?'
        matches = re.findall(pattern, gestion_str)
        items = []
        if not matches and gestion_str.strip():
            items.append(gestion_str.strip())
        else:
            for code, multiplier in matches:
                count = int(multiplier) if multiplier else 1
                for _ in range(count):
                    items.append(code)
        return items

    def _perform_safe_backup(self):
        import shutil
        
        if not os.path.exists(self.db_path):
            return

        try:
            # Check integrity before backing up
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()
            conn.close()

            if result and result[0] == "ok":
                try:
                    shutil.copy2(self.db_path, self.backup_db_path)
                    print(f"Backup created successfully at {self.backup_db_path}")
                except Exception as e:
                     print(f"Failed to copy backup file: {e}")
            else:
                print("Database integrity check failed. Backup skipped to clean version.")
        except Exception as e:
            print(f"Failed to perform backup check: {e}")


    def __init__(self):
        # Determine base path for the database
        if getattr(sys, 'frozen', False):
            # Running as a PyInstaller executable
            base_path = os.path.dirname(sys.executable)
        else:
            # Running as a normal script
            # Go up one level from database/ folder to the root
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
        self.db_path = os.path.join(base_path, "acm_data.db")
        self.backup_db_path = os.path.join(base_path, "acm_data.backup.db")
        
        # If running as EXE and DB doesn't exist in the EXE folder, 
        # try to copy the bundled template if it exists
        if getattr(sys, 'frozen', False) and not os.path.exists(self.db_path):
            import shutil
            bundled_db = os.path.join(sys._MEIPASS, "acm_data.db")
            if os.path.exists(bundled_db):
                try:
                    shutil.copy2(bundled_db, self.db_path)
                except Exception:
                    pass

        # Attempt to create a backup if the DB exists and is healthy
        self._perform_safe_backup()
                    
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Main table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS certificados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero TEXT,
                nombre_estudiante TEXT NOT NULL,
                carrera TEXT NOT NULL,
                num_factura TEXT,
                gestion TEXT,
                notas TEXT,
                estado INTEGER DEFAULT 0, -- 0: Pendiente, 1: Entregado (Legacy/Global status)
                fecha_registro TEXT,
                fecha_entrega TEXT
            )
        ''')
        
        # Items table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS certification_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                certificado_id INTEGER NOT NULL,
                item_name TEXT NOT NULL,
                estado INTEGER DEFAULT 0,
                fecha_entrega TEXT,
                FOREIGN KEY (certificado_id) REFERENCES certificados (id) ON DELETE CASCADE
            )
        ''')

        # Check if numero column exists, if not add it (for migration)
        cursor.execute("PRAGMA table_info(certificados)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'numero' not in columns:
            cursor.execute('ALTER TABLE certificados ADD COLUMN numero TEXT')
        if 'notas' not in columns:
            cursor.execute('ALTER TABLE certificados ADD COLUMN notas TEXT')
            
        # --- MIGRATION: Populate certification_items for existing records ---
        # Check if we need migration (items table empty but main table has data)
        cursor.execute("SELECT COUNT(*) FROM certification_items")
        items_count = cursor.fetchone()[0]
        
        if items_count == 0:
            cursor.execute("SELECT id, gestion, estado, fecha_entrega FROM certificados")
            existing_certs = cursor.fetchall()
            if existing_certs:
                import re
                pattern = r'((?:II|I|VER|INV)-\d+)(?:\s*\(?[xX](\d+)\)?)?'
                
                for cert_id, gestion_str, estado_global, fecha_entrega_global in existing_certs:
                    if not gestion_str:
                        continue
                        
                    matches = re.findall(pattern, gestion_str)
                    items_to_create = []
                    
                    if not matches and gestion_str.strip():
                        # No standard pattern match, treat whole string as one item
                        items_to_create.append(gestion_str.strip())
                    else:
                        for code, multiplier in matches:
                            count = int(multiplier) if multiplier else 1
                            for _ in range(count):
                                items_to_create.append(code)
                    
                    for item_name in items_to_create:
                        # Inherit status from parent for migration
                        status = estado_global
                        d_date = fecha_entrega_global if status == 1 else None
                        
                        cursor.execute('''
                            INSERT INTO certification_items (certificado_id, item_name, estado, fecha_entrega)
                            VALUES (?, ?, ?, ?)
                        ''', (cert_id, item_name, status, d_date))

        conn.commit()
        conn.close()

    def add_certificate(self, numero, nombre, carrera, num_factura, gestion, notas=None):
        conn = self._get_connection()
        cursor = conn.cursor()
        fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute('''
            INSERT INTO certificados (numero, nombre_estudiante, carrera, num_factura, gestion, notas, estado, fecha_registro)
            VALUES (?, ?, ?, ?, ?, ?, 0, ?)
        ''', (numero, nombre, carrera, num_factura, gestion, notas, fecha_registro))
        
        cert_id = cursor.lastrowid
        
        # Create individual items
        items = self._parse_gestion_items(gestion)
        for item_name in items:
            cursor.execute('''
                INSERT INTO certification_items (certificado_id, item_name, estado, fecha_entrega)
                VALUES (?, ?, 0, NULL)
            ''', (cert_id, item_name))
            
        conn.commit()
        conn.close()

    def get_career_certificates(self, carrera):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, COALESCE(numero, ''), nombre_estudiante, num_factura, gestion, fecha_registro, estado, COALESCE(notas, ''), fecha_entrega
            FROM certificados 
            WHERE carrera = ?
            ORDER BY TRIM(nombre_estudiante) COLLATE NOCASE ASC
        ''', (carrera,))
        rows = cursor.fetchall()
        conn.close()
        return rows

    def mark_as_delivered(self, cert_id, fecha_entrega=None):
        conn = self._get_connection()
        cursor = conn.cursor()
        if fecha_entrega is None:
            fecha_entrega = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
            UPDATE certificados 
            SET estado = 1, fecha_entrega = ? 
            WHERE id = ?
        ''', (fecha_entrega, cert_id))
        conn.commit()
        conn.close()

    def delete_certificate(self, cert_id):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM certificados WHERE id = ?', (cert_id,))
        conn.commit()
        conn.close()

    def get_filtered_delivered_certificates(self, month=None, year=None, carrera=None):
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT id, COALESCE(numero, ''), nombre_estudiante, carrera, num_factura, gestion, fecha_entrega, COALESCE(notas, '')
            FROM certificados
            WHERE estado = 1
        '''
        params = []
        
        if month:
            query += " AND strftime('%m', fecha_entrega) = ?"
            params.append(f"{int(month):02d}")
        
        if year:
            query += " AND strftime('%Y', fecha_entrega) = ?"
            params.append(str(year))

        if carrera:
            query += " AND carrera = ?"
            params.append(carrera)

        query += " ORDER BY TRIM(nombre_estudiante) COLLATE NOCASE ASC"
            
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_delivered_certificates_by_month(self, month, year, carrera=None):
        # Keeps compatibility with old export logic if needed, but uses the new filtering logic
        rows = self.get_filtered_delivered_certificates(month, year, carrera)
        # return only (numero, nombre, carrera, factura, gestion, fecha) for export
        return [(r[1], r[2], r[3], r[4], r[5], r[6]) for r in rows]

    def get_all_delivered_certificates(self, carrera=None):
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT id, COALESCE(numero, ''), nombre_estudiante, carrera, num_factura, gestion, fecha_entrega, COALESCE(notas, '')
            FROM certificados
            WHERE estado = 1
        '''
        params = []
        
        if carrera:
            query += " AND carrera = ?"
            params.append(carrera)
            
        query += " ORDER BY TRIM(nombre_estudiante) COLLATE NOCASE ASC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return rows

    def clear_delivered_certificates(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM certificados WHERE estado = 1')
        conn.commit()
        conn.close()

    def undo_delivery(self, cert_id):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE certificados 
            SET estado = 0, fecha_entrega = NULL 
            WHERE id = ?
        ''', (cert_id,))
        
        # Reset all items for this certificate
        cursor.execute('UPDATE certification_items SET estado = 0, fecha_entrega = NULL WHERE certificado_id = ?', (cert_id,))
        
        conn.commit()
        conn.close()

    def update_certificate_field(self, cert_id, field_name, new_value):
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Mapping Treeview column names to DB column names
        field_map = {
            "N.": "numero",
            "Nombre": "nombre_estudiante",
            "Factura": "num_factura",
            "Gestión": "gestion",
            "Notas": "notas"
        }
        
        db_column = field_map.get(field_name)
        if db_column:
            query = f"UPDATE certificados SET {db_column} = ? WHERE id = ?"
            cursor.execute(query, (new_value, cert_id))
            conn.commit()
        
        conn.close()

    # --- New Methods for Items ---

    def get_certificate_items(self, cert_id):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, item_name, estado, fecha_entrega 
            FROM certification_items 
            WHERE certificado_id = ?
            ORDER BY id ASC
        ''', (cert_id,))
        rows = cursor.fetchall()
        conn.close()
        return rows

    def mark_item_delivered(self, item_id, fecha_entrega=None):
        conn = self._get_connection()
        cursor = conn.cursor()
        if fecha_entrega is None:
            fecha_entrega = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
            UPDATE certification_items 
            SET estado = 1, fecha_entrega = ? 
            WHERE id = ?
        ''', (fecha_entrega, item_id))
        
        # Update parent status
        cursor.execute('SELECT certificado_id FROM certification_items WHERE id = ?', (item_id,))
        cert_id_row = cursor.fetchone()
        if cert_id_row:
            cert_id = cert_id_row[0]
            cursor.execute('SELECT COUNT(*) FROM certification_items WHERE certificado_id = ? AND estado = 0', (cert_id,))
            remaining = cursor.fetchone()[0]
            
            # If 0 remaining, mark parent as delivered (1).
            if remaining == 0:
                cursor.execute('UPDATE certificados SET estado = 1, fecha_entrega = ? WHERE id = ?', (fecha_entrega, cert_id))
                
        conn.commit()
        conn.close()

    def undo_item_delivery(self, item_id):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE certification_items 
            SET estado = 0, fecha_entrega = NULL 
            WHERE id = ?
        ''', (item_id,))
        
        # Update parent to Pending if it was delivered
        cursor.execute('SELECT certificado_id FROM certification_items WHERE id = ?', (item_id,))
        cert_id_row = cursor.fetchone()
        if cert_id_row:
             cursor.execute('UPDATE certificados SET estado = 0 WHERE id = ?', (cert_id_row[0],))
             
        conn.commit()
        conn.close()

    def delete_certificate_item(self, item_id):
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Get parent id first to update its status later if needed
        cursor.execute('SELECT certificado_id FROM certification_items WHERE id = ?', (item_id,))
        row = cursor.fetchone()
        
        cursor.execute('DELETE FROM certification_items WHERE id = ?', (item_id,))
        
        if row:
            cert_id = row[0]
            # Check if parent has any items left.
            cursor.execute('SELECT COUNT(*) FROM certification_items WHERE certificado_id = ? AND estado = 0', (cert_id,))
            remaining_pending = cursor.fetchone()[0]
            cursor.execute('SELECT COUNT(*) FROM certification_items WHERE certificado_id = ?', (cert_id,))
            total_remaining = cursor.fetchone()[0]
            
            if total_remaining > 0:
                new_status = 1 if remaining_pending == 0 else 0
                cursor.execute('UPDATE certificados SET estado = ? WHERE id = ?', (new_status, cert_id))
            
        conn.commit()
        conn.close()

    def update_item_name(self, item_id, new_name):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE certification_items SET item_name = ? WHERE id = ?', (new_name, item_id))
        conn.commit()
        conn.close()
    def add_certificate_item(self, cert_id, item_name):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO certification_items (certificado_id, item_name, estado, fecha_entrega)
            VALUES (?, ?, 0, NULL)
        ''', (cert_id, item_name))
        
        # Reset parent status to Pending if it was delivered
        cursor.execute('UPDATE certificados SET estado = 0 WHERE id = ?', (cert_id,))
        
        conn.commit()
        conn.close()

    def get_certificate_counts(self, cert_id):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*), SUM(estado) FROM certification_items WHERE certificado_id = ?', (cert_id,))
        row = cursor.fetchone()
        conn.close()
        total = row[0] if row and row[0] is not None else 0
        delivered = row[1] if row and row[1] is not None else 0
        return total, delivered

