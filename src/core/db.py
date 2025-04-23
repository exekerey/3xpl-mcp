import sqlite3

allowed_functions = {
    "json_extract", "json_each", "json_array_length", "json_type",
    "json_insert", "json_replace", "json_set", "json_remove",
    "json_valid", "json_quote", "json_object", "json_array",
    "min", "max", "avg", "sum", "total", "count",
    "length", "lower", "upper", "substr", "trim", "ltrim", "rtrim", "replace",
    "abs", "round", "cast", "pow", "power", "sqrt", "log", "ln", "log10", "exp", "ceil", "ceiling", "floor",
    "coalesce", "ifnull", "nullif",
    "date", "time", "datetime", "strftime",
    "group_concat"
}


def unwrap_into_table(conn: sqlite3.Connection, keys: dict, data: list[dict]):
    cols = ', '.join(f'{name} {type_}' for name, type_ in keys.items())
    conn.execute(f'DROP TABLE IF EXISTS data')
    conn.execute(f'CREATE TABLE data ({cols})')
    cols_names = ', '.join(keys)
    placeholders = ', '.join('?' for _ in keys)
    insert_sql = f'INSERT INTO data ({cols_names}) VALUES ({placeholders})'
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


def setup_sqlite_connection() -> sqlite3.Connection:
    # concurrency?
    conn = sqlite3.connect(":memory:")  # temp conn
    # conn.enable_load_extension(True)
    # conn.execute("SELECT load_extension('json1')")
    return conn


def get_aggregate(conn: sqlite3.Connection, sql_query: str):
    # maybe transform this into usual table, so model has better performance? TODO
    conn.set_authorizer(auth_cb)
    cur = conn.cursor()
    cur.execute(sql_query)
    result = cur.fetchall()
    return result
