import sqlite3
import sys

allowed_functions = {
    "json_extract", "json_each", "json_array_length", "json_type",
    "json_insert", "json_replace", "json_set", "json_remove",
    "json_valid", "json_quote", "json_object", "json_array",
    "min", "max", "avg", "sum", "total", "count", "length",
    "group_concat", "cast", "abs", "replace",
}


def unwrap_into_table(conn: sqlite3.Connection, keys: dict, data: list[dict]):
    cols = ', '.join(f'{name} {type_}' for name, type_ in keys.items())
    conn.execute(f'DROP TABLE IF EXISTS data')
    print(cols, file=sys.stderr)
    conn.execute(f'CREATE TABLE data ({cols})')
    cols_names = ', '.join(keys)
    placeholders = ', '.join('?' for _ in keys)
    insert_sql = f'INSERT INTO data ({cols_names}) VALUES ({placeholders})'
    print(insert_sql, file=sys.stderr)
    for row in data:
        values = tuple(row.get(col) for col in keys)
        conn.execute(insert_sql, values)
    conn.commit()


def auth_cb(action, arg1, arg2, dbname, sql):
    # print(action, arg1, arg2, dbname, sql, file=sys.stderr)
    if action == sqlite3.SQLITE_SELECT:
        return sqlite3.SQLITE_OK
    if action == sqlite3.SQLITE_FUNCTION:
        fn = (arg1 or arg2 or "").lower()
        if fn in allowed_functions:
            return sqlite3.SQLITE_OK
    if action == sqlite3.SQLITE_MISMATCH:
        return sqlite3.SQLITE_OK
    return sqlite3.SQLITE_DENY


def validate_sql(conn, query):
    query = query.strip(";")
    try:
        conn.execute(f"EXPLAIN QUERY PLAN {query}")
    except sqlite3.Error as e:
        conn.close()
        raise sqlite3.Error(f"You have provided an invalid sqlite query: {str(e)}")


def setup_sqlite_connection():
    # concurrency?
    conn = sqlite3.connect(":memory:")  # temp conn
    # conn.enable_load_extension(True)
    # conn.execute("SELECT load_extension('json1')")
    return conn


def get_aggregate(conn, sql_query):
    # maybe transform this into usual table, so model has better performance? TODO
    conn.set_authorizer(auth_cb)
    cur = conn.cursor()
    cur.execute(sql_query)
    result = cur.fetchall()
    return result
