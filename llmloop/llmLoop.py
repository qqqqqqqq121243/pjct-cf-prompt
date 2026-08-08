"""
**readme**

这个代码是我拿来学习的，你可以指导，但是不要修改



"""


import json
import requests
import time
from siliconflow_model_info import list_model_poor  #硅基流动穷鬼模型名单
from progress import p_moon
from sk import secret_key as sk



def api_counter(func):
    def insider(*arg,**kwargs):
        time0 = time.time()
        result = func(*arg,**kwargs)
        time1 = time.time()
        print(f"用时{(time1-time0):2f}s")
        return result
    return insider



class Own():   #之后要单开一个来存储
    def __init__(self) -> None:
        self.default = 0   #决定了选哪一个模型
        self.sk = {"Qwen/Qwen3.5-27B":sk,
                    "Qwen/Qwen3-Omni-30B-A3B-Instruct":sk,
                    "zai-org/GLM-4.5V":sk}
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

client = requests.Session()

user = Own()

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
            "enable_thinking": True,
        },
        stream=True,
    )
    thinking_con = ""
    con = ""
    print()

    for line in resp.iter_lines():
        to_sent = ""
        if not line or not line.startswith(b"data:"):
            # print(f"\r{p_moon}",flush=True,end = "")
            continue
        if line.startswith(b"data: [DONE]"):
            break
        data = json.loads(line[5:])
        if not data.get("choices"):   # 空 choices 的收尾 chunk，跳过
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
        if pre_status != status and status == "main🙂":
            print(f"\n\n{status}",end='',flush=True)
        print(to_sent,end='',flush=True)
        pre_status = status
    mes.append({"role":"assistant","content":f"{con}"})
    print()


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
