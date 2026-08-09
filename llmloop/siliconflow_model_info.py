list_model_poor = [
    "deepseek-ai/DeepSeek-V3.2",
    "deepseek-ai/DeepSeek-V3.1-Terminus",
    "Qwen/Qwen3.5-35B-A3B",
    "Qwen/Qwen3.5-27B",
    "Qwen/Qwen3.5-9B",
    "deepseek-ai/DeepSeek-R1",
    "deepseek-ai/DeepSeek-V3",
    "Qwen/Qwen3-VL-32B-Instruct",
    "Qwen/Qwen3-VL-32B-Thinking",
    "Qwen/Qwen3-VL-8B-Instruct",
    "Qwen/Qwen3-VL-8B-Thinking",
    "Qwen/Qwen3-VL-30B-A3B-Instruct",
    "Qwen/Qwen3-VL-30B-A3B-Thinking",
    "Qwen/Qwen3-Omni-30B-A3B-Instruct",
    "Qwen/Qwen3-Omni-30B-A3B-Thinking",
    "Qwen/Qwen3-Omni-30B-A3B-Captioner",
    "inclusionAI/Ling-flash-2.0",
    "inclusionAI/Ling-mini-2.0",
    "Qwen/Qwen-Image-Edit-2509",
    "Qwen/Qwen-Image-Edit",
    "Qwen/Qwen-Image",
    "ByteDance-Seed/Seed-OSS-36B-Instruct",
    "Wan-AI/Wan2.2-I2V-A14B",
    "Wan-AI/Wan2.2-T2V-A14B",
    "zai-org/GLM-4.5V",
    "zai-org/GLM-4.5-Air",
    "Qwen/Qwen3-Coder-30B-A3B-Instruct",
    "Qwen/Qwen3-30B-A3B-Instruct-2507",
    "tencent/Hunyuan-A13B-Instruct",
    "Qwen/Qwen3-32B",
    "Qwen/Qwen3-14B",
    "Qwen/Qwen3-Reranker-8B",
    "Qwen/Qwen3-Embedding-8B",
    "Qwen/Qwen3-Reranker-4B",
    "Qwen/Qwen3-Embedding-4B",
    "Qwen/Qwen3-Reranker-0.6B",
    "Qwen/Qwen3-Embedding-0.6B",
    "THUDM/GLM-4-32B-0414",
    "fnlp/MOSS-TTSD-v0.5",
    "FunAudioLLM/CosyVoice2-0.5B",
    "Qwen/Qwen2.5-72B-Instruct",
    "Qwen/Qwen2.5-32B-Instruct",
    "Qwen/Qwen2.5-7B-Instruct",
    "Pro/BAAI/bge-m3",
    "Pro/BAAI/bge-reranker-v2-m3",
    "Pro/Qwen/Qwen2.5-7B-Instruct",
    "LoRA/Qwen/Qwen2.5-7B-Instruct",
    "LoRA/Qwen/Qwen2.5-14B-Instruct",
    "LoRA/Qwen/Qwen2.5-32B-Instruct",
    "LoRA/Qwen/Qwen2.5-72B-Instruct"]

# import json
# with open(f'O:\project\pjct-cf-prompt\llmloop\models.json','r',encoding="utf-8") as f:
#     aval_model = list(json.load(f))

# collect_tags = [i['tags'] for i in aval_model]
# c = {j for i in collect_tags for j in i}

# B_tag = {x for x in c if x[-1] in "BbT" or (x[-1] == "M" and x != "1M")}

# # 上下文大小：K/k 结尾，或特殊的 1M
# long_tag = {x for x in c if x[-1] in "Kk" or x == "1M"}

# normal_tag = (c - B_tag) - long_tag
# print(B_tag,long_tag,normal_tag)
# class Tag():
#     def __init__(self):
#         self.poor = list_model_poor
#         self.B = B_tag
#         self.long = long_tag
#         self.normal = normal_tag

