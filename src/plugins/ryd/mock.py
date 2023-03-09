import json
from typing import Callable

from jinja2 import ext
from loguru import logger

from util import jinja, mysql
from util.http import HttpClient


async def send(client: HttpClient, path: str, tpl: str, data_call: Callable):
    """
    发送数据

    :param client: http客户端
    :param path: 路径
    :param tpl: 数据模板
    :param data_call: 数据函数
    :return:
    """
    page = 1
    end, res = await data_call(page)
    while res:
        datas = [res]
        if isinstance(res, list):
            datas = res
        for data in datas:
            req_str = jinja.render(data, tpl, extensions=[ext.do])
            resp = await client.req_json(path=path, data=json.loads(req_str))
            logger.info("Response Data: ", resp)
        if end:
            break
        page += 1
        end, res = await data_call(page)


async def data_allocate_agent(page: int) -> (bool, dict):
    """
    代理商划拨

    :param page:
    :return:
    """
    if page > 10:
        return True, []
    conn = mysql.connect({
        "host": "",
        "password": "",
        "database": ""
    })
    count = 10000
    price = 1000
    agent = mysql.first(conn=conn, sql=f"select id from account where type='AGENT' limit {page - 1},1")
    res_terminals = mysql.query(conn=conn, sql=f"select id from terminal limit {(page - 1) * count},{count}")
    return False, {
        "agent_id": agent.get("id"),
        "price": price,
        "terminal_ids": list(map(lambda x: x.id, res_terminals.rs))
    }


async def data_allocate_user(page: int) -> (bool, dict):
    """
    用户划拨

    :param page:
    :return:
    """
    if page > 100:
        return True, []
    conn = mysql.connect({
        "host": "",
        "password": "",
        "database": ""
    })
    count = 1000
    user = mysql.first(conn=conn, sql=f"select id from account where type='USER' limit {page - 1},1")
    agent_flow = mysql.first(conn=conn, sql=f"select id from agent_flow limit {page - 1},1")
    res_terminals = mysql.query(conn=conn,
                                sql=f"select terminal_id from agent_terminal where flow_id='{agent_flow}' "
                                    f"limit {(page - 1) * count},{count}")
    return False, {
        "user_id": user.get("id"),
        "agent_flow_id": agent_flow.get("id"),
        "terminal_ids": list(map(lambda x: x.id, res_terminals.rs))
    }
    ...


async def data_recharge_user(page: int) -> (bool, dict):
    """
    用户充值

    :param page:
    :return:
    """
    if page > 100000:
        return True, []
    conn = mysql.connect({
        "host": "",
        "password": "",
        "database": ""
    })
    terminal = mysql.first(conn=conn, sql=f"select id from terminal limit {page - 1},1")
    return False, {
        "terminal_id": terminal.get("id")
    }


_SEND_LIST_ = [
    {
        "title": "发送代理商划拨数据",
        "path": "/manage/stock/allocate/agent/allocate",
        "tpl": '{"accountId":{{agent_id}},"accountType":"AGENT","totalPrice":{{price}},"terminals":{{terminal_ids}}}',
        "data": data_allocate_agent
    },
    {
        "title": "发送用户划拨数据-单卡",
        "path": "/manage/stock/allocate/user/allocate",
        "tpl": '{"accountId":{{user_id}},"accountType":"USER","allocateType":"SINGLE","cycleType":"FIXED","coefficient":100,"months":1,"agentFlowId":{{agent_flow_id}},"flow":5,"totalPrice":5,"terminals":{{terminal_ids}}}',
        "data": data_allocate_user
    },
    {
        "title": "发送用户划拨数据-流量池",
        "path": "/manage/stock/allocate/user/allocate",
        "tpl": '{"accountId":{{user_id}},"accountType":"USER","allocateType":"POOL","cycleType":"FIXED","coefficient":100,"months":1,"agentFlowId":{{agent_flow_id}},"flow":5000,"totalPrice":5000,"terminals":{{terminal_ids}}}',
        "data": data_allocate_user
    },
    {
        "title": "发送用户充值数据",
        "path": "/manage/mall/user/recharge",
        "tpl": '{"accountType":"USER","allocateType":"SINGLE","rechargeType":"CURRENT","months":1,"flow":1,"totalPrice":1,"terminalId":{{terminal_id}}}',
        "data": data_recharge_user
    },
]

if __name__ == '__main__':
    http_client = HttpClient(uri="http://47.96.163.197:8000", headers={
        "Origin": "http://47.96.163.197:8000",
        "Referer": "http://47.96.163.197:8000/",
        "X-Authorization-Ryd": "eyJhbGciOiJIUzI1NiJ9.eyJSWURfVVNFUiI6IkFBRWhZMjl0TG5KNVpDNTFkR011YzNsemRHVnRMbXAzZEM1U2VXUktkM1JWYzJWeXdQYUM4TGt2dXl3QUFBQUFBUkZxWVhaaExuVjBhV3d1U0dGemFGTmxkQUgyQWYvOEJtdDFZV2xtZFFBPSIsImV4cCI6MTY3ODMzMjM4NCwiaXNzIjoicnlkIiwianRpIjoiMDVkOTQ5NGNlZWU0MzAwMSIsImlhdCI6MTY3ODI4OTE4NH0.4lv6_x9tMNW_b9ehcweYpVACJj9Njc8wNg21k0YKVSE",
    })
    for send_data in _SEND_LIST_:
        logger.info(send_data.get("title"))
        await send(client=http_client,
                   path=send_data.get("path"),
                   tpl=send_data.get("tpl"),
                   data_call=send_data.get("data"))
    logger.info("finished")
