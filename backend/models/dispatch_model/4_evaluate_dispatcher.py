#!/usr/bin/env python3
"""
Stage 4: Interactive Dispatcher & Benchmark Evaluation CLI with Complete Turkey GIS Database Integration
Loads the fine-tuned LoRA conceptual emergency dispatcher model (`models/firefl_dispatcher_lora`)
and evaluates tactical fire dispatch scenarios in Turkish/English.
Supports:
  1) `--benchmark`: Standard benchmark scenarios with coordinates.
  2) `--interactive`: Live interactive console featuring automatic GIS database lookup by province/district/coordinates
     using the Turkey-wide `su_kaynaklari.json` (113 resources) and `yerlesim_ve_tesisler.json` (84 settlements/facilities).
"""

import os
import sys
import json
import argparse
import math
import torch
from pathlib import Path

try:
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    from peft import PeftModel
except ImportError:
    print("[ERROR] Missing transformers or peft. Please install via requirements.txt")
    sys.exit(1)

def load_turkey_gis_database():
    base_dir = Path(__file__).resolve().parent
    data_dir = base_dir / "data"
    water_file = data_dir / "su_kaynaklari.json"
    settlement_file = data_dir / "yerlesim_ve_tesisler.json"

    water_list = []
    settlement_list = []

    if water_file.exists():
        with open(water_file, "r", encoding="utf-8") as f:
            water_list = json.load(f)
    if settlement_file.exists():
        with open(settlement_file, "r", encoding="utf-8") as f:
            settlement_list = json.load(f)

    return water_list, settlement_list

def search_gis_by_province(il_query: str, water_list: list, settlement_list: list):
    il_query = il_query.strip().lower()
    matched_water = [w for w in water_list if il_query in w.get("il", "").lower() or il_query in w.get("ilce", "").lower() or il_query in w.get("bolge", "").lower()]
    matched_settlements = [s for s in settlement_list if il_query in s.get("il", "").lower() or il_query in s.get("ilce", "").lower()]
    return matched_water, matched_settlements

def format_gis_context(matched_water: list, matched_settlements: list) -> str:
    lines = []
    lines.append("**[TÜRKİYE CBS TAKTİK KOORDİNAT VERİ TABANI]**")
    lines.append("TEHDİT ALTINDAKİ YERLEŞİMLER, OTELLER VE KRİTİK ALTYAPI (KOORDİNATLI):")
    if matched_settlements:
        for s in matched_settlements[:6]:
            lines.append(f"  - [{s.get('id')}] {s.get('isim')} ({s.get('il')}/{s.get('ilce')}) | Koordinat: {s.get('gps_format')} | Risk: {s.get('risk_seviyesi')} | Öncelik: {s.get('savunma_onceligi')}")
    else:
        lines.append("  - Bölgede kayıtlı spesifik tesis bulunamadı, standart koordinat hattı uygulanacak.")

    lines.append("\nYAKIN STRATEJİK SU KAYNAKLARI VE İKMAL NOKTALARI (KOORDİNATLI):")
    if matched_water:
        for w in matched_water[:6]:
            lines.append(f"  - [{w.get('id')}] {w.get('isim')} ({w.get('il')}/{w.get('ilce')}) | Koordinat: {w.get('gps_format')} | Tip: {w.get('tip')} | Uygun Araçlar: {', '.join(w.get('uygun_araclar', []))}")
    else:
        lines.append("  - Bölgede kayıtlı spesifik su kaynağı bulunamadı, en yakın göl/deniz ikmalı esas alınacak.")
    return "\n".join(lines)

BENCHMARK_SCENARIOS = [
    {
        "title": "ANTALYA / MANAVGAT - OYMAPINAR BARAJI HATTINDA TAÇ YANGINI",
        "instruction": (
            "### ORMAN YANGINI ACİL SEVKİYAT VE KOORDİNAT KOMUT TALİMATI\n"
            "**[İHBAR / GÖRSEL CAPTION]:** Manavgat Oymapınar Barajı üst yamaçlarında kızılçam ormanında kuvvetli poyrazla birlikte alevler hızla vadi yukarısına tırmanıyor. Yoğun duman Karavca köyü istikametine yayılmış durumda.\n\n"
            "**[GIS VE METEOROLOJİK TELEMETRİ VERİLERİ]:**\n"
            "- **Konum & Merkez Koordinat:** Antalya / Manavgat [36.884°N, 31.465°E]\n"
            "- **Yangın Alanı & Cephe:** 45 Hektar (aktif taç yangını) - Kızılçam ormanı, sarp vadi yamaçları\n"
            "- **Hava Durumu:** Sıcaklık: 39°C | Bağıl Nem: %14 | Rüzgar: Poyraz (KD) - 42 km/s (Acil Durum - Aşırı rüzgar)\n"
            "- **Tehdit Altındaki Yerleşimler & Nüfus:** Karavca Köyü [36.887°N, 31.470°E] (850 Nüfus), Oymapınar Köyü [36.895°N, 31.485°E] (1400 Nüfus), Trafo Merkezi [36.905°N, 31.530°E]\n"
            "- **Altyapı (Karayolu & Demiryolu):** D400 Karayolu, Oymapınar Servis Yolu [36.889°N, 31.475°E]\n"
            "- **Yakın Su Kaynakları:** Oymapınar Baraj Gölü 3. İskele [36.881°N, 31.460°E], YH-14 Yangın Havuzu [36.885°N, 31.468°E]\n"
            "- **Mevcut / Sevk Edilebilir Güçler:** 3 Amfibik Uçak, 6 Helikopter, 20 Arazöz, 4 Dozer, 85 Personel\n\n"
            "TAMP ve resmi optimizasyon (ILP) ilkelerine göre;\n"
            "BİLGİLERİ KESİNLİKLE GPS KOORDİNATLARI ([Enlem°N, Boylam°E]) ÜZERİNDEN VEREREK:\n"
            "1) Hangi koordinata İTFAİYE / ARAZÖZ sevk edileceğini ve hangi sektörün savunulacağını (ör. [36.895°N, 31.485°E] Oymapınar Köyü savunma hattı),\n"
            "2) Hangi koordinatlar arasına DOZER ile HENDEK / YANGIN ŞERİDİ açılacağını (ör. [36.905°N, 31.530°E] ile orman sınırı arasına 30 m şerit),\n"
            "3) Hangi koordinattan SU ALIMI yapılıp hangi koordinata SU SEVKİYATI / İKMALİ gerçekleştirileceğini (ör. [36.881°N, 31.460°E] baraj alımı -> [36.887°N, 31.470°E] Karavca cephesine ikmal),\n"
            "4) Tahliye, karayolu ve altyapı yönetim koordinatlarını,\n"
            "5) Matematiksel optimizasyon ve TAMP gerekçesini açıkça emir olarak yaz."
        ),
        "context": "MEVZUAT VE OPTİMİZASYON BAĞLAMI:\n1. TAMP / OGM Doktrini: TAMP Orman Yangınları Afet Grubu: 40 km/s üzeri rüzgarlarda ve yerleşim tehdidi altında önceliği can emniyetine ve önleyici tahliye şeridine ver.\n2. Kaynak Optimizasyon Modeli: ILP (Integer Linear Programming) ve mekansal optimizasyon ilkelerine göre ilk 30 dakikada yapılan hava taarruzu alev cephesi genişlemesini kırar."
    },
    {
        "title": "MUĞLA / MARMARİS - İÇMELER ELEKTRİK TRAFO MERKEZİ VE OTELLER TEHDİDİ",
        "instruction": (
            "### ORMAN YANGINI ACİL SEVKİYAT VE KOORDİNAT KOMUT TALİMATI\n"
            "**[İHBAR / GÖRSEL CAPTION]:** İçmeler sırtlarında lodos etkisiyle başlayan örtü yangını ağaç taçlarına sıçradı. Oteller bölgesine doğru alev parçacıkları (spotting) düşüyor.\n\n"
            "**[GIS VE METEOROLOJİK TELEMETRİ VERİLERİ]:**\n"
            "- **Konum & Merkez Koordinat:** Muğla / Marmaris [36.802°N, 28.231°E]\n"
            "- **Yangın Alanı & Cephe:** 28 Hektar - Sık kızılçam ve maki örtüsü\n"
            "- **Hava Durumu:** Sıcaklık: 37°C | Bağıl Nem: %18 | Rüzgar: Lodos (GB) - 34 km/s (Yüksek Risk)\n"
            "- **Tehdit Altındaki Yerleşimler & Nüfus:** İçmeler Mahallesi [36.800°N, 28.234°E] (6500 Nüfus), Turunç Mahallesi [36.775°N, 28.248°E] (2100 Nüfus), 100 kW Elektrik Trafo Merkezi [36.802°N, 28.230°E], Grand Yazıcı Otel [36.828°N, 28.242°E]\n"
            "- **Altyapı (Karayolu & Demiryolu):** Marmaris-Turunç Karayolu [36.789°N, 28.239°E], D400 Muğla-Marmaris arter hattı\n"
            "- **Yakın Su Kaynakları:** Marmaris Körfezi İçmeler Koyu [36.799°N, 28.238°E], YH-08 Turunç Yangın Havuzu [36.772°N, 28.245°E]\n"
            "- **Mevcut / Sevk Edilebilir Güçler:** 2 Amfibik Uçak, 4 Helikopter, 12 Arazöz, 2 Dozer, 45 Personel\n\n"
            "TAMP ve resmi optimizasyon (ILP) ilkelerine göre;\n"
            "BİLGİLERİ KESİNLİKLE GPS KOORDİNATLARI ([Enlem°N, Boylam°E]) ÜZERİNDEN VEREREK:\n"
            "1) Hangi koordinata İTFAİYE / ARAZÖZ sevk edileceğini ve hangi sektörün savunulacağını,\n"
            "2) Hangi koordinatlar arasına DOZER ile HENDEK / YANGIN ŞERİDİ açılacağını,\n"
            "3) Hangi koordinattan SU ALIMI yapılıp hangi koordinata SU SEVKİYATI / İKMALİ gerçeleştirileceğini,\n"
            "4) Tahliye, karayolu ve altyapı yönetim koordinatlarını,\n"
            "5) Matematiksel optimizasyon ve TAMP gerekçesini açıkça emir olarak yaz."
        ),
        "context": "MEVZUAT VE OPTİMİZASYON BAĞLAMI:\n1. TAMP / OGM Doktrini: OGM Yangınla Mücadele Yönergesi: Kritik altyapı (enerji, trafo, oteller hattı) savunmasında arazöz su perdesi ve dozer şerit açımı önceliklidir.\n2. Kaynak Optimizasyon Modeli: Dinamik kaynak rotalama periyotları minimizasyonu ile denizden su alan uçakların sorti süresi kısaltılır."
    }
]

def load_dispatcher_model(lora_dir: str):
    print("Loading tokenizer and base model...")
    metadata_file = Path(lora_dir) / "firefl_metadata.json"
    base_model_name = "Qwen/Qwen2.5-3B-Instruct"
    
    if metadata_file.exists():
        with open(metadata_file, "r", encoding="utf-8") as f:
            meta = json.load(f)
            base_model_name = meta.get("base_model", base_model_name)

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
    )

    tokenizer = AutoTokenizer.from_pretrained(base_model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True
    )

    lora_path = Path(lora_dir)
    if lora_path.exists() and (lora_path / "adapter_config.json").exists():
        print(f"Loading fine-tuned LoRA weights from: {lora_dir}")
        model = PeftModel.from_pretrained(model, lora_dir)
    else:
        print(f"[WARN] No LoRA adapter found in {lora_dir}. Running with Base Model ({base_model_name}).")

    model.eval()
    return model, tokenizer

def generate_dispatch_order(model, tokenizer, instruction: str, context: str = "") -> str:
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

    inputs = tokenizer.apply_chat_template(
        messages,
        tokenize=True,
        add_generation_prompt=True,
        return_tensors="pt",
        return_dict=True
    ).to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=650,
            do_sample=False,
            repetition_penalty=1.05,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=[tokenizer.eos_token_id, tokenizer.convert_tokens_to_ids("<|im_end|>")] if tokenizer.convert_tokens_to_ids("<|im_end|>") is not None else tokenizer.eos_token_id,
        )

    new_tokens = outputs[0][inputs.input_ids.shape[-1]:]
    assistant_reply = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
    return assistant_reply

def run_benchmark(model, tokenizer):
    print("\n" + "=" * 70)
    print("  FIREFL-AI: AUTOMATED BENCHMARK EVALUATION WITH GIS TELEMETRY")
    print("=" * 70)

    for i, scen in enumerate(BENCHMARK_SCENARIOS, 1):
        print(f"\n[BENCHMARK SCENARIO #{i}]: {scen['title']}")
        print("--- GENERATED DISPATCH ORDER ---")
        reply = generate_dispatch_order(model, tokenizer, scen["instruction"], scen["context"])
        print(reply)
        print("-" * 70)

def run_interactive(model, tokenizer):
    print("\n" + "=" * 80)
    print("  FIREFL-AI: İNTERAKTİF TAKTİKSEL SEVKİYAT VE KOMUTA KONSOLU (CBS DESTEKLİ)")
    print("  Türkiye geneli 113+ su kaynağı ve 84+ yerleşim/tesis veritabanına doğrudan bağlı.")
    print("=" * 80)

    water_list, settlement_list = load_turkey_gis_database()
    print(f"[CBS VERİ TABANI HAZIR] {len(water_list)} su kaynağı ve {len(settlement_list)} kritik tesis aktif.")

    while True:
        try:
            print("\n[Giriş Modu Seçin]:")
            print("  1) İl / Bölge Seçmeli CBS Senaryo Sihirbazı (Ör: Antalya, Muğla, İzmir, Mersin vb.)")
            print("  2) Manuel Adım Adım Senaryo Girişi")
            print("  3) Serbest Metin / Hazır İhbar Yapıştır")
            print("  q) Çıkış (Exit)")
            mode = input("\n[Seçiminiz (1/2/3/q)]> ").strip().lower()
            if mode in ["q", "exit", "quit"]:
                break

            if mode == "1":
                print("\n--- İL / BÖLGE SEÇMELİ CBS SENARYO SİHİRBAZI ---")
                print("Mevcut illerden birini girin (Ör: Antalya, Muğla, İzmir, Çanakkale, Balıkesir, Mersin, Adana, Hatay, Bolu vb.)")
                il_query = input("İl / İlçe veya Bölge Adı> ").strip()
                if not il_query:
                    il_query = "Antalya"

                matched_water, matched_settlements = search_gis_by_province(il_query, water_list, settlement_list)
                print(f"\n[{il_query.upper()} CBS SORGUSU]: {len(matched_settlements)} tesis/yerleşim ve {len(matched_water)} su kaynağı bulundu.")

                caption = input("1. İhbar / Görsel Durum (ör. Ormanlık alanda rüzgar etkisiyle hızla yayılan tepe yangını): ").strip()
                if not caption:
                    caption = f"{il_query} bölgesinde kuvvetli rüzgar etkisiyle ormanlık alanda hızla yayılan taç yangını ihbarı alındı."

                weather = input("2. Hava Durumu & Rüzgar (ör. Sıcaklık: 39°C | Nem: %14 | Rüzgar: Poyraz - 40 km/s): ").strip()
                if not weather:
                    weather = "Sıcaklık: 39°C | Bağıl Nem: %14 | Rüzgar: Poyraz (KD) - 40 km/s (Acil Durum - Yüksek Risk)"

                forces = input("3. Mevcut Güçler (ör. 3 Amfibik Uçak, 6 Helikopter, 20 Arazöz, 4 Dozer, 85 Personel): ").strip()
                if not forces:
                    forces = "3 Amfibik Uçak, 6 Helikopter, 20 Arazöz, 4 Dozer, 85 Personel"

                gis_text = format_gis_context(matched_water, matched_settlements)

                user_input = f"""### ORMAN YANGINI ACİL SEVKİYAT VE KOORDİNAT KOMUT TALİMATI
**[İHBAR / GÖRSEL CAPTION]:** {caption}

**[GIS VE METEOROLOJİK TELEMETRİ VERİLERİ]:**
- **Bölge:** {il_query.upper()} ORMAN SEKTÖRÜ
- **Hava Durumu:** {weather}
- **Mevcut / Sevk Edilebilir Güçler:** {forces}

{gis_text}

TAMP ve resmi optimizasyon (ILP) ilkelerine göre;
BİLGİLERİ KESİNLİKLE GPS KOORDİNATLARI ([Enlem°N, Boylam°E]) ÜZERİNDEN VEREREK:
1) Hangi koordinata İTFAİYE / ARAZÖZ sevk edileceğini ve hangi yerleşim/tesisin savunulacağını,
2) Hangi koordinatlar arasına DOZER ile HENDEK / YANGIN ŞERİDİ açılacağını,
3) Hangi koordinattaki su kaynağından SU ALIMI yapılıp hangi koordinata SU SEVKİYATI / İKMALİ gerçeleştirileceğini,
4) Tahliye, karayolu ve altyapı yönetim koordinatlarını,
5) Matematiksel optimizasyon ve TAMP gerekçesini açıkça emir olarak yaz."""

            elif mode == "2":
                print("\n--- MANUEL ADIM ADIM SENARYO GİRİŞİ ---")
                caption = input("1. İhbar / Görsel Durum: ").strip()
                if not caption:
                    caption = "Ormanlık alanda rüzgar etkisiyle hızla yayılan örtü ve taç yangını ihbarı alındı."
                coord = input("2. Bölge & Merkez Koordinat: ").strip()
                if not coord:
                    coord = "Antalya / Manavgat [36.884°N, 31.465°E]"
                threats = input("3. Tehdit Altındaki Yerleşimler & Tesisler: ").strip()
                if not threats:
                    threats = "Karavca Köyü [36.887°N, 31.470°E], Oymapınar Barajı Trafo Merkezi [36.905°N, 31.530°E]"
                weather = input("4. Hava Durumu & Rüzgar: ").strip()
                if not weather:
                    weather = "Sıcaklık: 39°C | Bağıl Nem: %14 | Rüzgar: Poyraz - 40 km/s"
                water = input("5. Yakın Su Kaynakları: ").strip()
                if not water:
                    water = "Oymapınar Barajı 3. İskele [36.881°N, 31.460°E], YH-14 Yangın Havuzu [36.885°N, 31.468°E]"
                forces = input("6. Mevcut Güçler: ").strip()
                if not forces:
                    forces = "3 Amfibik Uçak, 6 Helikopter, 20 Arazöz, 4 Dozer, 80 Personel"

                user_input = f"""### ORMAN YANGINI ACİL SEVKİYAT VE KOORDİNAT KOMUT TALİMATI
**[İHBAR / GÖRSEL CAPTION]:** {caption}

**[GIS VE METEOROLOJİK TELEMETRİ VERİLERİ]:**
- **Konum & Merkez Koordinat:** {coord}
- **Hava Durumu:** {weather}
- **Tehdit Altındaki Yerleşimler & Nüfus:** {threats}
- **Yakın Su Kaynakları:** {water}
- **Mevcut / Sevk Edilebilir Güçler:** {forces}

TAMP ve resmi optimizasyon (ILP) ilkelerine göre;
BİLGİLERİ KESİNLİKLE GPS KOORDİNATLARI ([Enlem°N, Boylam°E]) ÜZERİNDEN VEREREK:
1) Hangi koordinata İTFAİYE / ARAZÖZ sevk edileceğini ve hangi sektörün savunulacağını,
2) Hangi koordinatlar arasına DOZER ile HENDEK / YANGIN ŞERİDİ açılacağını,
3) Hangi koordinattan SU ALIMI yapılıp hangi koordinata SU SEVKİYATI / İKMALİ gerçeleştirileceğini,
4) Tahliye, karayolu ve altyapı yönetim koordinatlarını,
5) Matematiksel optimizasyon ve TAMP gerekçesini açıkça emir olarak yaz."""

            else:
                user_input = input("\n[Senaryo Metnini Girin]> ").strip()
                if not user_input:
                    continue

            print("\n" + "-" * 80)
            print("Taktiksel Sevk Planı ve Koordinat Hesaplaması Yapılıyor...")
            print("-" * 80)
            reply = generate_dispatch_order(model, tokenizer, user_input)
            print("\n--- FIREFL-AI KOORDİNAT BAZLI SEVKİYAT VE KOMUTA EMİR METNİ ---")
            print(reply)
            print("=" * 80)
        except (KeyboardInterrupt, EOFError):
            break

def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True)
    parser = argparse.ArgumentParser(description="FireFl-AI Dispatcher Evaluation CLI with Turkey GIS Database")
    parser.add_argument("--lora_dir", type=str, default="models/firefl_dispatcher_lora", help="Path to LoRA model")
    parser.add_argument("--interactive", action="store_true", help="Launch interactive console")
    parser.add_argument("--benchmark", action="store_true", help="Run benchmark scenarios")
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent
    lora_path = base_dir / args.lora_dir

    model, tokenizer = load_dispatcher_model(str(lora_path))

    if args.interactive:
        run_interactive(model, tokenizer)
    else:
        run_benchmark(model, tokenizer)

if __name__ == "__main__":
    main()
