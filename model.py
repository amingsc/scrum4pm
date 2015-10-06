#coding=utf-8
"""
methods for operate database.

@auto: amingsc@qq.com
@version: 1.0
"""

import sqlite3

DBFILE = 'data.sqlite'  # under current directory


def _dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def get_project():
    'get the dataset of all projects.'
    conn = sqlite3.connect(DBFILE)
    conn.row_factory = _dict_factory
    cursor = conn.cursor()
    sql = """SELECT id, name, status, category FROM project"""
    cursor.execute(sql)
    result = cursor.fetchall()
    return result


def get_userstory():
    'get the dataset of all userstories.'
    conn = sqlite3.connect(DBFILE)
    conn.row_factory = _dict_factory
    cursor = conn.cursor()
    sql = """SELECT u.id, u.name, u.status, u.priority,
            u.project_id, p.name AS project_name,
            p.category AS project_category
            FROM userstory u
            LEFT JOIN project p ON p.id=u.project_id"""
    cursor.execute(sql)
    result = cursor.fetchall()
    return result

def insert_userstory(data):
    'insert new userstory'
    conn = sqlite3.connect(DBFILE)
    cursor = conn.cursor()
    sql = """INSERT INTO userstory(name,status,priority,project_id)
            VALUES(:name, :status, :priority, :project_id)"""
    cursor.execute(sql, data)
    rowid = cursor.lastrowid
    conn.commit()
    conn.close()
    return rowid

def delete_userstory(usid):
    'delete a userstory'
    conn = sqlite3.connect(DBFILE)
    cursor = conn.cursor()
    sql = """DELETE FROM userstory WHERE id=?"""
    cursor.execute(sql, (usid,))
    rows = conn.total_changes
    conn.commit()
    conn.close()
    return rows
