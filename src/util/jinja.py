# coding:utf-8

from jinja2 import Environment, meta, Template


# 从模板中取得所有变量
def get_all_variables(tpl_content: str, extensions=[]):
    env = Environment(extensions=extensions)
    parsed_content = env.parse(tpl_content)
    return meta.find_undeclared_variables(parsed_content), Template(parsed_content)


# 从文件取得模板和模板中变量
def get_all_variables_from_file(tpl_file, extensions=[]):
    with open(tpl_file, 'r') as f:
        data = f.read()
    return get_all_variables(data, extensions)


# 替换变量
def render(kv_list, content=None, file=None, extensions=[]):
    if content and ("{{" not in content):
        return content

    # 导入模板， 检查变量是否都有
    if file:
        var_list, template = get_all_variables_from_file(file, extensions)
    else:
        var_list, template = get_all_variables(content, extensions)
    variables = {}
    for v in var_list:
        if v in kv_list.keys():
            variables[v] = kv_list[v]

    # if len(variables.keys())==0:
    #    return template_content  # 没匹配到变量

    # 替换变量
    return template.render(variables)
