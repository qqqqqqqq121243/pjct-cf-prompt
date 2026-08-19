import threading
import time
import random

# progress_moon = ['🌘', '🌗', '🌖', '🌕', '🌔', '🌓', '🌒', '🌑']
# class P_moon():
#     def __init__(self) :
#         self.count = 0
#         self.event = threading.Event
#     def __str__(self):
#         self.count += 1
#         return progress_moon[self.count % len(progress_moon)]
#     def wait():
#         pass
        

# p_moon = P_moon()
class Loading(threading.Thread):
    def __init__(self) -> None:
        super().__init__()
        self.get_res = threading.Event()
        self.pic = ['🌘', '🌗', '🌖', '🌕', '🌔', '🌓', '🌒', '🌑']
        

    # def hide(self,func):
    #     def inner():
    #         print("\033[?25l")
    #         func()
    #         print("\033[?25h")
    #     return inner
    def run(self):
        print("\033[?25l",end ="",flush= True)
        try:
            count = 0
            while not self.get_res.is_set():
                print(f"{self.pic[count%len(self.pic)]}\r",end = "")
                time.sleep(0.15)
                count += 1
        finally:
            print("\033[1A\033[?25h",end ="",flush= True)



    # def fake_response():
    #     time.sleep(random.randint(3,7))
    #     get_res.set()
    #     print("\a启动")

# loading_thread = threading.Thread(target=loading)
# loading_thread.start()
# fake_response()
# loading_thread.join()