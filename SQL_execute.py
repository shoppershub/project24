import sqlite3 as sql

def GetData(sqlStatement):
    con = sql.connect('products.db')
    con.row_factory = sql.Row

    cur = con.cursor()
    cur.execute(sqlStatement)

    sql_data = cur.fetchall()
    con.close()
    return sql_data
