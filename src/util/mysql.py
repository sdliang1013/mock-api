from typing import Optional, List

import pymysql
from pydantic import BaseModel

_TYPE_QUERY_ = ['SELECT', 'SHOW']


class ResultSet(BaseModel):
    columns: List[str]
    rs: List[dict]


def connect(settings: dict) -> pymysql.Connect:
    """
    数据库连接

    :param settings:
    :return:
    """
    return pymysql.Connect(host=settings.get('host', '127.0.0.1'),
                           port=settings.get('port', 3306),
                           user=settings.get('username', 'root'),
                           password=settings['password'],
                           database=settings.get('database', None),
                           charset='utf8mb4')


def query(conn: pymysql.Connect, sql: str, args: Optional[list] = None, close: bool = False) -> ResultSet:
    """
    查询

    :param conn:
    :param sql:
    :param args:
    :param close:
    :return:
    """
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(query=sql, args=args)
            cols = [col_desc[0] for col_desc in cursor.description]
            rs = cursor.fetchall()
            return ResultSet(columns=cols, rs=rs)
    finally:
        if close:
            conn.close()


def first(conn: pymysql.Connect, sql: str, args: Optional[list] = None, close: bool = False) -> dict:
    """
    查询第一条记录

    :param conn:
    :param sql:
    :param args:
    :param close:
    :return:
    """
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(query=sql, args=args)
            return cursor.fetchone()
    finally:
        if close:
            conn.close()


def execute(conn: pymysql.Connect, sql: str, args: Optional[list] = None, close: bool = False) -> int:
    """
    执行

    :param conn:
    :param sql:
    :param args:
    :param close:
    :return:
    """
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            count = cursor.execute(query=sql, args=args)
        if count > 0:
            conn.commit()
        return count
    except:
        conn.rollback()
        raise
    finally:
        if close:
            conn.close()


def batch_execute(conn: pymysql.Connect, sqls: List[str], args: Optional[list] = None, close: bool = False) -> int:
    """
    执行

    :param conn:
    :param sqls:
    :param args:
    :param close:
    :return:
    """
    try:
        count = 0
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            for sql in sqls:
                count += cursor.execute(query=sql, args=args)
        if count > 0:
            conn.commit()
        return count
    except:
        conn.rollback()
        raise
    finally:
        if close:
            conn.close()


def is_query(sql: str) -> bool:
    return sql.strip().split()[0].upper() in _TYPE_QUERY_


def is_select(sql: str) -> bool:
    return sql.strip().split()[0].upper() == "SELECT"
