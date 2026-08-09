"""
**readme**

这个代码是我拿来学习的，你可以指导，但是不要修改



"""

import threading
import json
from re import M
from turtle import Turtle
import requests
import time
from siliconflow_model_info import list_model_poor  #硅基流动穷鬼模型名单
from progress import p_moon
from sk import secret_key 




important_tag= [
    "Tools", "全模态",            # 你已有的
    "视觉", "多模态理解 / 识别",   # 视觉/文档
    ]

class Own():   #之后要单开一个来存储
    def __init__(self) -> None:
        self.default = 0   #决定了选哪一个模型
        self.sk = {"Qwen/Qwen3.5-27B":secret_key,
                    "Qwen/Qwen3-Omni-30B-A3B-Instruct":secret_key,
                    "zai-org/GLM-4.5V":secret_key}
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

    def add_sk(self):
        mdl = input("请输入模型名称\n")
        if mdl not in list_model_poor:
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

        self.current_model = user.default
        self.ori_setting = {k:[] for k in user.sk.keys(),}
        # 思考（特殊，我把单独的思考模型认为是第三类） 视觉（0，1，2） 全模态 视频输入(特殊要手动开启，全模态自带)

    def check(self,to_chcek_model :str):
        with open(f'O:\project\pjct-cf-prompt\llmloop\models.json','r',encoding="utf-8") as f:
            aval_model = list(json.load(f))
            aval_model_processed = {i.get["name"]:i for i in aval_model}
            print(aval_model_processed)

            if "Instruct" in to_chcek_model and to_chcek_model.replace("Instruct","Thinking") in aval_model :
                pass




    

class Model_Tag():
    def __init__(self) -> None:

        with open(f'O:\project\pjct-cf-prompt\llmloop\models.json','r',encoding="utf-8") as f:
            aval_model = list(json.load(f))
        collect_tags = [i['tags'] for i in aval_model]
        c = {j for i in collect_tags for j in i}
        self.items = c
model_tag = Model_Tag()

def api_counter(func):
    def insider(*arg,**kwargs):
        time0 = time.time()
        result = func(*arg,**kwargs)
        time1 = time.time()
        print(f"用时{(time1-time0):2f}s")
        return result
    return insider




client = requests.Session()



class Mes():    #这个我先暂时搁置
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
    to_sent,pre_status,status = "","None","None"
    resp = client.post(
        "https://api.siliconflow.cn/v1/chat/completions",
        headers={"Authorization": f"Bearer {list(user.sk.values())[user.default]}", "Content-Type": "application/json"},
        json={
            "model":f"{list(user.sk.keys())[user.default]}",# default -> "Qwen/Qwen3.5-27B"
            "messages": mes,
            "stream": True,
            "enable_thinking": ,
        },
        stream=True,
    )
    thinking_con = ""
    con = ""
    print()

    for line in resp.iter_lines():

        to_sent = ""
        # if status == "None":
            # print(f"\r{p_moon}",flush=True,end = "")    #月亮转转转进度条
        if not line or not line.startswith(b"data:"):
            continue
        # if line.startswith(b"data: [DONE]"):
        #     break
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



"""
主循环

"""

if __name__ == "__main__" :
    print(f"\n/m -查询可用模型\n/a -增加模型\n\n当前模型: \n{list(user.sk.keys())[user.default]}\n")
    while 1:
        u_input = input("you:")
        if u_input == "/m":         #查看可用模型
            print("可用模型：\n","\n\n".join([f"{n} - {m}" for n,m in enumerate(user.sk.keys())]) ,sep = '\n')
            continue

        elif u_input == "/a":       #添加可用模型
            user.add_sk()
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
