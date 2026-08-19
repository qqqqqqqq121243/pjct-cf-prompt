# for i in range(256):
#     print(f"\033[38;5;{i}m{i}{"█"*(3-(len(str(i))))}{'\n' if not i%6 else ""} ",end = "")
# status ="main🙂"
# # print(f"\r\n\033[0m\033[7;1m {status} \033[0m ",end='',flush=True)
# print("\033[107;1myou:\033[0m",end='',flush=True)
# comand_list = [("/h","查看命令列表"),('/m' ,'查询可用模型'),('/a','增加模型'),('/s' ,'选择模型'),('/t' ,'开关思考'),('/c' ,'清理对话'),("",""),('/' ,'文件上传')]
# helpful_word = "\n"+"\n".join(["\033[0m"+cmd+"  \033[2m"+wrd for cmd,wrd in comand_list])
# print(helpful_word)
r"""
当前问题
    文字 -> 完整排列问题
        判断坐标合法性
            有坐标的先排,同坐标放下一页
            没坐标的做组合
                先确定组合长度,长度超标的raise error
                确定组合种类
                从compose_law获得组合方式: 单页几个组合/优先级[默认按排列顺序,其中每页都有的组合优先级最高,同优先级排列看默认排序]
                   `-->[(1,4,5   数字组合):{位置list:行(1和1之间也不一样) None就是index最小的一个可用行,优先级: int 为-1的时候就是路边一条 满了就不排了}
                   看看会不会和已有位置冲突,先尽量在同行排



"""
from pydantic import BaseModel
import pynput.keyboard as keyboard
class BaseUI :
    def __init__(self) -> None:
        # self.select_mode = ("only_line","only_column","free")
        self.hxl = [[0,0,0,0],
                    [0,0,0,0],
                    [0,0,0,0],
                    [0,0,0,0],]     # ！0 为选项  0 为空的
        self.page = {0:self.hxl}
        self.now = [0,0,0]
        self.tar_dict = {"test":[1,["\033[7m",'\033[96m'],{'location = '}]}
        self.notice = ""  #通告栏 放在最上面或者最下面




    def word(self,tar_word:str,type01:int,effect = ['',''],location = [-1,-1,-1],suspend = None,press =None,info = None):
        return {tar_word:[type01,effect,{'location':location,'suspend':suspend,'press':press,'info':info}]}


    def _build(self,tar:list,compose_law=dict): #目标列表 [[文字，文字，文字],[(类型)，0文字，10选项与光标重合时会亮的文字，1选项]，]
                                #目标列表 [{文字：[[0文字，1选项],[光标重合效果，默认效果，{空则为默认}],
                                # {'location': [page,0,0{位置，-1则为看程序自己排}] or必要组合[自己代号int，[组合包含号码]]
                                #  "suspend": func                                        
                                # {"press" :func }   ,info:文字 ]     } ]}


        """
        先创建位置列表，后按照列表渲染
        目前设计是只要单个占了一行的某一个位置，组合就放不上去
        
        
        """
        def _add_page():
            last_page = sorted(list(self.page.keys()))[-1]
            self.page.update({last_page+1:self.hxl})
            return last_page+1
        def _creat_page(page_index):
            self.page.update({page_index:self.hxl})

        def _count_0(line:list,tar_len):
            count = 0
            for index ,l in enumerate(line):
                if l != 0:
                    count = 0
                else:
                    count += 1
                    if tar_len == count:
                        return True,index-count
            return False,None


        h,l= len(self.hxl),len(self.hxl[0]) 
        compose_list =[]
        index_to_word = {}
        for i in tar:
            [word,[type01,effect,args]] = list(i.items())[0]
            location = args.get('location',[-1,-1,-1])

            if type(location[-1]) == int and len(location) != 1:   #说明是位置排序
                [z,x,y] = location
                if x > l or y > h:
                    raise IndexError            #超出了

                elif z == -1:       #随便排
                    for p in range(sorted(list(self.page.keys()))[-1]+1):
                        if p not in list(self.page.keys()):  #说明有些页被跳过了，没创建，先创建后填入
                            _creat_page(p)
                            self.page[p][x][y] = word
                            break
                        elif not self.page[p][x][y]:  #True 说明原本是空的
                            self.page[p][x][y] = word
                            break
                    else:                               #能到这说明没位置了
                        last_page = _add_page()
                        self.page[last_page][x][y]
                else :
                    if z not in self.page.keys():
                        print(f'[warn] 页不存在: {word} page{z}')
                        continue
                    elif self.page[z][x][y]:
                        print(f'[warn] 出现位置重合: {word} page{z}')
                        continue
                    self.page[z][x][y] = word

            else:                           #组合排序
                index,group_list = loaction
                if group_list in list(compose_law.keys()):
                    if l <= len(list(i.values())[2].get('location')[-1]):
                        print(f'[warn] 超长组合{list(i.values())[0]}')
                    compose_list.append(i)
                    index_to_word.update({list(i.values())[2].get('location')[0]:list(i.keys())[0]})
                else:
                    print(f'[warn] 未收录的组合: {index} 组合{group_list}')
                    continue
        #此时单个的排完了，先排次要的
        # compose_law = sorted(compose_law.items(),key = lambda x:100-x[1].get("law",-1) if x[1].get("law",-1)<=0 else x[1].get("law",-1))
        # compose_law = sorted(compose_law,key = lambda x:100  if x[1].get("law",-1) != 0 else x[1].get("law",-1))
        compose_law_sroted = sorted(compose_law.items(),key = lambda x:100 if x[1].get('priority',-1) == -1 else x[1].get('priority',-1))
        for i in compose_law_sroted:
            group ,args = i.items()
            hang = args.get("hang",[None])#None就是index最小的一个可用行,这是一个列表存放的数字就是可接受的位置，but 类型str = only, int = 可接受   
            priority = args.get("priority",-1)
            # law = args.get("law",0)
            hang.sort(key = lambda x : x+100 if type(x) == int else int(x)) if None not in hang else None
            """
            ->
                yes ->
                    有剩余吗
                    有 ->
                        再看位置,从小看 -执行一次,先排str后int
                            str -> 有位置就放
                            int -> 放
                    无 -> return 0
                no ->
                    有剩余吗
                    无了 ->
                        return 0
                    有 ->
                        下一页
            """
            for i in range(sorted(list(self.page.keys()))[-1]+1):
                if i not in list(self.page.keys()):
                    _creat_page(i)                              #要显示的文字从index到名字的映射
                    self.page[i][int(hang[0])][:len(group)] = [index_to_word[idx] for idx in group]
                    break
                #兼容小行
                current_page = self.page[i]
                #处理优先行 str
                for index in hang :
                    flag , loca = _count_0(line)
                    if flag :
                        self.page[i][int(index)][loca:loca+len(group)] = [index_to_word[idx] for idx in group]
                    break

            else:
                last_page = _add_page()



            



            
        
        
            
                



    def press(self,key):
        k = keyboard.Key
        if key == k.esc:
            return False
        elif key == k.up:
            pass
        elif key == k.down:
            pass
        elif key == k.left:
            pass
        elif key == k.right:
            pass
        elif key == k.enter:
            pass
print(str({'asdf':0}.keys()[0]))
 