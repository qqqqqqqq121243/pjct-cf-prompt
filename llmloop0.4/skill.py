import json
from pathlib import Path
import os

import yaml


skill_path = Path(__file__).parent / '.skill'
def initital():
    os.makedirs(skill_path,exist_ok=True)


class Skill:
    def __init__(self) -> None:
        if not os.path.exists(skill_path) :
            initital()
        self.skill_path = skill_path
        self.skills = {}

        self.available_skill = {}#self.skills的子集

    def on(self):
        self._load_all()

    def off(self):
        self.skills = {}
        self.available_skill = {}

        
    def _parse_skill(self,md_txt:str):
        if md_txt.startswith("---"):
            _,front,body = md_txt.split("---",2)
            meta = yaml.safe_load(front) or {}
            return meta,body.strip()
        return {},md_txt

    def _load_one(self,d:Path):
        md = d / "SKILL.md"
        if not md.exists() :
            return None
        meta , body = self._parse_skill(md.read_text(encoding = 'utf-8'))
        name = meta.get('name') or d.name

        cn_body = None
        cn = d / "SKILL.cn.md"
        if cn.exists():
            _, cn_body = self._parse_skill(cn.read_text(encoding="utf-8"))


        meta_info = {}
        my = d / "meta.yaml"
        if my.exists():
            meta_info = yaml.safe_load(my.read_text(encoding = 'utf-8')) or {}

        references = {}
        ref_dir = d / "references"
        if ref_dir.is_dir():
            for f in ref_dir.iterdir():
                if f.is_file():
                    references[f.name] = f.read_text(encoding = "utf-8")

        return {
            "name": name,
            "description": meta.get("description", ""),
            "body": body,
            "cn_body": cn_body,
            "meta": meta_info,
            "refs": references
        }
    def _load_all(self):
        self.skills = {}
        for d in self.skill_path.iterdir():
            if d.is_dir():
                s = self._load_one(d)
                if s:
                    self.skills[s['name']] = s

    # 列表展示（中文优先）给终端看的
    def list_skills(self):
        for name, s in self.skills.items():
            display = s["meta"].get("display-name-zh") or name
            summary = s["meta"].get("summary-cn") or s["description"]
            print(f"\033[1m{name}\033[0m - {display}\n\033[2m{summary}\033[0m")


    #一次性返回所有提示词
    def all_prompt(self,name ,use_cn = True):
        s = self.skills.get(name)
        if not s:
            return None
        body = s['cn_body'] if s['cn_body'] is not None and use_cn else s['body'] 
        if s['refs']:
            refs_text = '\n\n'.join(f'### {k}\n{v}'for k,v in s['refs'].items())
            body = body +'\n\n'+refs_text
        return body

    #获得激活的提示词 （需要先用load_from_lis
    def part_prmt(self,name ,use_cn = True):
        s = self.available_skill.get(name)
        if not s:
            return None
        body = s['cn_body'] if s['cn_body'] is not None and use_cn else s['body'] 
        if s['refs']:
            refs_text = '\n\n'.join(f'### {k}\n{v}'for k,v in s['refs'].items())
            body = body +'\n\n'+refs_text
        return body

    #在系统提示词上
    def build_skill_intro(self):
        lines = []
        for name, s in self.skills.items():
            lines.append(f"- {name}: {s['description']}")
        return "\n".join(lines)

    #这个是给tools call用的
    def load_from_list(self,skill_list:list):
        self.available_skill = {}
        for s in skill_list:
            if s in self.skills:
                self.available_skill[s] = self.skills[s]


    






    
