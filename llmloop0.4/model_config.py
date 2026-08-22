import copy
class Model_Config :
    def __init__(self,ori_setting) -> None:
        # 获得默认设定
        # with open("O:/project/pjct-cf-prompt/llmloop0.2/data/models_config.json",'r',encoding="utf-8") as f :
        #     ori_setting = dict(json.load(f))
        self.user_setting= copy.deepcopy(ori_setting)
        self.ori_setting = ori_setting
    
    # def __call__(self,model_name:str):      #默认返回用户设置
    #     return self.user_setting.get(model_name,(1,1,1,1))
    
    def change_setting(self,args:list,model_name:str):
        def legal_test(new_args:list,model_name:str) -> bool:         #检查是否设置合法
            # test_result = map(lambda x : x[1]!= 0 and x[0] == 1 or x[0] == 0, ((usr,syt) for usr,syt in zip(new_args,self.ori_setting.get(model_name,(1,1,1,1)))))
            test_result = (syt != 0 and usr == 1 or usr == 0 for usr,syt in zip(new_args,self.ori_setting.get(model_name,[1,1,1,1])))
            if False in test_result:
                print("illegal setting")
                return 0
            print("legal setting")
            return 1

        if legal_test(args,model_name):
            self.user_setting[model_name] = args
            status = "97m ON" if "Thinking" in model_name or args[0] == 1 else "90m OFF"
            print(f"\033[0;7;97m思考\033[0;1;{status}\033[0m")
        else:
            print("设置失败")