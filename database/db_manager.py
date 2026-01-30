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
                nombre_estudiante TEXT NOT NULL,
                carrera TEXT NOT NULL,
                num_factura TEXT,
                gestion TEXT,
                estado INTEGER DEFAULT 0, -- 0: Pendiente, 1: Entregado
                fecha_registro TEXT,
                fecha_entrega TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def add_certificate(self, nombre, carrera, num_factura, gestion):
        conn = self._get_connection()
        cursor = conn.cursor()
        fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
            INSERT INTO certificados (nombre_estudiante, carrera, num_factura, gestion, estado, fecha_registro)
            VALUES (?, ?, ?, ?, 0, ?)
        ''', (nombre, carrera, num_factura, gestion, fecha_registro))
        conn.commit()
        conn.close()

    def get_pending_certificates(self, carrera):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, nombre_estudiante, num_factura, gestion, fecha_registro 
            FROM certificados 
            WHERE carrera = ? AND estado = 0
            ORDER BY nombre_estudiante ASC
        ''', (carrera,))
        rows = cursor.fetchall()
        conn.close()
        return rows

    def mark_as_delivered(self, cert_id):
        conn = self._get_connection()
        cursor = conn.cursor()
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

    def get_delivered_certificates_by_month(self, month, year, carrera=None):
        # month is integer 1-12
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # SQLite doesn't have a simple MONTH() function without extensions in some versions, 
        # but strftime works reliable.
        # %m returns 01-12, %Y returns YYYY
        
        month_str = f"{int(month):02d}"
        year_str = str(year)

        query = '''
            SELECT nombre_estudiante, carrera, num_factura, gestion, fecha_entrega
            FROM certificados
            WHERE estado = 1 
            AND strftime('%m', fecha_entrega) = ?
            AND strftime('%Y', fecha_entrega) = ?
        '''
        params = [month_str, year_str]

        if carrera:
            query += " AND carrera = ?"
            params.append(carrera)

        query += " ORDER BY nombre_estudiante ASC"
            
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return rows
