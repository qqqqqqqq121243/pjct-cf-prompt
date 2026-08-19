import json
from pathlib import Path
import os

import pyyaml


skill_path = Path(__file__).parent / '.skill'
def initital():
    os.makedirs(skill_path,exist_ok=True)


class Skill:
    def __init__(self) -> None:
        if os.path.exists(skill_path) :
            initital()
        self.skill_path = skill_path
        self.skills = {}
        self._load_all()
        self.available_skill = {}#self.skills的子集
        
    def _parse_skill(self,md_txt:str):
        if md_txt.startswith("---"):
            _,front,body = md_txt.split("---",2)
            meta = yaml.safe_load(front) or {}
            return meta,body.strip()
        return {},md_txt

    def _load_one(self,d:path):
        md = d / "SKILL.md"
        if not md.exists() :
            return None
        meta , body = self._parse_skill(md.read_text(encoding = 'utf-8'))
        name = meta.get('name') or d.name

        cn_body = None
        cn = d / "SKILL.cn.md"
        if cn.exists():
            _, cn_body = self._parse_frontmatter(cn.read_text(encoding="utf-8"))


        meta_info = {}
        my = d / "meta.yaml"
        if my.exists():
            meta_info = yaml.safe_load(md.read_text(encoding = 'utf-8')) or {}

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

    def load_from_list(self,skill_list:list):#这个是给tools call用的
        self.available_skill = {}
        for s in skill_list:
            if s in self.skills:
                self.available_skill[s] = self.skills[s]

    # 列表展示（中文优先）
    def list_skills(self):
        for name, s in self.skills.items():
            display = s["meta"].get("display-name-zh") or name
            summary = s["meta"].get("summary-cn") or s["description"]
            print(f"{name}  |  {display}  |  {summary}")

    def all_propmt(self,name ,use_cn = True):
        s = self.skills.get(name)
        if not s:
            return None
        body = s['cn_body'] if s['cn_body'] is not None and use_cn else s['body'] 
        if s['refs']:
            refs_text = '\n\n'.join(f'### {k}\n{v}'for k,v in s['refs'].items())
            body = body +'\n\n'+refs_text
        return body

    def build_skill_intro(self):
        lines = []
        for name, s in self.skills.items():
            lines.append(f"- {name}: {s['description']}")
        return "\n".join(lines)

    






    
