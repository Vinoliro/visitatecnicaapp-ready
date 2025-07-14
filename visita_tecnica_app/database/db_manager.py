import sqlite3
import os
from datetime import datetime
import json

DB_PATH = os.path.join(os.path.dirname(__file__), 'visita_tecnica.db')

class DBManager:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        self.criar_tabelas()

    def criar_tabelas(self):
        cursor = self.conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT,
                email TEXT UNIQUE,
                senha TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS visitas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                produtor TEXT,
                propriedade TEXT,
                municipio TEXT,
                tecnico TEXT,
                data TEXT,
                chegada TEXT,
                saida TEXT,
                divisao_tarefa INTEGER,
                borracha_chao INTEGER,
                estimulo_intervalo TEXT,
                estimulo_conc TEXT,
                controle_doencas INTEGER,
                controle_pragas INTEGER,
                limpeza_linhas INTEGER,
                limpeza_entrelinhas INTEGER,
                tracagem_consumo INTEGER,
                foto_path TEXT,
                latitude REAL,
                longitude REAL,
                usuario_id INTEGER,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS visitas_fsc (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                produtor TEXT,
                propriedade TEXT,
                data TEXT,
                chegada TEXT,
                saida TEXT,
                checklist TEXT,             -- JSON com os itens marcados
                fotos_com_observacoes TEXT, -- JSON com lista de dicionários {foto_path, observacao}
                usuario_id INTEGER,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        ''')

        self.conn.commit()

    # VISITA TÉCNICA
    def inserir_visita(self, dados, usuario_id=None):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO visitas (
                produtor, propriedade, municipio, tecnico, data, chegada, saida,
                divisao_tarefa, borracha_chao, estimulo_intervalo, estimulo_conc,
                controle_doencas, controle_pragas, limpeza_linhas,
                limpeza_entrelinhas, tracagem_consumo, foto_path, latitude, longitude,
                usuario_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            dados.get('produtor'),
            dados.get('propriedade'),
            dados.get('municipio'),
            dados.get('tecnico'),
            dados.get('data'),
            dados.get('chegada'),
            dados.get('saida'),
            int(dados.get('divisao_tarefa', 0)),
            int(dados.get('borracha_chao', 0)),
            dados.get('estimulo_intervalo'),
            dados.get('estimulo_conc'),
            int(dados.get('manutencao', {}).get("Controle de Doenças", 0)),
            int(dados.get('manutencao', {}).get("Controle de Pragas", 0)),
            int(dados.get('manutencao', {}).get("Limpeza nas Linhas", 0)),
            int(dados.get('manutencao', {}).get("Limpeza nas Entrelinhas", 0)),
            int(dados.get('manutencao', {}).get("Traçagem de Consumo", 0)),
            dados.get('foto_path'),
            float(dados.get('latitude')) if dados.get('latitude') else None,
            float(dados.get('longitude')) if dados.get('longitude') else None,
            usuario_id
        ))
        self.conn.commit()

    # VISITA FSC
    def inserir_visita_fsc(self, dados, usuario_id=None):
        cursor = self.conn.cursor()
        checklist_json = json.dumps(dados.get('checklist', {}))
        fotos_json = json.dumps(dados.get('fotos', []))  # lista de {foto_path, observacao}
        cursor.execute('''
            INSERT INTO visitas_fsc (
                produtor, propriedade, data, chegada, saida,
                checklist, fotos_com_observacoes, usuario_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            dados.get('produtor'),
            dados.get('propriedade'),
            dados.get('data'),
            dados.get('chegada'),
            dados.get('saida'),
            checklist_json,
            fotos_json,
            usuario_id
        ))
        self.conn.commit()

    # LISTAGEM UNIFICADA PARA HISTÓRICO
    def listar_visitas_filtradas(self, produtor='', municipio='', data_inicio='', data_fim='', usuario_id=None):
        cursor = self.conn.cursor()
        query = """
            SELECT id, produtor, propriedade, tecnico, data, municipio, 'tecnica' as tipo
            FROM visitas
            WHERE 1=1
        """
        params = []

        if usuario_id is not None:
            query += " AND usuario_id = ?"
            params.append(usuario_id)

        if produtor:
            query += " AND LOWER(produtor) LIKE ?"
            params.append(f"%{produtor.lower()}%")
        if municipio:
            query += " AND LOWER(municipio) LIKE ?"
            params.append(f"%{municipio.lower()}%")
        if data_inicio:
            try:
                data_inicio_sql = datetime.strptime(data_inicio, "%d/%m/%Y").strftime("%Y-%m-%d")
                query += " AND data >= ?"
                params.append(data_inicio_sql)
            except ValueError:
                pass
        if data_fim:
            try:
                data_fim_sql = datetime.strptime(data_fim, "%d/%m/%Y").strftime("%Y-%m-%d")
                query += " AND data <= ?"
                params.append(data_fim_sql)
            except ValueError:
                pass

        # Visitas FSC também
        query_fsc = """
            SELECT id, produtor, propriedade, '' as tecnico, data, '' as municipio, 'fsc' as tipo
            FROM visitas_fsc
            WHERE 1=1
        """
        params_fsc = []

        if usuario_id is not None:
            query_fsc += " AND usuario_id = ?"
            params_fsc.append(usuario_id)
        if produtor:
            query_fsc += " AND LOWER(produtor) LIKE ?"
            params_fsc.append(f"%{produtor.lower()}%")
        if data_inicio:
            try:
                data_inicio_sql = datetime.strptime(data_inicio, "%d/%m/%Y").strftime("%Y-%m-%d")
                query_fsc += " AND data >= ?"
                params_fsc.append(data_inicio_sql)
            except ValueError:
                pass
        if data_fim:
            try:
                data_fim_sql = datetime.strptime(data_fim, "%d/%m/%Y").strftime("%Y-%m-%d")
                query_fsc += " AND data <= ?"
                params_fsc.append(data_fim_sql)
            except ValueError:
                pass

        # Executa ambas e une os resultados
        cursor.execute(query, params)
        tecnica = cursor.fetchall()

        cursor.execute(query_fsc, params_fsc)
        fsc = cursor.fetchall()

        resultado = []
        for r in tecnica + fsc:
            resultado.append({
                "id": r["id"],
                "produtor": r["produtor"],
                "propriedade": r["propriedade"],
                "tecnico": r["tecnico"],
                "data": r["data"],
                "municipio": r["municipio"],
                "tipo": r["tipo"]
            })

        # Ordena pela data descendente
        resultado.sort(key=lambda x: x["data"], reverse=True)
        return resultado

    def obter_visita_fsc_por_id(self, visita_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM visitas_fsc WHERE id = ?", (visita_id,))
        row = cursor.fetchone()
        if not row:
            return None

        visita = dict(row)
        visita["checklist"] = json.loads(visita.get("checklist", "{}"))
        visita["fotos"] = json.loads(visita.get("fotos_com_observacoes", "[]"))
        return visita

    def obter_visita_por_id(self, visita_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM visitas WHERE id = ?", (visita_id,))
        row = cursor.fetchone()

        if not row:
            return None

        visita = dict(row)
        visita["manutencao"] = {
            "Controle de Doenças": bool(visita.get("controle_doencas")),
            "Controle de Pragas": bool(visita.get("controle_pragas")),
            "Limpeza nas Linhas": bool(visita.get("limpeza_linhas")),
            "Limpeza nas Entrelinhas": bool(visita.get("limpeza_entrelinhas")),
            "Traçagem de Consumo": bool(visita.get("tracagem_consumo")),
        }
        return visita

    def obter_todas_visitas(self, usuario_id=None):
        cursor = self.conn.cursor()
        if usuario_id:
            cursor.execute("SELECT * FROM visitas WHERE usuario_id = ? ORDER BY data DESC", (usuario_id,))
        else:
            cursor.execute("SELECT * FROM visitas ORDER BY data DESC")

        rows = cursor.fetchall()
        visitas = []
        for row in rows:
            visita = dict(row)
            visita["manutencao"] = {
                "Controle de Doenças": bool(visita.get("controle_doencas")),
                "Controle de Pragas": bool(visita.get("controle_pragas")),
                "Limpeza nas Linhas": bool(visita.get("limpeza_linhas")),
                "Limpeza nas Entrelinhas": bool(visita.get("limpeza_entrelinhas")),
                "Traçagem de Consumo": bool(visita.get("tracagem_consumo")),
            }
            visitas.append(visita)
        return visitas

    def autenticar_usuario(self, email, senha):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE email = ? AND senha = ?", (email, senha))
        usuario = cursor.fetchone()
        return dict(usuario) if usuario else None

    def cadastrar_usuario(self, nome, email, senha):
        cursor = self.conn.cursor()
        try:
            cursor.execute("INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)", (nome, email, senha))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
