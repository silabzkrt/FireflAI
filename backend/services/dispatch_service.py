"""
FireflAI - Tactical Dispatch & Emergency Planning Service

Generates structured TAMP (Türkiye Afet Müdahale Planı) emergency response directives using
a fine-tuned Qwen-2.5-3B-Instruct model (PEFT/LoRA). Computes spatial proximities to regional
water sources and settlements via Haversine distance calculations.
"""

import json
import math
import traceback
from pathlib import Path
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel

class DispatchService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DispatchService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, base_model_name: str = "Qwen/Qwen2.5-3B-Instruct"):
        if getattr(self, "_initialized", False):
            return

        base_dir = Path(__file__).resolve().parent.parent
        self.lora_path = base_dir / "models" / "dispatch_model"
        if not self.lora_path.exists() and (base_dir / "models" / "dispatch_model").exists():
            self.lora_path = base_dir / "models" / "dispatch_model"

        self.base_model_name = base_model_name
        self.model = None
        self.tokenizer = None

        self.water_list, self.settlement_list = self._load_gis_data(base_dir)
        self._load_lora_model()
        self._initialized = True

    def _load_gis_data(self, base_dir: Path):
        data_dir = base_dir / "data"
        water_file = data_dir / "su_kaynaklari.json"
        settlement_file = data_dir / "yerlesim_ve_tesisler.json"

        water_list, settlement_list = [], []
        if water_file.exists():
            with open(water_file, "r", encoding="utf-8") as f:
                water_list = json.load(f)
        if settlement_file.exists():
            with open(settlement_file, "r", encoding="utf-8") as f:
                settlement_list = json.load(f)
        return water_list, settlement_list

    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        R = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    def find_nearest_gis(self, lat: float, lon: float, top_k: int = 3):
        sorted_water = sorted(
            self.water_list,
            key=lambda x: self._haversine_distance(lat, lon, x.get("koordinat_enlem", 0), x.get("koordinat_boylam", 0))
        )[:top_k]

        sorted_settlements = sorted(
            self.settlement_list,
            key=lambda x: self._haversine_distance(lat, lon, x.get("koordinat_enlem", 0), x.get("koordinat_boylam", 0))
        )[:top_k]

        return sorted_water, sorted_settlements

    def _load_lora_model(self):
        try:
            metadata_file = self.lora_path / "firefl_metadata.json"
            if metadata_file.exists():
                with open(metadata_file, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                    self.base_model_name = meta.get("base_model", self.base_model_name)

            self.tokenizer = AutoTokenizer.from_pretrained(self.base_model_name, trust_remote_code=True)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            device = "cuda" if torch.cuda.is_available() else "cpu"
            torch_dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32

            try:
                bnb_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_compute_dtype=torch.float16,
                )
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.base_model_name,
                    quantization_config=bnb_config,
                    device_map="auto",
                    trust_remote_code=True
                )
            except Exception:
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.base_model_name,
                    torch_dtype=torch_dtype,
                    device_map="auto",
                    trust_remote_code=True
                )

            if self.lora_path.exists() and (self.lora_path / "adapter_config.json").exists():
                self.model = PeftModel.from_pretrained(self.model, str(self.lora_path))

            self.model.eval()
        except Exception:
            self.model = None

    def calculate_spread_polygon(self, lat: float, lon: float, wind_speed: float, wind_dir: float, hours: int) -> dict:
        rad = math.radians(wind_dir)
        distance_km = (wind_speed * 0.1) * hours
        dlat = (distance_km / 111.0) * math.cos(rad)
        dlon = (distance_km / (111.0 * math.cos(math.radians(lat)))) * math.sin(rad)

        perp_rad = rad + math.pi / 2
        lateral_km = distance_km * 0.4
        plat = (lateral_km / 111.0) * math.cos(perp_rad)
        plon = (lateral_km / (111.0 * math.cos(math.radians(lat)))) * math.sin(perp_rad)

        coordinates = [[
            [round(lon, 6), round(lat, 6)],
            [round(lon + dlon * 0.5 + plon, 6), round(lat + dlat * 0.5 + plat, 6)],
            [round(lon + dlon, 6), round(lat + dlat, 6)],
            [round(lon + dlon * 0.5 - plon, 6), round(lat + dlat * 0.5 - plat, 6)],
            [round(lon, 6), round(lat, 6)]
        ]]

        return {
            "type": "Polygon",
            "coordinates": coordinates
        }

    def generate_plan(self, lat: float, lon: float, wind_speed: float, caption: str, forces: str) -> tuple:
        nearest_water, nearest_settlements = self.find_nearest_gis(lat, lon)

        if not self.model or not self.tokenizer:
            return "LoRA Modeli aktif değil. Standart sevk protokolü devrede.", nearest_water, nearest_settlements

        try:
            water_text = ", ".join([f"{w['isim']} {w['gps_format']}" for w in nearest_water]) if nearest_water else "Yerel su kaynakları"
            settlement_text = ", ".join([f"{s['isim']} {s['gps_format']} ({s.get('nufus_yatak_kapasitesi', '')})" for s in nearest_settlements]) if nearest_settlements else "Yerleşim çeperi"

            instruction = (
                f"### ORMAN YANGINI ACİL SEVKİYAT VE KOORDİNAT KOMUT TALİMATI\n"
                f"**[İHBAR / GÖRSEL CAPTION]:** {caption}\n\n"
                f"**[GIS VE METEOROLOJİK TELEMETRİ VERİLERİ]:**\n"
                f"- **Konum & Merkez Koordinat:** [{lat}°N, {lon}°E]\n"
                f"- **Hava Durumu:** Rüzgar: {wind_speed} km/s\n"
                f"- **Tehdit Altındaki Yerleşimler & Tesisler:** {settlement_text}\n"
                f"- **Yakın Su Kaynakları:** {water_text}\n"
                f"- **Mevcut / Sevk Edilebilir Güçler:** {forces}\n\n"
                f"TAMP ilkelerine göre KESİNLİKLE GPS KOORDİNATLARI üzerinden taktiksel sevk emrini yaz."
            )

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
                eos_ids = [self.tokenizer.eos_token_id]
                im_end = self.tokenizer.convert_tokens_to_ids("<|im_end|>")
                if im_end is not None:
                    eos_ids.append(im_end)

                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=650,
                    do_sample=False,
                    repetition_penalty=1.05,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=eos_ids
                )

            new_tokens = outputs[0][inputs.input_ids.shape[-1]:]
            raw_order = self.tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
            return raw_order, nearest_water, nearest_settlements

        except Exception as e:
            traceback.print_exc()
            return f"Taktik plan metni oluşturulamadı: {str(e)}", nearest_water, nearest_settlements