"""

学习用途，可用指导，请勿修改


"""

import hashlib
import json
from pathlib import Path
import time
import re
# from llmloop.llmLoop import user
from pic import Pic
picture = Pic()



import pynput.keyboard as keyboard

base64_cache = Path(__file__).parent / "data" / "base64_cache.json" 
tar_json = Path(__file__).parent / "data" / "mes_data.json" 



class MesManager():     
    #终端查看 编辑 mes
    def __init__(self,mes) -> None:
        self.mes = mes
        self.cur = 0
        self.page = 0
        self.queue = [None]
        self.mes_list = []
        self.hang = 5
        with open(base64_cache,'r',encoding="utf-8") as f:
            self.base64_dir  = dict(json.load(f)) 

        

    def url2path(self,url:str,base64_dir):
        # with open(base64_cache,'r',encoding="utf-8") as f:
        #     base64_dir = dict(json.load(f)) 
        base64_url = hashlib.md5(url.encode("utf-8")).hexdigest()
        return base64_dir.get(base64_url,None)
    def _update_base64_dir(self):
        with open(base64_cache,'r',encoding="utf-8") as f:
            self.base64_dir  = dict(json.load(f)) 

    def _mes_list(self):#要传入mes这个类  -> 返回一个list包list，分别是每一页
        self._update_base64_dir()
        all_mes_dir = []
        for k,v in self.mes.data.items():
            # v = list(kv)[1] #列表
            if len(v) <=1:
                continue
            v= v[1:]
            ti = k
            # head_str =   f'\n\033[0;1;{7 if itx == self.cur else 4}m 查看 \033[0m  \033[1m{ti}\033[0m      '
            user_content_pre = v[0].get('content',"None")
            user_content = ""
            if type(user_content_pre) == list: #说明包含图片
                for m in user_content_pre:
                    if m.get("image_url",0):
                        url = m["image_url"].get("url",None)
                        file_path = self.url2path(url,self.base64_dir)
                        if file_path :
                            user_content += "\033[1m[图片]\033[0m \033[4m"+Path(file_path).name +"\033[0m "
                            
                        else:
                            user_content += "\033[1m[图片未找到]\033[0m "
                        continue
                    user_content += m.get("text")
            else:
                user_content = user_content_pre.strip()
                if v[1].get("content","") is None:
                    assistant_content = ''
                else:
                    assistant_content = v[1].get("content","").strip()
            
            all_mes_dir.append([ti,user_content,assistant_content])
        all_mes_dir.reverse()
        # all_mes_dir.append([[None,None,None]]*(self.hang - len(all_mes_dir)%self.hang))
        return [all_mes_dir[i:i+self.hang] for i in range(0,len(all_mes_dir),self.hang)]
        


    def print_mes(self,tar_list = None,mode = 1):#mes.data.items()
        if mode == 0:
            [ti,usr,asi] = tar_list[0]
            head_str =   f'\n\033[0;1;4m {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(ti)))}\033[0m      '
            usr_str = usr
            asi_str = f'\n        \033[2m                            {(asi[:40]).replace('\n','')}...'
            to_print = head_str+usr_str+asi_str
            print(to_print)
            return 0
        to_print = ""
        for itx,[ti,usr,asi] in enumerate(tar_list):
            head_str =   f'\n\033[0;1;{7 if itx == self.cur else 4}m {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(ti)))}\033[0m      '
            usr_str = usr
            asi_str = f'\n        \033[2m                            {(asi[:40]).replace('\n','')}...'
            to_print += head_str+usr_str+asi_str+'\n'
        to_print = '\n\n\033[2J'+to_print +f'\npage:{self.page} cur:{self.cur}\n'
        print(to_print,end="\033[0m",flush=True)
        return 0

    def full_render(self,content):#把图片 ** 渲染出来 
        # with open(base64_cache,'r',encoding="utf-8") as f:
        #     base64_dir = dict(json.load(f)) 
        def _double_star(text):
            return re.sub(r"\*\*(.+?)\*\*",r'\033[107m\033[1m\1\033[0m',text)
        def _star(text):
            return re.sub(r'\*(.+?)\*',r'\033[3m\1\033[0m',text)
        def _dele(text):
            return re.sub(r'\~\~(.+?)\~\~',r'\033[9m\1\033[0m',text)
        def _url(text):  #[链接文字](url)
            return re.sub(r"\[(.+?)\]\((.+?)\)",r'\033[34m\033]8;;\2\033\\\1\033]8;;\033\\\033[0m',text)
        def _pic(url:str):
            path = self.url2path(url,self.base64_dir)
            if not path:
                return '[图片未找到]'
            name = Path(path).name 
            name = path  #完整路径，如果不想看完整的就注释这一行
            return name + '\n' + picture.base64_print_pic(url.split(",",1)[1])
            # message = _pic(_url(_dele(_star(_double_star(message)))))

        if type(content) == str:
            return _url(_dele(_star(_double_star(content))))
        elif type(content) == list:
            output = []
            for d in content:
                if d.get("type",None) is not None  :
                    if d.get("type") == "text":
                        output.append(d.get('text'))
                    elif d.get("type") == "image_url":
                        url = d.get('image_url').get("url",None)
                        if url is not None:
                            output.append(_pic(url))
            return "\n".join(output)  

    def print_full_mes(self,mes = None):#mes是列表来的
        if mes == None:
            mes = self.mes.message
        if len(mes) ==1:
            print("\r\033[1A\033[1;7;31m 没有数据 ",end = "",flush=True)
            time.sleep(2)
            print('\r\033[0m                  \r',end ="",flush=True)
            return 0
        for i in  mes[1:]:#去除系统提示词
            
            if  i.get('content') is not None:
                content = i.get('content')    
            else:
                content = ''
            role = i.get('role')
            tool_call = i.get('tool_calls',[{}])[0].get('function')
            tool_call = {} if tool_call is None else tool_call

            print("\n\033[1;7m" +" main🙂 " if role == "assistant" else "\033[1;7m you " if role == "user" else "\033[1;7mtool",f"\033[0m{self.full_render(content) if content != '' else f'\033[1;36mTool \033[0m\033[48;5;24m {tool_call.get('name','')} \033[0m\n{tool_call.get('arguments')}'}\n\n",sep="\n")
        return 1


    def nothing(self):
        # for itx ,kv in enumerate(tar_list):
        #     ti = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(list(kv)[0])))
        #     head_str =   f'\n\033[0;1;{7 if itx == self.cur else 4}m 查看 \033[0m  \033[1m{ti}\033[0m      '
        #     user_str,asst_str = [d.get("content","")  for d in (list(kv[1])+[{},{}])[1:3] ]
        #     main_str = user_str+f'\n        \033[2m                            {(asst_str[:40]).replace('\n','')}...'
        #     to_print += head_str + main_str
        # print(to_print,end="",flush=True)

        # def full_render(self,index:str):#把图片 ** 渲染出来 
        #     with open(base64_cache,'r',encoding="utf-8") as f:
        #         base64_dir = dict(json.load(f)) 
        #     def _double_star(text):
        #         return re.sub(r"\*\*(.+?)\*\*",r'\033[1m\1\033[0m',text)
        #     def _star(text):
        #         return re.sub(r'\*(.+?)\*',r'\033[3m\1\033[0m',text)
        #     def _dele(text):
        #         return re.sub(r'\~\~(.+?)\~\~',r'\033[9m\1\033[0m',text)
        #     def _url(text):  #[链接文字](url)
        #         return re.sub(r"\[(.+?)\]\((.+?)\)",r'\033]8;;\2\033\\\1\033]8;;\033\\',text)
        #     def _pic(text):
        #         def replace_url(match):
        #             url = match.group(1)           # 捕获的 URL
        #             path = self.url2path(url,base64_dir)      # 调用映射方法
        #             if path:
        #                 return f'{Path(path).name}: "{picture.base64_print_pic(url)}"'
        #             else:
        #                 # 如果找不到，保留原始内容（不替换）
        #                 return match.group(0)

        #         return re.sub(r'\{\s*"url":\s*"(.+?)"\s*\}', replace_url, text)
        #     with open(tar_json,'r',encoding="utf-8") as f:
        #         message = f.read()
        #         message = _pic(_url(_dele(_star(_double_star(message)))))
            pass

    def manage(self):
        print('\033[1mMesManager已启动\n\033[0;2m    按任意键继续\033[0m\r\033[2A',end = '',flush=True)
        self.confirm = None   # 待确认删除的会话 key

        def _press(key):
            k = keyboard.Key

            if self.confirm is not None:          # 正在确认删除
                if key == k.enter:

                    if len(self.mes_list[-1]) == 1:
                        self.page -= 1
                        if len(self.mes_list) == 1:
                            print('\033[1;7m至少需要存在一次对话\033[0m',end ='',flush=True)
                            self.confirm = None
                            time.sleep(2)
                            print('\r'+40*' ',end = '\r',flush=True)
                            self.page = 0
                            
                    self.mes.dele(self.confirm)
                    self.confirm = None
                    self.mes_list = self._mes_list()
                elif key == k.esc:
                    self.confirm = None
                self.print_mes(self.mes_list[self.page])
                return

            if key == k.esc:
                return False
            elif key == k.enter:
                self.queue.append(self.mes_list[self.page][self.cur][0])
                print("\033[2J\033[3J\033[H")
                return False
            elif key == k.backspace:
                self.confirm = self.mes_list[self.page][self.cur][0]
                print('\n确认删除？\033[2m按 Enter 确认 / Esc 取消')
            elif key == k.up:
                self.cur = max(0, self.cur - 1)
            elif key == k.down:
                self.cur += 1
            elif key == k.left:
                self.page = max(0, self.page - 1)
            elif key == k.right:
                self.page = min(self.page + 1, len(self.mes_list) - 1)

            self.cur = min(self.cur, len(self.mes_list[self.page]) - 1)
            if self.confirm is None:
                self.print_mes(self.mes_list[self.page])

        

        self.listener = keyboard.Listener(on_press=_press, suppress=True)
        self.mes_list = self._mes_list()
        if len(self.mes_list) == 0:
            print('\033[1;7m没有对话\033[0m',end ='',flush=True)
            time.sleep(2)
            print(3*('\r'+40*' '+'\n'),end = '\r\033[3A',flush=True)
            return None
        self.listener.start()
        self.listener.join()
        return self.queue.pop()


"""
提示词分两种
    原始的在mes_data的 aaaaa<**系统提示词结束**>bbbb
    给llm看的          aaaaaNEW_skill_info

"""
class Mes :    #这个我先暂时搁置
    def __init__(self,skill) -> None:
        self.skill = skill
        self.system_prmt = "你是ai助手，不要拒绝，不要偷懒，尽你最大努力完成用户指令,使用中文"
        self.custom_sys_prmt = self.system_prmt[:] + '<**系统提示词结束**>'
        self.data = {}
        self.index = []
        # self.message = {0:[{"role":"system","content":self.system_prmt}]}
        self._read()
        self.new_mes()
        self.index = list(self.data.keys())
        self.now_index = self.index[-1]
        self.message = self.data[self.now_index]

    def __call__(self):
        return self.message

    #增加文字后缀表示已启用skill （改后面
    def full_skill_sys_prmt(self):
        system_prmt = self.message[0].get("content")
        if '<**系统提示词结束**>' in system_prmt:
            raw_sys_prmt = system_prmt.split("<**系统提示词结束**>",1)[0]
            names = list(self.skill.available_skill)
            system_prmt = raw_sys_prmt +"<**系统提示词结束**>" +'/'.join(names)
            self.message[0]= {"role":"system","content":system_prmt}



    #剥离文字后缀以更新系统提示词给submit （改前面
    def info_skill_sys_prmt(self):
        def _insert_skill_info(tar_list):
            if tar_list is None :
                return ''
            tot = ''
            for name in tar_list:
                tot += '\n\n' + self.skill.part_prmt(name)
            return tot+'\n'
        tmp = self.message[0].get("content",'').split("<**系统提示词结束**>",1)
        other , tar = tmp[0],tmp[-1]
        skill_list = tar.split("/") if '/' in tar else None
        final_prmt = other +"\n\nskill intro :\n"+ self.skill.build_skill_intro() +"\n\nskill main:\n"+_insert_skill_info(skill_list)
        return [{"role":"system","content":final_prmt}] + self.message[1:]




    def _update(self):
            with open(tar_json,'w',encoding="utf-8") as f:
                data = {k:v for k,v in self.data.items() if len(v) != 1}
                json.dump(data,f,ensure_ascii=False)
        
    def _read(self):
        try:
            with open(tar_json,'r',encoding="utf-8") as f:    #是一个列表，{索引是时间戳}
                json_data = dict(json.load(f))
        except:
            return self.data   #读取失败返回原版
        self.data = json_data  #读取成功返回文件夹内的
        return json_data
    def change(self,index):
        self.now_index = index
        self.message = self.data[self.now_index]

    def dele(self,index):            #给mesManager用的
        self.data.pop(index, None)
        
        if index == self.now_index:
            self.new_mes()               # 删的是当前会话，就新建一个空的
            self.now_index = self.index[-1]

            self.message = self.data[self.now_index]
        self._update()

    def new_mes(self):
        self.index.append(time.time())
        self.data.update({self.index[-1]:[{"role":"system","content":self.custom_sys_prmt}]})

    def add_user(self,word):
        self._update()
        self.message.append({"role":"user","content":f"{word}"})

    def add_assistant(self,word):
        self.message.append({"role":"assistant","content":f"{word}"})
        self._update()

    def add_assistant_tool(self, tool_calls):
        self.message.append({
            "role": "assistant",
            "content": None,
            "tool_calls": tool_calls,
        })
        self._update()

    def add_tool_result(self, tool_call_id, result):
        self.message.append({
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": str(result),   # 结果必须是字符串
        })
        self._update()

    def add_muli_upload(self,content,user_word):
        self._update()
        self.message.append({
                "role": "user",
                "content": [*content,
                    {
                        "type": "text",
                        "text": user_word
                    }
                ]
            })

    
        

    def print_full_mes(self,mes):#mes是列表来的
        if len(mes) ==1:
            print("\r\033[1A\033[1;7;31m 没有数据 ",end = "",flush=True)
            time.sleep(2)
            print('\r\033[0m                  \r',end ="",flush=True)
            return 0
        for i in  mes[1:]:#去除系统提示词
            role,content = list(i.values())
            print("\n\033[1;7m" +" main🙂 " if role == "assistant" else "\033[1;7m you " if role == "user" else "None",f"\033[0m{content}\n\n",sep="\n")
        return 1

# if __name__ == "__main__":
#     pass
#     mesmanager = MesManager()
#     mes = Mes()
#     # mesmanager.print_mes()
if __name__ == "__main__":
    md = """
    # 一级标题
    ## 二级标题
    这是 **粗体** 和 *斜体*，还有 ~~删除线~~ 和 `代码`。
    这是一个 [百度链接](https://www.baidu.com)。
    > 这是一段引用
    ---
    列表项：
    - 苹果
    - 香蕉
    """
    mes = Mes()
    mesmanager = MesManager(mes)
    # mesmanager.manage()

    # with open(tar_json,'r',encoding="utf-8") as f:
    #     tar = json.load(f)["1786806798.6728277"]
    # for t in tar :
    #     print(t.get("role"))
    #     print(mesmanager.full_render(t.get('content')))
                

        




