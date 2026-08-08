
progress_moon = ['🌘', '🌗', '🌖', '🌕', '🌔', '🌓', '🌒', '🌑']
class P_moon():
    def __init__(self) :
        self.count = 0
    def __str__(self):
        self.count += 1
        return progress_moon[self.count % len(progress_moon)]
    
p_moon = P_moon()
# import time
# for i in range(10):
#     print(f"\r{p_moon}",flush=True,end = "")
#     time.sleep(0.1)