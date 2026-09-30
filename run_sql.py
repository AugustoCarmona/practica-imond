#!/usr/bin/env python3
"""Arma el data warehouse ejecutando los archivos SQL de la carpeta sql/.

Uso:
    python run_sql.py          # ejecuta sql/*.sql en orden y exporta el resultado a dw/
    python run_sql.py --ui     # además abre la interfaz web de DuckDB para explorar las tablas

Cada vez que se ejecuta:
  1. Borra la base warehouse.duckdb y la vuelve a crear desde cero.
  2. Ejecuta los archivos de sql/ en orden alfabético (01_..., 02_..., 03_...).
     Si una consulta es un SELECT, muestra el resultado en la terminal.
  3. Exporta cada tabla creada a dw/<tabla>.csv (la carpeta dw/ se regenera completa).
  4. Genera dw/modelo_estrella.md con el diagrama del modelo (GitHub lo dibuja solo).
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parent
SQL_DIR = ROOT / "sql"
DW_DIR = ROOT / "dw"
DATABASE = ROOT / "warehouse.duckdb"
DIAGRAM = DW_DIR / "modelo_estrella.md"


def reset_outputs() -> None:
    for path in (DATABASE, DATABASE.with_name(DATABASE.name + ".wal")):
        path.unlink(missing_ok=True)
    DW_DIR.mkdir(exist_ok=True)
    for path in list(DW_DIR.glob("*.csv")) + [DIAGRAM]:
        path.unlink(missing_ok=True)


def run_file(con: duckdb.DuckDBPyConnection, path: Path) -> bool:
    """Ejecuta un archivo sentencia por sentencia. Devuelve False si hubo un error."""
    relative = path.relative_to(ROOT)
    try:
        statements = con.extract_statements(path.read_text(encoding="utf-8"))
    except duckdb.Error as error:
        print(f"\nERROR de sintaxis en {relative}:\n  {error}")
        return False
    print(f"\n>> {relative} ({len(statements)} sentencias)")
    for number, statement in enumerate(statements, start=1):
        query = statement.query.strip()
        try:
            result = con.sql(query)
            if result is not None:  # SELECT: mostrar el resultado
                print(f"\n-- Consulta {number}: {first_line(query)}")
                result.show(max_rows=30)
        except duckdb.Error as error:
            print(f"\nERROR en {relative}, sentencia {number}:")
            print("  " + "\n  ".join(query.splitlines()[:8]))
            print(f"\n  {error}")
            return False
    return True


def first_line(query: str) -> str:
    lines = [line for line in query.splitlines() if line.strip() and not line.strip().startswith("--")]
    return (lines[0].strip() if lines else query)[:80]


def user_tables(con: duckdb.DuckDBPyConnection) -> list[str]:
    rows = con.sql("SELECT table_name FROM duckdb_tables() WHERE NOT internal ORDER BY table_name").fetchall()
    return [row[0] for row in rows]


def export_tables(con: duckdb.DuckDBPyConnection, tables: list[str]) -> None:
    print("\nTablas exportadas a dw/:")
    for table in tables:
        rows = con.sql(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
        con.sql(f"COPY \"{table}\" TO '{(DW_DIR / f'{table}.csv').as_posix()}' (HEADER)")
        print(f"  {table + '.csv':<32}{rows:>10} filas")


def write_diagram(con: duckdb.DuckDBPyConnection, tables: list[str]) -> None:
    """Dibuja el modelo como diagrama Mermaid a partir de las PRIMARY KEY y FOREIGN KEY."""
    columns = con.sql(
        "SELECT table_name, column_name, data_type FROM duckdb_columns() "
        "WHERE NOT internal ORDER BY table_name, column_index"
    ).fetchall()
    constraints = con.sql(
        "SELECT table_name, constraint_type, constraint_column_names, referenced_table "
        "FROM duckdb_constraints() WHERE constraint_type IN ('PRIMARY KEY', 'FOREIGN KEY')"
    ).fetchall()
    keys: dict[tuple[str, str], set[str]] = {}
    relations = []
    for table, kind, cols, referenced in constraints:
        for col in cols:
            keys.setdefault((table, col), set()).add("PK" if kind == "PRIMARY KEY" else "FK")
        if kind == "FOREIGN KEY":
            relations.append(f'    {referenced} ||--o{{ {table} : "{", ".join(cols)}"')

    lines = ["# Modelo estrella", "", "Generado por `run_sql.py` a partir de las tablas de `warehouse.duckdb`.", "",
             "```mermaid", "erDiagram"]
    lines += sorted(set(relations))
    for table in tables:
        lines.append(f"    {table} {{")
        for t, column, data_type in columns:
            if t == table:
                simple_type = re.sub(r"\(.*\)", "", data_type).replace(" ", "_")
                marks = ", ".join(sorted(keys.get((table, column), set()), reverse=True))
                lines.append(f"        {simple_type} {column}{' ' + marks if marks else ''}")
        lines.append("    }")
    lines.append("```")
    DIAGRAM.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nDiagrama del modelo: {DIAGRAM.relative_to(ROOT)}")


def open_ui(con: duckdb.DuckDBPyConnection) -> None:
    print("\nAbriendo la interfaz de DuckDB en el navegador (necesita internet la primera vez)...")
    try:
        con.sql("CALL start_ui()")
    except duckdb.Error as error:
        print(f"No se pudo abrir la interfaz: {error}")
        return
    print("Si no se abrió sola, entrá a http://localhost:4213")
    input("Presioná Enter para cerrarla...\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--ui", action="store_true", help="abrir la interfaz web de DuckDB al terminar")
    args = parser.parse_args()

    sql_files = sorted(SQL_DIR.glob("*.sql"))
    if not sql_files:
        sys.exit(f"No hay archivos .sql en {SQL_DIR}")

    os.chdir(ROOT)  # así 'raw/...' funciona aunque se ejecute desde otra carpeta
    reset_outputs()
    con = duckdb.connect(str(DATABASE))
    for path in sql_files:
        if not run_file(con, path):
            print("\nSe detuvo la ejecución. Corregí el error y volvé a correr: python run_sql.py")
            con.close()
            sys.exit(1)

    tables = user_tables(con)
    if tables:
        export_tables(con, tables)
        write_diagram(con, tables)
    else:
        print("\nTodavía no se creó ninguna tabla.")
    print(f"\nListo. Base de datos: {DATABASE.name}")
    if args.ui:
        open_ui(con)
    con.close()


if __name__ == "__main__":
    main()
