"""
**readme**

这个代码是我拿来学习的，你可以指导，但是不要修改



"""

import threading
import json
import requests
import time
from siliconflow_model_info import list_model_poor  #硅基流动穷鬼模型名单
from progress import p_moon
from sk import secret_key 
import pynput.keyboard as keyboard




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

    def select_model(self):
        
        self.tmp_model = None   #用来给增加模型时，暂时存放选择的模型
        with open(f'O:/project/pjct-cf-prompt/llmloop/models_details.json','r',encoding="utf-8") as f:
            aval_model = list(json.load(f))
        poor_m = list_model_poor
        all_m = [(item.get("name"),item.get("date"),1 if item.get("name") in poor_m else 0) for item in aval_model if item.get("name") not in user.sk.keys()]

        def print_model(page,tar):
            print("\033[2H")   #回到左上角

            for itx,m in enumerate(all_m[page * 10 :(page + 1) * 10]):
                #红色字体(31)，选择框为红色(41)，穷鬼模型为加粗(1)
                print(f"\n\033[{1 if m[-1] == 1 else 0};{41 if tar == itx else 31}m{m[0]}"+f"\033[0m - {m[1]}"+50*" ",end="")  

            

        def user_select_model(key):
            if key == keyboard.Key.left:
                self.page = max(self.page - 1, 0)  #防止变 -1

            elif key == keyboard.Key.right:
                self.page = min(self.page + 1, (len(all_m)-1)//10) 

            elif key == keyboard.Key.up:
                if self.tar == 0:
                    self.tar = 9
                    self.page = max(self.page - 1, 0)  
                else:
                    self.tar = max(self.tar - 1, 0)  
            elif key == keyboard.Key.down:
                if self.tar == 9:
                    self.tar = 0
                    self.page = min(self.page + 1, (len(all_m)-1)//10) 
                else:
                    self.tar = min(self.tar + 1, 9) 
            elif key == keyboard.Key.esc :
                self.tmp_model = None
                return False
            elif key == keyboard.Key.enter:
                self.tmp_model = all_m[self.page*10 + self.tar][0]
                return False
            
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


# class Model_Config :
#     def __init__(self) -> None:
#         # 获得默认设定
#         with open("O:/project/pjct-cf-prompt/llmloop/models_config.json",'r',encoding="utf-8") as f :
#             ori_setting = json.load(f)
#         self.current_model = user.default
#         self.user_setting= ori_setting
#         self.ori_settting = ori_setting
    
#     def __call__(self,model):
        






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

    json_args = {
            "model":f"{list(user.sk.keys())[user.default]}",# default -> "Qwen/Qwen3.5-27B"
            "messages": mes,
            "stream": True,
        }

    to_sent,pre_status,status = "","None","None"

    resp = client.post(
        "https://api.siliconflow.cn/v1/chat/completions",
        headers={"Authorization": f"Bearer {list(user.sk.values())[user.default]}", "Content-Type": "application/json"},
        json=json_args,
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
    print(f"\033[2J/m -查询可用模型\n/a -增加模型\n\n当前模型: \n{list(user.sk.keys())[user.default]}\n")
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
