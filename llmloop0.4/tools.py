import time
import json

def get_time(**kwargs):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))




class Tools:
    def __init__(self) -> None:
        self.name_to_func = self._name_to_func()
        self.tool = self._tool_list()
        

    def _name_to_func(self):
        func_dic = {
            'get_time' : get_time,
        }
        return func_dic

    def _tool_list(self):
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_time",
                    "description": "获得用户当前时间",
                    "parameters": {
                        "type": "object",
                        "properties": {

                        },
                        "required": []
                    },
                }
            },
        ]
        return tools

    def update(self,func,description):
        if type(description)== dict and description.get('function')['name']:
            name = (description.get('function') or {}).get("name")
        # elif type(description) == dict and len(list(description.keys())) :

        else:
            return 0
        if description not in self.tool:
            self.tool.append(description)
            self.name_to_func.update({name:func})
        

    def excute_tool(self,dic_args:dict):
        # example = {
        #     'name':name,
        #     'id':id,
        #     'args':{
        #         'xxx':'xxx'
        #             }
        #         }
        func = self.name_to_func.get(dic_args['function']['name'],None)
        if func is None:
            return False
        # tools.py 的 excute_tool 里
        kwargs = json.loads(dic_args['function'].get('arguments', '{}') or '{}')        
        res = func(**kwargs)
        return dic_args['id'],res





if __name__ == "__main__":
    print('test')
    tool = Tools()



