import sqlite3
from datetime import datetime
from pathlib import Path
import json

DB_PATH = Path("outputs/historico_prisma.sqlite")


def iniciar_banco():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS revisoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tema TEXT,
        tipo_revisao TEXT,
        query_geral TEXT,
        ano_inicial INTEGER,
        ano_final INTEGER,
        max_artigos INTEGER,
        total_identificados INTEGER,
        total_pos_duplicatas INTEGER,
        total_pos_similaridade INTEGER,
        data_execucao TEXT,
        parametros_json TEXT
    )
    """)

    conn.commit()
    conn.close()


def salvar_revisao(parametros, total_identificados, total_pos_duplicatas, total_pos_similaridade):
    iniciar_banco()

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO revisoes (
        tema, tipo_revisao, query_geral, ano_inicial, ano_final, max_artigos,
        total_identificados, total_pos_duplicatas, total_pos_similaridade,
        data_execucao, parametros_json
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        parametros.get("tema", ""),
        parametros.get("tipo_revisao", ""),
        parametros.get("query_geral", ""),
        parametros.get("ano_inicial", ""),
        parametros.get("ano_final", ""),
        parametros.get("max_artigos", ""),
        total_identificados,
        total_pos_duplicatas,
        total_pos_similaridade,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        json.dumps(parametros, ensure_ascii=False)
    ))

    conn.commit()
    conn.close()


def listar_revisoes():
    iniciar_banco()

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    SELECT id, tema, tipo_revisao, ano_inicial, ano_final,
           total_identificados, total_pos_duplicatas, total_pos_similaridade, data_execucao
    FROM revisoes
    ORDER BY id DESC
    """)

    dados = cur.fetchall()
    conn.close()

    return dados

# ============================================================
# ATHENA - Limpar Histórico
# ============================================================

def limpar_historico():
    """
    Remove todas as revisões do histórico PRISMA.
    """
    iniciar_banco()

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("DELETE FROM revisoes")
    cur.execute("DELETE FROM sqlite_sequence WHERE name='revisoes'")

    conn.commit()
    conn.close()
