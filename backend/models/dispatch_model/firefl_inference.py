import torch
from pathlib import Path
import json
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel

class FireFlDispatcher:
    def __init__(self, lora_path: str, base_model_name: str = "Qwen/Qwen2.5-3B-Instruct"):
        """
        Initializes the FireFl-AI Dispatcher Model.
        
        Args:
            lora_path (str): Path to the trained LoRA adapter directory.
            base_model_name (str): The HuggingFace ID of the base model.
        """
        self.lora_path = Path(lora_path)
        self.base_model_name = base_model_name
        self.model = None
        self.tokenizer = None
        self._load_model()

    def _load_model(self):
        print(f"Loading tokenizer and base model ({self.base_model_name})...")
        
        # Check metadata if available to override base_model_name
        metadata_file = self.lora_path / "firefl_metadata.json"
        if metadata_file.exists():
            with open(metadata_file, "r", encoding="utf-8") as f:
                meta = json.load(f)
                self.base_model_name = meta.get("base_model", self.base_model_name)

        # 4-bit Quantization Config (optimized for 8GB VRAM)
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.float16,
        )

        self.tokenizer = AutoTokenizer.from_pretrained(self.base_model_name, trust_remote_code=True)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        self.model = AutoModelForCausalLM.from_pretrained(
            self.base_model_name,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True
        )

        if self.lora_path.exists() and (self.lora_path / "adapter_config.json").exists():
            print(f"Applying LoRA weights from: {self.lora_path}")
            self.model = PeftModel.from_pretrained(self.model, str(self.lora_path))
        else:
            print(f"[WARNING] LoRA weights not found at {self.lora_path}. Running with Base Model only.")

        self.model.eval()
        print("Model loaded successfully!")

    def generate_dispatch_order(self, instruction: str) -> str:
        """
        Generates a tactical dispatch order based on the provided instruction.
        
        Args:
            instruction (str): The scenario details including visual caption, weather, coordinates, and resources.
            
        Returns:
            str: The model's coordinate-based tactical command.
        """
        messages = [
            {
                "role": "system",
                "content": (
                    "Sen Türkiye Afet Müdahale Planı (TAMP) ve OGM yönergelerine hakim, tüm emirlerini "
                    "KESİN GPS KOORDİNATLARI ([Enlem°N, Boylam°E]), hedef savunma sektörleri, dozer hendek/yangın "
                    "şeridi koordinat hatları ve su alım/boşaltım noktaları üzerinden operasyonel askeri emir "
                    "formatında veren taktiksel bir komuta merkezisin. Asla koordinat vermeden genel ifadeler kullanma. "
                    "Şu koordinata itfaiye/arazöz gitsin, şu koordinatlar arasına hendek açılsın, şu koordinattan su sevk edilsin "
                    "şeklinde net emirler yaz."
                )
            },
            {"role": "user", "content": instruction}
        ]

        inputs = self.tokenizer.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=True,
            return_tensors="pt",
            return_dict=True
        ).to(self.model.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=650,
                do_sample=False,
                repetition_penalty=1.05,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=[self.tokenizer.eos_token_id, self.tokenizer.convert_tokens_to_ids("<|im_end|>")] if self.tokenizer.convert_tokens_to_ids("<|im_end|>") is not None else self.tokenizer.eos_token_id,
            )

        new_tokens = outputs[0][inputs.input_ids.shape[-1]:]
        assistant_reply = self.tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
        return assistant_reply

# ==========================================
# EXAMPLE USAGE
# ==========================================
if __name__ == "__main__":
    # Specify the absolute or relative path to your trained LoRA adapter directory
    LORA_MODEL_PATH = "models/firefl_dispatcher_lora" 
    
    # Initialize the dispatcher
    dispatcher = FireFlDispatcher(lora_path=LORA_MODEL_PATH)
    
    # Sample Scenario
    sample_instruction = (
        "### ORMAN YANGINI ACİL SEVKİYAT VE KOORDİNAT KOMUT TALİMATI\n"
        "**[İHBAR / GÖRSEL CAPTION]:** Manavgat Oymapınar Barajı üst yamaçlarında alevler hızla yayılıyor.\n\n"
        "**[GIS VE METEOROLOJİK TELEMETRİ VERİLERİ]:**\n"
        "- **Konum & Merkez Koordinat:** Antalya / Manavgat [36.884°N, 31.465°E]\n"
        "- **Hava Durumu:** Sıcaklık: 39°C | Bağıl Nem: %14 | Rüzgar: Poyraz - 42 km/s\n"
        "- **Tehdit Altındaki Yerleşimler:** Karavca Köyü [36.887°N, 31.470°E]\n"
        "- **Yakın Su Kaynakları:** Oymapınar Baraj Gölü [36.881°N, 31.460°E]\n"
        "- **Mevcut / Sevk Edilebilir Güçler:** 2 Amfibik Uçak, 4 Helikopter, 10 Arazöz, 2 Dozer\n\n"
        "TAMP ilkelerine göre KESİNLİKLE GPS KOORDİNATLARI üzerinden taktiksel sevk emrini yaz."
    )
    
    print("\n--- GENERATING DISPATCH ORDER ---")
    response = dispatcher.generate_dispatch_order(sample_instruction)
    print("\n" + response)
