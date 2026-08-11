"""
**readme**

这个代码是我拿来学习的，你可以指导，但是不要修改



"""


import threading
import json
from tkinter import N
import requests
import time
from siliconflow_model_info import list_model_poor  #硅基流动穷鬼模型名单

from sk import secret_key 
import pynput.keyboard as keyboard




important_tag= [
    "Tools", "全模态",            # 你已有的
    "视觉", "多模态理解 / 识别",   # 视觉/文档
    ]

class Own:   #之后要单开一个来存储
    def __init__(self) -> None:
        

        self.sk = {"Qwen/Qwen3.5-27B":secret_key,
                    "Qwen/Qwen3-Omni-30B-A3B-Instruct":secret_key,
                    "zai-org/GLM-4.5V":secret_key}
        self.current = list(self.sk.keys())[0]   #决定了选哪一个模型

        with open(f'O:/project/pjct-cf-prompt/llmloop/models_details.json','r',encoding="utf-8") as f:
            aval_model = list(json.load(f))
        poor_m = list_model_poor
        all_m = [(item.get("name"),item.get("date",""),1 if item.get("name") in poor_m else 0) for item in aval_model if item.get("name") not in self.sk.keys()]
        self.unload_model = all_m     #特供补丁
        self.workspace = "O:/project/pjct-cf-prompt/llmloop"

    def __iter__(self):
        return iter(self.sk)
    def test_sk(self,m ,s):   #先只做硅基流动的 来验证sk
        test = requests.post(
            "https://api.siliconflow.cn/v1/chat/completions",
            headers={"Authorization": f"Bearer {s}", "Content-Type": "application/json"},
            json={
                "model": f"{m}",
                "messages": [{'role':'user',"content":"test"}],
            }
        )
        sta = int(test.status_code)

        sta_code = {200:"key有效",
                    401:"Unauthorized - key 无效/格式错（比如多空格、被截断）",
                    400:"Bad Request - 请检查参数是否正确",
                    403:"Forbidden - key 无权限 / 余额问题 / 风控",
                    429:"限流或余额不足"}

        print(sta_code.get(sta,"未收录的状态码"))

        return  1 if sta == 200 else 0

    def select_model(self,tar_list = None):  #  (name date 是否在穷鬼名单)
        if tar_list is None :
            tar_list = self.unload_model   #超级补丁
        
        self.tmp_model = None   #用来给增加模型时，暂时存放选择的模型

        def print_model(page,tar):
            print("\033[2H")   #回到左上角

            for itx,m in enumerate(tar_list[page * 10 :(page + 1) * 10]):
                #红色字体(31)，选择框为红色(41)，穷鬼模型为加粗(1)
                print(f"\n\033[{1 if m[-1] == 1 else 0};{41 if tar == itx else 31}m{m[0]}"+f"\033[0m - {m[1]}"+50*" ",end="",flush=True)  

            

        def user_select_model(key):
            if key == keyboard.Key.left:
                self.page = max(self.page - 1, 0)  #防止变 -1

            elif key == keyboard.Key.right:
                self.page = min(self.page + 1, (len(tar_list)-1)//10) 

            elif key == keyboard.Key.up:
                if self.tar == 0 and self.page != 0:
                    self.tar = 9 
                    self.page = max(self.page - 1, 0)  
                else:
                    self.tar = max(self.tar - 1, 0)  
            elif key == keyboard.Key.down:
                if self.tar == 9 and self.page != (len(tar_list)-1)//10:
                    self.tar = 0
                    self.page = min(self.page + 1, (len(tar_list)-1)//10) 
                else:
                    self.tar = self.tar + 1         #min(self.tar + 1, len(all_m)-self.page*10-1) 
            elif key == keyboard.Key.esc :
                self.tmp_model = None
                return False
            elif key == keyboard.Key.enter:
                self.tmp_model = tar_list[self.page*10 + self.tar][0]
                return False
            
            self.tar = min(self.tar,len(tar_list)-self.page*10 -1)
            print_model(self.page,self.tar)

            # print("\033[2J")   #清屏
            # for itx,m in enumerate(all_m[self.page * 10 :(self.page + 1) * 10]):
            #     #红色字体(31)，选择框为红色(41)，穷鬼模型为加粗(1)
            #     print(f"\033[{1 if m[-1] == 1 else 0};{41 if self.tar == itx else 31}m{m[0]}",end="")  
            #     print(f"\033[0m - date {m[1]}")


        # all_m = all_m if len(all_m) % 10 == 0 else all_m + [("None",None,0) for _ in range(10 - len(all_m)%10)]


        self.page = 0
        self.tar = 0
        print("\033[?25l", end="", flush=True)   # 进入选择界面时隐藏
        print_model(0,0) #打印模型列表
        #用户操作
        with keyboard.Listener(on_press=user_select_model,suppress=True) as listener:
            try:
                listener.join()
            except KeyboardInterrupt:      
                self.tmp_model = None
        print("\n\033[?25h", end="", flush=True)   # 退出时恢复
        return self.tmp_model


    def add_sk(self):
        print("\033[2J")
        mdl = self.select_model()
        print("\033[2J")
        if mdl == None :
            return 0 
        elif mdl not in list_model_poor:
            print("你当前所选择的模型不在代金卷名单内\n若要添加, 请输入 /y\n若取消添加, 请输入 /n")
            for turn in range(3,0,-1):   #事不过三
                u_input = input(f"({turn})you-")
                if u_input ==  "/y":
                    break
                elif u_input == "/n":
                    return 0
            else:
                return 0
        skey = input("请输入 api-key\n")
                    
        code = self.test_sk(mdl,skey)

        if code:
            self.sk.update({mdl:skey})
            print(f"模型 {mdl} 添加成功")
user = Own()


class Model_Config :
    def __init__(self) -> None:
        # 获得默认设定
        with open("O:/project/pjct-cf-prompt/llmloop/models_config.json",'r',encoding="utf-8") as f :
            ori_setting = json.load(f)

        self.user_setting= ori_setting
        self.ori_setting = ori_setting
    
    def __call__(self,model_name:str):      #默认返回用户设置
        return self.user_setting
    
    def change_setting(self,args:tuple,model_name:str):
        def legal_test(new_args:tuple,model_name:str) -> bool:         #检查是否设置合法
            test_result = map(lambda x : x[0]!= 0 and x[0] == 0 or x[0]==-1, ((usr,syt) for usr,syt in zip(new_args,self.ori_setting.get(model_name,(-1,)))))
            if False in test_result:
                print("illegal setting")
                return 0
            print("legal setting")
            return 1

        if legal_test(args,model_name):
            self.user_setting[model_name] = args

model_config = Model_Config()   


def api_counter(func):
    def insider(*arg,**kwargs):
        time0 = time.time()
        result = func(*arg,**kwargs)
        time1 = time.time()
        print(f"\n用时{(time1-time0):.2f}s")
        return result
    return insider


client = requests.Session()


class Mes :    #这个我先暂时搁置
    def __init__(self) -> None:
        self.prmt = {0:[{"role":"system","content":"你是ai助手"}]}
        self.count = 1
    
    def new_mes(self):
        self.count += 1
        self.prmt.update({self.count:[{"role":"system","content":""}]})
messages = Mes()
mes = messages.prmt[0]

@api_counter
def res():  
    """
    请求 + 流式输出
    
    """
    def load_model_config(json_arg:dict,model_name:str)->json:    #这里的user_config最好是一个全局变量或者是self.
        try:
            if model_config[user.current][0] == 1:
                json_arg.update({"enable_thinking": True})
            elif model_config[user.current][0] == 2:
                json_arg.update({"model":model_name.replace("Instruct","Thinking")})
            return json_arg

        except:
            return json_arg


    def res_submit(json_arg):
        resp = client.post(
        "https://api.siliconflow.cn/v1/chat/completions",
        headers={"Authorization": f"Bearer {user.sk.get(user.current)}", "Content-Type": "application/json"},
        json=load_model_config(json_arg,user.current),
        stream=True,
    )
        return resp

    def response_parse(response:requests.Response):
        to_sent,pre_status,status = "","None","None"
        thinking_con = ""
        con = ""
        print()
        for line in response.iter_lines():
            to_sent = ""
            if not line or not line.startswith(b"data:"):
                continue
            if line.startswith(b"data: [DONE]"):
                break
            data = json.loads(line[5:])
            if not data.get("choices"):   # 空 choices 的收尾 chunk，跳过
                if data.get("usage"):
                    usage = data.get("usage")
                    print(f"\n\ncompletion_tokens : {usage['completion_tokens']} - total_tokens{usage['total_tokens']}")
                    break
                continue
            delta = data["choices"][0]["delta"]

            if delta.get("reasoning_content"):
                status = "thinking☁"
                to_sent = delta['reasoning_content']
                thinking_con += delta.get("reasoning_content")
            elif delta.get("content"):
                status = "main🙂"
                to_sent = delta['content']
                con += delta.get("content")
            if pre_status != status :
                if status == "main🙂":
                    print(f"\n\n{status}",end='',flush=True)
                elif status == "thinking☁":
                    pass

            print(to_sent,end='',flush=True)
            pre_status = status
        mes.append({"role":"assistant","content":f"{con}"})

    json_config = {
            "model":f"{user.current}",# default -> "Qwen/Qwen3.5-27B"
            "messages": mes,
            "stream": True,}
    response = res_submit(load_model_config(json_arg=json_config,model_name=user.current))
    response_parse(response)



    


    # for line in resp.iter_lines():

    #     to_sent = ""
    #     if not line or not line.startswith(b"data:"):
    #         continue
    #     # if line.startswith(b"data: [DONE]"):
    #     #     break
    #     data = json.loads(line[5:])
    #     if not data.get("choices"):   # 空 choices 的收尾 chunk，跳过
    #         if data.get("usage"):
    #             usage = data.get("usage")
    #             print(f"\n\ncompletion_tokens : {usage['completion_tokens']} - total_tokens{usage['total_tokens']}")
    #             break
    #         continue
    #     delta = data["choices"][0]["delta"]

    #     if delta.get("reasoning_content"):
    #         status = "thinking☁"
    #         to_sent = delta['reasoning_content']
    #         thinking_con += delta.get("reasoning_content")
    #     elif delta.get("content"):
    #         status = "main🙂"
    #         to_sent = delta['content']
    #         con += delta.get("content")
    #     if pre_status != status :
    #         if status == "main🙂":
    #             print(f"\n\n{status}",end='',flush=True)
    #         elif status == "thinking☁":
    #             pass

        
    #     print(to_sent,end='',flush=True)
    #     pre_status = status



"""
主循环

"""

if __name__ == "__main__" :
    print(f"\033[2J/m -查询可用模型\n/a -增加模型\n/c -选择模型\n当前模型: \n{user.current}\n")
    while 1:
        u_input = input("you:")
        if u_input == "/m":         #查看可用模型
            print("可用模型：\n\033[31m","\n".join([f"{m}" for m in list(user.sk.keys())]),"\033[0m" ,sep = '\n')
            continue

        elif u_input == "/a":       #添加可用模型
            user.add_sk()
            continue
        elif u_input == "/c":        #选择模型
            print("\033[2J")         #清屏
            name = user.select_model(tar_list=[(name,"",1 if name in list_model_poor else 0) for name in list(user.sk.keys())])
            if name :
                user.current = name 
                print(f"选择了{name}")
            continue

        elif u_input == "/e":
            break

        mes.append({"role": "user", "content": f"{u_input}"})
        res()



"""
完成了 增加模型

todo
    选择模型
    模型详情
    功能开关
    多模态上传
    skill兼容

"""
