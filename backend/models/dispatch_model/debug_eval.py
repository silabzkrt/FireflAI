import torch
import json
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import importlib

ev = importlib.import_module("4_evaluate_dispatcher")
scen = ev.BENCHMARK_SCENARIOS[0]

print("Loading model...")
m = AutoModelForCausalLM.from_pretrained('Qwen/Qwen2.5-3B-Instruct', torch_dtype=torch.float16, device_map='auto')
m = PeftModel.from_pretrained(m, 'models/firefl_dispatcher_lora')
t = AutoTokenizer.from_pretrained('Qwen/Qwen2.5-3B-Instruct')

user_content = scen['instruction'] + '\n\n### MEVZUAT / OPTİMİZASYON BAĞLAMI:\n' + scen['context']
prompt = (
    f"<|im_start|>system\n"
    f"Sen Türkiye Afet Müdahale Planı (TAMP) ve OGM yönergelerine hakim, tüm emirlerini KESİN GPS KOORDİNATLARI ([Enlem°N, Boylam°E]), hedef savunma sektörleri, dozer hendek/yangın şeridi koordinat hatları ve su alım/boşaltım noktaları üzerinden operasyonel askeri emir formatında veren taktiksel bir komuta merkezisin.<|im_end|>\n"
    f"<|im_start|>user\n"
    f"{user_content}<|im_end|>\n"
    f"<|im_start|>assistant\n"
)

inputs = t(prompt, return_tensors='pt').to(m.device)
print("input_ids shape:", inputs.input_ids.shape)
out = m.generate(**inputs, max_new_tokens=50, do_sample=False)
print("out shape:", out.shape)
new_tokens = out[0][inputs.input_ids.shape[-1]:]
print("NEW TOKENS:", new_tokens)
print("NEW TOKENS DECODED:\n", repr(t.decode(new_tokens, skip_special_tokens=False)))
