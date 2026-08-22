"""
还要添加一个判断图片宽度决定换行的

"""
import base64
from io import BytesIO
from PIL import Image
class Pic:
    def __init__(self) -> None:
        self.tar_y = 20
        self.tar_y *= 2
        self.top_half = '▀'

    def _base64_to_image(self,base64_str):
        image_data = base64.b64decode(base64_str)
        image = Image.open(BytesIO(image_data))
        
        return image

    def _resize_for_terminal(self,image):
        raw_x , raw_y = image.size
        aspect = raw_x/raw_y
        tar_x = int(self.tar_y * aspect)
        return image.resize((tar_x,self.tar_y), Image.Resampling.LANCZOS)

    def _image_to_terminal(self,image):
        img = self._resize_for_terminal(image)
        w,h = img.size
        img = img.convert("RGB")
        pi = img.load()

        to_print = []
        for y in range(0,h,2):
            line = []
            for x in range(w):
                r1 ,g1 ,b1  = pi[x,y]

                if y + 1 < h:
                    r2 ,g2 ,b2 = pi[x,y+1]

                else :
                    r2 ,g2 ,b2 = 0, 0, 0
                single_pi = f'\033[48;2;{r1};{g1};{b1}m\033[38;2;{r2};{g2};{b2}m{self.top_half}' 
                line.append(single_pi)
            to_print.append(''.join(line)+'\033[0m')

        return '\n'.join(to_print)

    def path_print_pic(self):#测试用
        test_path = "C:\\Users\\mahto\\Pictures\\Screenshots\\屏幕截图 2026-08-05 214408.png"
        with Image.open(test_path) as p:
            fin_p = self._image_to_terminal(self._resize_for_terminal(p))
        print(fin_p)
        p.close()
    def base64_print_pic(self,base64_str):
        p = self._base64_to_image(base64_str)
        fin_p = self._image_to_terminal(self._resize_for_terminal(p))
        p.close()
        return fin_p