import sqlite3
from datetime import datetime
import os

class DatabaseManager:
    DB_NAME = "acm_data.db"

    def __init__(self):
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.DB_NAME)

    def _init_db(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS certificados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero TEXT,
                nombre_estudiante TEXT NOT NULL,
                carrera TEXT NOT NULL,
                num_factura TEXT,
                gestion TEXT,
                estado INTEGER DEFAULT 0, -- 0: Pendiente, 1: Entregado
                fecha_registro TEXT,
                fecha_entrega TEXT
            )
        ''')
        # Check if numero column exists, if not add it (for migration)
        cursor.execute("PRAGMA table_info(certificados)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'numero' not in columns:
            cursor.execute('ALTER TABLE certificados ADD COLUMN numero TEXT')
            
        conn.commit()
        conn.close()

    def add_certificate(self, numero, nombre, carrera, num_factura, gestion):
        conn = self._get_connection()
        cursor = conn.cursor()
        fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
            INSERT INTO certificados (numero, nombre_estudiante, carrera, num_factura, gestion, estado, fecha_registro)
            VALUES (?, ?, ?, ?, ?, 0, ?)
        ''', (numero, nombre, carrera, num_factura, gestion, fecha_registro))
        conn.commit()
        conn.close()

    def get_pending_certificates(self, carrera):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, COALESCE(numero, ''), nombre_estudiante, num_factura, gestion, fecha_registro 
            FROM certificados 
            WHERE carrera = ? AND estado = 0
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
            SELECT id, COALESCE(numero, ''), nombre_estudiante, carrera, num_factura, gestion, fecha_entrega
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
            SELECT id, COALESCE(numero, ''), nombre_estudiante, carrera, num_factura, gestion, fecha_entrega
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
        conn.commit()
        conn.close()
