import threading

waiting_cond = threading.Condition()
progress_moon = ['🌘', '🌗', '🌖', '🌕', '🌔', '🌓', '🌒', '🌑']
class P_moon():
    def __init__(self) :
        self.count = 0
    def __str__(self):
        self.count += 1
        return progress_moon[self.count % len(progress_moon)]
    def wait():
        pass
        

p_moon = P_moon()
