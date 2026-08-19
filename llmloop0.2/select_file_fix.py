import base64
from pathlib import Path
import hashlib
import json
import queue
import tkinter as tk
from tkinter import filedialog
import pynput.keyboard as keyboard
from data.siliconflow_model_info import ori_setting
cache_file = Path(__file__).parent / "data" / "base64_cache.json"

class Select_File:
    def __init__(self) -> None:
        # with open("O:\\project\\pjct-cf-prompt\\llmloop0.2\\data\\models_config.json", 'r', encoding="utf-8") as f:
        self.model_info = ori_setting

        self.file_list = []
        self.loac = 0
        self.key_queue = queue.Queue()
        self.root = None
        self.listener = None

    def selec_file(self):
        self.root.attributes('-topmost', True)   # 置顶
        file_path = filedialog.askopenfilename(title="请选择一个文件")
        # self.root.attributes('-topmost', False)  # 弹完取消
        self.root.lift()
        if file_path:
            with open(file_path,'rb') as f:
                file_b = f.read()
            b64_str = base64.b64encode(file_b).decode("utf-8")
            name,typ = file_path.rsplit(".",1)
            url = f"data:image/{typ.lower()};base64,{b64_str}"
            return [[name,typ],url]
        return [[None, None], ""]

    def _press(self,key):
        self.key_queue.put(key)

    def select_info(self,model_name):
        self.file_list = []
        self.loca = 0

        self.root = tk.Tk()
        self.root.withdraw()

        self.listener = keyboard.Listener(on_press=self._press,suppress=True)
        self.listener.start()

        def handle_key(key):
            if key == keyboard.Key.up:
                if self.loca != 0:
                    self.loca -= 1
            elif key == keyboard.Key.down:
                if self.loca != len(self.file_list):
                    self.loca += 1
            elif key == keyboard.Key.backspace:
                if self.loca != 0:
                    self.file_list.pop(self.loca - 1)
                    self.loca -= 1
            elif key == keyboard.Key.enter:
                if self.loca != 0:
                    self.file_list.pop(self.loca - 1)
                    self.loca -= 1
                else:
                    self.listener.stop()
                    try:
                        self.file_list.append(self.selec_file())
                    finally:
                        self.listener = keyboard.Listener(on_press=self._press, suppress=True)
                        self.listener.start()
            elif key == keyboard.Key.esc:
                return False
            print_files(model_name)
            return True

        def print_files(model_name):
            new_str = "\033[32m选择\033[0m\n" if self.loca != 0 else "\033[102m选择\033[0m\n"
            file_list_str = "\n".join(
                f"\033[1;97m{n} - \033[0;4m{t}"
                f' {"\033[41m" if itx == self.loca - 1 else "\033[31m"}删除\033[0m'
                for itx, [(n, t), _] in enumerate(self.file_list) if self.file_list
            )
            model_info_str = (
                f"\033[1;3;7m按ESC退出 按ENTER选择 \033[0m\033[1;7;111m{model_name}\033[0m 可用: \033[1;4m"
                + " ".join(s for i, s in enumerate(["视觉", "音频", "视频"])
                           if self.model_info[model_name][i + 1])
            )
            print("\033[2J\033[2H" + model_info_str + "\n" + new_str + file_list_str,
                  self.loca, sep="\n", flush=True)


        print("\033[?25l", end="", flush=True)
        print_files(model_name)

        while True:
            try:
                key = self.key_queue.get(timeout=0.05)
            except queue.Empty:
                self.root.update()
                continue 

            try:
                if handle_key(key) is False:
                    break
            except Exception as e:
                print(e)


        
        self.listener.stop()
        print("\n\033[?25h", end="", flush=True)
        self.root.destroy()
                                    #这是url
        hash_dict = { hashlib.md5(i[-1].encode("utf-8")).hexdigest():i[0][0]+"."+i[0][1] for i in self.file_list if i[0][0] != None}

        with open(cache_file,'a+',encoding="utf-8") as f:
            f.seek(0)
            data = f.read()
            caches = dict(json.loads(data)) if data.strip() != '' else {}
            caches.update(hash_dict)
            f.seek(0)
            f.truncate()
            json.dump(caches, f, ensure_ascii=False)

        return [i for i in self.file_list if i[0][0] != None]


if __name__ == "__main__":
    print("测试启动")
    sel = Select_File()
    print([i[0] for i in sel.select_info("moonshotai/Kimi-K2.7-Code")])
