#coding=utf-8
"""
methods for operate database.

@auto: amingsc@qq.com
@version: 1.0
"""

import datetime
import sqlite3

DBFILE = 'data_dev.sqlite'  # under current directory


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


def get_userstory(with_frame=False):
    '''get the dataset of all userstories.
    @param with_frame: bool, if True then will return
        one row presudo data for initlize empty web components.
    '''
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
    if with_frame:
        result.append({'id': -1, 'name': '', 'project_id': -1,
                'status': u'正常', 'priority': u'低'})
    return result

def insert_userstory(data):
    'insert new userstory'
    assert data.status in ('正常', '取消', '暂停', '关闭'), \
            '字段status输入值不合法: %s' % data.status
    assert data.priority in ('低', '一般', '高', '紧急'), \
            '字段priority输入值不合法: %s' % data.priority

    conn = sqlite3.connect(DBFILE)
    cursor = conn.cursor()
    sql = """INSERT INTO userstory(name,status,priority,project_id)
            VALUES(:name, :status, :priority, :project_id)"""
    cursor.execute(sql, data)
    rowid = cursor.lastrowid
    conn.commit()
    conn.close()
    return rowid

def update_userstory(usid, data, subtask):
    'update a already existed userstory'
    conn = sqlite3.connect(DBFILE)
    try:
        cursor = conn.cursor()

        # 更新userstory(父任务)
        if usid:    # update old
            sql = """UPDATE userstory SET name=:name, status=:status,
                    priority=:priority, project_id=:project_id
                    WHERE id=:usid"""
            data['usid'] = usid
            cursor.execute(sql, data)
            rows = conn.total_changes
            assert rows==1, '用户故事（ID=%s）不存在' % usid
        else:   # insert new
            sql = """INSERT INTO userstory(name,status,priority,project_id)
                    VALUES(:name, :status,:priority, :project_id)"""
            cursor.execute(sql, data)
            usid = cursor.lastrowid
            rows = 1

        # 更新子任务
        for t in subtask:
            if t['deleted']:
                if not t['id']: continue
                sql = "DELETE FROM backlog WHERE id=?"
                cursor.execute(sql, (t['id']))
            elif t['id']:
                sql = "UPDATE backlog SET name=:name,priority=:priority WHERE id=:id"
                cursor.execute(sql, t)
            else:
                sql = "INSERT INTO backlog(name,priority,userstory_id) VALUES(?,?,?)"
                cursor.execute(sql, (t['name'], t['priority'], usid))

        conn.commit()
        conn.close()
        return rows
    except:
        conn.rollback()
        conn.close()
        raise

def delete_userstory(usid):
    'delete a userstory'
    conn = sqlite3.connect(DBFILE)
    cursor = conn.cursor()
    # 检查backlog是否为空
    sql = "SELECT COUNT(1) FROM backlog WHERE userstory_id=?"
    cursor.execute(sql, (usid,))
    if cursor.fetchone()[0] > 0:
        raise Exception('Backlog not empty!')
    # 真正的删除操作
    sql = """DELETE FROM userstory WHERE id=?"""
    cursor.execute(sql, (usid,))
    rows = conn.total_changes
    conn.commit()
    conn.close()
    return rows

def delete_backlog(blid):
    'delete a backlog'
    conn = sqlite3.connect(DBFILE)
    cursor = conn.cursor()
    sql = """DELETE FROM backlog WHERE id=?"""
    cursor.execute(sql, (blid,))
    rows = conn.total_changes
    conn.commit()
    conn.close()
    return rows

def get_backlog(with_frame=False):
    '''get the dataset of all backlogs.
    @param with_frame: bool, if True then will return
        one row presudo data for initlize empty web components.
    '''
    conn = sqlite3.connect(DBFILE)
    conn.row_factory = _dict_factory
    cursor = conn.cursor()
    sql = """SELECT b.id, b.name, b.progress, b.priority, b.userstory_id
            FROM backlog b"""
    cursor.execute(sql)
    result = cursor.fetchall()
    if with_frame:
        result.append({'id': -1, 'name': '', 'userstory_id': -1,
                'progress': u'未开始', 'priority': u'低'})
    return result

def update_subtask(subtask_id, data):
    '更新子任务进度'
    conn = sqlite3.connect(DBFILE)
    cursor = conn.cursor()
    sql = """UPDATE backlog SET progress=? WHERE id=?"""
    cursor.execute(sql, (data['progress'], subtask_id))
    rows = conn.total_changes
    conn.commit()
    conn.close()
    return rows

def get_review_list(days_limit=7, plan_limit=1):
    '查询最近的review记录'
    conn = sqlite3.connect(DBFILE)
    conn.row_factory = _dict_factory
    cursor = conn.cursor()

    # 拼接连续日期的SQL
    sql = "SELECT d.`date`, r.id, r.plan, r.done, r.quality, r.notes" \
            " FROM (SELECT ? AS `date`"
    for i in range(1, days_limit+plan_limit):
        sql += " UNION ALL SELECT ? "
    sql += ") d LEFT JOIN " \
        " review r ON r.`date`=d.`date` " \
        " ORDER BY d.`date` LIMIT %s" % (days_limit+plan_limit)
    # 构造连续日期值
    date_list = [datetime.date.today() - datetime.timedelta(i) \
                    for i in range(-plan_limit,days_limit)]
    date_list = [d.strftime('%Y-%m-%d') for d in date_list]

    cursor.execute(sql, date_list)
    result = cursor.fetchall()
    return result

def update_review(data):
    '更新review属性'
    try:
        conn = sqlite3.connect(DBFILE)
        cursor = conn.cursor()

        # 查询已有review的日期
        sql = "SELECT `date` FROM review LIMIT 30"
        cursor.execute(sql)
        date_list = set([r[0] for r in cursor.fetchall()])

        sql1 = "UPDATE review SET plan=:plan, done=:done," \
                "quality=:quality, notes=:notes" \
                " WHERE `date`=:date"
        sql2 = "INSERT INTO review(`date`,plan,done,quality,notes)" \
                "VALUES(:date,:plan,:done,:quality,:notes)"
        for r in data:
            sql = (sql1, sql2)[r['date'] not in date_list]
            cursor.execute(sql, r)
        conn.commit()
        conn.close()
    except:
        cursor.rollback()
        conn.close()


def get_today():
    return datetime.date.today().strftime('%Y-%m-%d')
