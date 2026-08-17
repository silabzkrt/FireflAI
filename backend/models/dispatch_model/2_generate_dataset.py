#!/usr/bin/env python3
"""
Stage 2: SFT Training Dataset Generation
Transforms the extracted knowledge from `data/extracted_papers.json` into structured
Supervised Fine-Tuning (SFT) instruction-response pairs (`data/firefl_dispatch_dataset.jsonl`).
Includes Doctrinal QA (TAMP/AFAD/OGM), Mathematical Optimization reasoning, and
rich Turkish/English Tactical Fire Dispatch Scenarios.
"""

import os
import json
import random
from pathlib import Path

# Random seeds for reproducible dataset generation
random.seed(42)

# Turkish regions prone to forest fires for realistic scenario synthesis
# Turkish regions prone to forest fires with rich GIS telemetry, population, infrastructure, and water resources
TURKISH_REGIONS = [
    {
        "city": "Antalya", "district": "Manavgat",
        "terrain": "Kızılçam ormanı, sarp vadi yamaçları",
        "threat": "Oymapınar Barajı lojistik yolu ve 4 köy yerleşimi",
        "coordinates": "36.884°N, 31.465°E",
        "head_coord": "[36.888°N, 31.469°E] - Kuzey-Doğu Kafa Cephesi",
        "arazoz_coord": "[36.891°N, 31.472°E] - Karavca Köyü Güney Savunma Sektörü",
        "trench_line": "[36.890°N, 31.470°E] ile [36.893°N, 31.474°E] koordinatları arasındaki 450 metrelik hat",
        "water_coord": "[36.879°N, 31.455°E] - Oymapınar Baraj Gölü 3. İskele Noktası",
        "resupply_route": "[36.881°N, 31.460°E] (Su Dolum İstasyonu) -> [36.891°N, 31.472°E] (Arazöz İkmal Rota Hattı)",
        "evac_coord": "[36.887°N, 31.475°E] - D400 Karayolu Oymapınar Bağlantı Kavşağı",
        "fire_area": "45 Hektar (aktif taç yangını)",
        "villages": "Karavca Köyü (1.2 km, Nüfus: 850), Oymapınar Köyü (2.4 km, Nüfus: 1400), Güzelyalı (3.8 km, Nüfus: 620)",
        "water_sources": "Oymapınar Baraj Gölü (1.2 km), YH-14 Yangın Havuzu (0.8 km - Kapasite: 400 ton)",
        "roads_railroads": "D400 Karayolu (3.5 km), Oymapınar Servis Yolu (0.5 km - Tek şeritli asfalt), Antalya-Konya bağlantı yolu",
        "caption": "Manavgat Oymapınar Barajı üst yamaçlarında kızılçam ormanında kuvvetli poyrazla birlikte alevler hızla vadi yukarısına tırmanıyor. Yoğun duman Karavca köyü istikametine yayılmış durumda."
    },
    {
        "city": "Muğla", "district": "Marmaris",
        "terrain": "Sık kızılçam ve maki örtüsü, kıyı burnu ve dik yamaçlar",
        "threat": "İçmeler turizm bölgesi, oteller ve 100 kW trafo merkezi",
        "coordinates": "36.802°N, 28.231°E",
        "head_coord": "[36.805°N, 28.234°E] - Oteller Sırtı Kafa Noktası",
        "arazoz_coord": "[36.801°N, 28.238°E] - İçmeler Turizm Bölgesi Savunma Sektörü",
        "trench_line": "[36.803°N, 28.236°E] ile [36.806°N, 28.239°E] koordinatları arasındaki 380 metrelik hat",
        "water_coord": "[36.798°N, 28.242°E] - Marmaris Körfezi Sahil İkmal Noktası",
        "resupply_route": "[36.799°N, 28.240°E] (Sahil Dolum) -> [36.801°N, 28.238°E] (Oteller Savunma Hattı)",
        "evac_coord": "[36.808°N, 28.245°E] - D400 Marmaris Ana Arteri Çıkış Kavşağı",
        "fire_area": "28 Hektar (eğim yönlü hızlı yayılım)",
        "villages": "İçmeler Mahallesi (0.9 km, Nüfus: 6500), Turunç (4.2 km, Nüfus: 2100)",
        "water_sources": "Marmaris Körfezi Deniz Suyu (0.7 km), İçmeler Göleti (1.5 km), YH-08 Yangın Havuzu",
        "roads_railroads": "Marmaris-Turunç Karayolu (0.4 km), D400 Muğla-Marmaris ana arter (5 km)",
        "caption": "İçmeler sırtlarında lodos etkisiyle başlayan örtü yangını ağaç taçlarına sıçradı. Oteller bölgesine doğru alev parçacıkları (spotting) düşüyor."
    },
    {
        "city": "Çanakkale", "district": "Gelibolu",
        "terrain": "Tarihi milli park sahası, rüzgara açık tepe silsilesi",
        "threat": "Kabatepe feribot iskelesi, Çanakkale Şehitlikleri ve Anzak Koyu yolları",
        "coordinates": "40.215°N, 26.284°E",
        "head_coord": "[40.217°N, 26.281°E] - Kabatepe İskelesi Orman Sınırı",
        "arazoz_coord": "[40.219°N, 26.279°E] - Kilitbahir Yolu Savunma Sektörü",
        "trench_line": "[40.218°N, 26.280°E] ile [40.221°N, 26.283°E] koordinatları arasındaki 500 metrelik hat",
        "water_coord": "[40.211°N, 26.288°E] - Çanakkale Boğazı Kıyı Su Alım İskelesi",
        "resupply_route": "[40.212°N, 26.286°E] (Kıyı Dolum) -> [40.219°N, 26.279°E] (Kilitbahir Yolu İkmal Hattı)",
        "evac_coord": "[40.223°N, 26.290°E] - E87 Çanakkale-Edirne Karayolu Kavşağı",
        "fire_area": "18 Hektar (ilk 20 dakika içinde)",
        "villages": "Kilitbahir Köyü (3.1 km, Nüfus: 1200), Alçıtepe (4.5 km, Nüfus: 950)",
        "water_sources": "Çanakkale Boğazı (1.1 km), Ege Denizi Kabatepe Sahili (0.9 km)",
        "roads_railroads": "E87 Çanakkale-Edirne Karayolu (8 km), Gelibolu Tarihi Alan Asfalt Sahil Yolu (0.3 km)",
        "caption": "Gelibolu Tarihi Milli Park alanında batı rüzgarı ile çam ormanı taban örtüsü tutuştu. Duman Kabatepe iskelesi yönünde görüşü azaltıyor."
    },
    {
        "city": "İzmir", "district": "Çeşme-Ildır",
        "terrain": "Kuvvetli poyraz koridoru, makilik ve ardıç örtüsü",
        "threat": "Rüzgar enerji santrali tribünleri, Ildır kıyı konutları",
        "coordinates": "38.385°N, 26.482°E",
        "head_coord": "[38.388°N, 26.485°E] - Rüzgar Santrali Tribün Hattı Kafa Noktası",
        "arazoz_coord": "[38.389°N, 26.489°E] - Ildır Köyü Çeperi Savunma Sektörü",
        "trench_line": "[38.387°N, 26.486°E] ile [38.391°N, 26.490°E] koordinatları arasındaki 600 metrelik hat",
        "water_coord": "[38.381°N, 26.478°E] - Ege Denizi Ildır Körfezi Alım Sahası",
        "resupply_route": "[38.382°N, 26.480°E] (Körfez Dolum) -> [38.389°N, 26.489°E] (Ildır Çeperi Besleme Hattı)",
        "evac_coord": "[38.394°N, 26.495°E] - İzmir-Çeşme Otoyolu O-32 Bağlantı Kavşağı",
        "fire_area": "62 Hektar (geniş cepheli maki yangını)",
        "villages": "Ildır Köyü (1.5 km, Nüfus: 1800), Germiyan (4.0 km, Nüfus: 1100)",
        "water_sources": "Ege Denizi Ildır Körfezi (0.6 km), Alaçatı Barajı (7 km)",
        "roads_railroads": "İzmir-Çeşme Otoyolu O-32 (9 km), Ildır Sahil Yolu (0.2 km), TCDD İzmir-Aliağa demiryolu hattı (45 km - Lojistik gar)",
        "caption": "Ildır tepelerinde şiddetli poyraz makilik alanda alevleri hızla sürüklüyor. Rüzgar santrali hattına doğru alev dili oluşmuş durumda."
    },
    {
        "city": "Mersin", "district": "Gülnar",
        "terrain": "Yüksek rakımlı kanyon vadisi, dik dağlık kızılçam sahası",
        "threat": "Akkuyu Nükleer Santral lojistik iletim hattı ve tarım arazileri",
        "coordinates": "36.341°N, 33.402°E",
        "head_coord": "[36.344°N, 33.406°E] - Kanyon Çıkışı Taç Noktası",
        "arazoz_coord": "[36.347°N, 33.410°E] - Büyükeceli Yerleşim Çeperi Savunma Sektörü",
        "trench_line": "[36.345°N, 33.408°E] ile [36.349°N, 33.412°E] koordinatları arasındaki 550 metrelik hat",
        "water_coord": "[36.335°N, 33.398°E] - YH-22 Yangın Havuzu ve Sahil Alımı",
        "resupply_route": "[36.336°N, 33.399°E] (YH-22 Dolum Noktası) -> [36.347°N, 33.410°E] (Büyükeceli İkmal Hattı)",
        "evac_coord": "[36.350°N, 33.415°E] - D400 Akdeniz Sahil Yolu Kontrol Kavşağı",
        "fire_area": "85 Hektar (kanyon içi baca etkisi)",
        "villages": "Büyükeceli (2.1 km, Nüfus: 2400), Koçaşlı Köyü (3.5 km, Nüfus: 680)",
        "water_sources": "Akdeniz Sahili (3.0 km), Gezende Barajı (14 km), YH-22 ve YH-23 Havuzları (1.2 km)",
        "roads_railroads": "D400 Akdeniz Sahil Yolu (1.8 km), Mersin-Adana Demiryolu İkmal Lojistik Terminali (60 km)",
        "caption": "Gülnar kanyon vadisinde başlayan yangın, vadi içi türbülans ve baca etkisiyle hızla büyüyor. Duman D400 karayolunu kapattı."
    }
]

WIND_CONDITIONS = [
    {"dir": "Poyraz (KD)", "speed": 28, "risk": "Kritik - Rüzgar yönünde hızlı taç yangını riski"},
    {"dir": "Lodos (GB)", "speed": 34, "risk": "Yüksek Risk - Nem düşük, alev cephesi genişliyor"},
    {"dir": "Kuzey-Kuzeybatı", "speed": 18, "risk": "Orta-Yüksek - Yamaç yukarı yayılma eğilimi"},
    {"dir": "Doğu-Güneydoğu", "speed": 42, "risk": "Acil Durum - Aşırı rüzgar, havadan müdahale kısıtlı"},
    {"dir": "Batı", "speed": 12, "risk": "Kontrollü - Yer müdahalesi için uygun rüzgar"}
]

RESOURCES_POOL = [
    {"air_amphibious": 2, "air_heli": 4, "ground_arazoz": 12, "ground_dozer": 2, "personnel": 45},
    {"air_amphibious": 1, "air_heli": 6, "ground_arazoz": 18, "ground_dozer": 4, "personnel": 80},
    {"air_amphibious": 3, "air_heli": 8, "ground_arazoz": 24, "ground_dozer": 5, "personnel": 120},
    {"air_amphibious": 0, "air_heli": 3, "ground_arazoz": 8,  "ground_dozer": 1, "personnel": 25},
    {"air_amphibious": 4, "air_heli": 10, "ground_arazoz": 30, "ground_dozer": 6, "personnel": 160}
]

def generate_tactical_scenarios(extracted_corpus: list, num_samples: int = 180) -> list:
    """Generates synthetic tactical dispatch scenarios with explicit GPS coordinate commands."""
    samples = []
    
    doctrinal_snippets = []
    optimization_snippets = []
    
    for paper in extracted_corpus:
        if paper["domain"] == "doctrinal":
            doctrinal_snippets.extend(paper["chunks"][:15])
        else:
            optimization_snippets.extend(paper["chunks"][:15])
            
    default_doc_snippet = "TAMP ve OGM Orman Yangınları Müdahale Yönergesi: Can güvenliği ve yerleşim yerleri öncelikli koruma hedefidir. Rüzgar hızı 25 km/s üzerinde ve arazi eğimi yüksekse havadan su perdesi oluşturulur ve yerleşim hattına savunma arazözleri konuşlandırılır."
    default_opt_snippet = "Integer Linear Programming (ILP) and spatial optimization principles prioritize initial attack dispatch within the first 30 minutes to minimize non-linear fire perimeter growth and optimize aerial turnaround cycles."
    
    for i in range(num_samples):
        reg = random.choice(TURKISH_REGIONS)
        wnd = random.choice(WIND_CONDITIONS)
        res = random.choice(RESOURCES_POOL)
        
        doc_ctx = random.choice(doctrinal_snippets) if doctrinal_snippets else default_doc_snippet
        opt_ctx = random.choice(optimization_snippets) if optimization_snippets else default_opt_snippet
        
        temp = random.randint(34, 42)
        hum = random.randint(12, 24)
        
        # Build multi-modal instruction requesting explicit coordinate-based commands
        instruction = (
            f"### ORMAN YANGINI ACİL SEVKİYAT VE KOORDİNAT KOMUT TALİMATI\n"
            f"**[İHBAR / GÖRSEL CAPTION]:** {reg['caption']}\n\n"
            f"**[GIS VE METEOROLOJİK TELEMETRİ VERİLERİ]:**\n"
            f"- **Konum & Merkez Koordinat:** {reg['city']} / {reg['district']} ({reg['coordinates']})\n"
            f"- **Yangın Alanı & Cephe:** {reg['fire_area']} - {reg['terrain']}\n"
            f"- **Hava Durumu:** Sıcaklık: {temp}°C | Bağıl Nem: %{hum} | Rüzgar: {wnd['dir']} - {wnd['speed']} km/s ({wnd['risk']})\n"
            f"- **Tehdit Altındaki Yerleşimler & Nüfus:** {reg['villages']} | Diğer Tehditler: {reg['threat']}\n"
            f"- **Altyapı (Karayolu & Demiryolu):** {reg['roads_railroads']}\n"
            f"- **Yakın Su Kaynakları:** {reg['water_sources']}\n"
            f"- **Mevcut / Sevk Edilebilir Güçler:** {res['air_amphibious']} Amfibik Uçak, {res['air_heli']} Helikopter, "
            f"{res['ground_arazoz']} Arazöz, {res['ground_dozer']} Dozer, {res['personnel']} Personel\n\n"
            f"TAMP ve resmi optimizasyon (ILP) ilkelerine göre;\n"
            f"BİLGİLERİ KESİNLİKLE GPS KOORDİNATLARI ([Enlem°N, Boylam°E]) ÜZERİNDEN VEREREK:\n"
            f"1) Hangi koordinata İTFAİYE / ARAZÖZ sevk edileceğini ve hangi sektörün savunulacağını,\n"
            f"2) Hangi koordinatlar arasına DOZER ile HENDEK / YANGIN ŞERİDİ açılacağını,\n"
            f"3) Hangi koordinattan SU ALIMI yapılıp hangi koordinata SU SEVKİYATI / İKMALİ gerçeleştirileceğini,\n"
            f"4) Tahliye, karayolu ve altyapı yönetim koordinatlarını,\n"
            f"5) Matematiksel optimizasyon ve TAMP gerekçesini açıkça emir olarak yaz."
        )
        
        context = f"MEVZUAT VE OPTİMİZASYON BAĞLAMI:\n1. TAMP / OGM Doktrini: {doc_ctx[:350]}\n2. Kaynak Optimizasyon Modeli: {opt_ctx[:350]}"
        
        if wnd['speed'] >= 30:
            priority = "SEVİYE 4 (KRİTİK - ULUSAL ACİL DURUM)"
            evac = "DERHAL TAHLİYE"
        elif wnd['speed'] >= 20:
            priority = "SEVİYE 3 (YÜKSEK - BÖLGESEL TEHDİT)"
            evac = "ÖNLEYİCİ TAHLİYE UYARISI"
        else:
            priority = "SEVİYE 2 (KONTROLLÜ - YEREL KONTROL)"
            evac = "GÖZETİM VE İZLEME"
            
        arazoz_savunma = int(res['ground_arazoz'] * 0.65)
        arazoz_taarruz = res['ground_arazoz'] - arazoz_savunma
        
        response = (
            f"### FIREFL-AI KOORDİNAT BAZLI TAKTİKSEL SEVKİYAT VE MÜDAHALE EMİRLERİ\n\n"
            f"#### 1. İTFAİYE / ARAZÖZ KONUŞLANDIRMA KOORDİNATLARI (FIRE TRUCK DEPLOYMENT)\n"
            f"- **Savunma Sektörü Konuşlandırması:** **{arazoz_savunma} Arazöz** doğrudan **{reg['arazoz_coord']}** koordinatına sevk edilmiş olup yerleşim ve kritik tesis hattında yüksek basınçlı su perdesi kuracaktır.\n"
            f"- **Kanat Taarruz Sektörü:** Kalan **{arazoz_taarruz} Arazöz** ve **{res['personnel']} Personel** doğrudan **{reg['head_coord']}** koordinatında sağ ve sol kanatları baskılayacaktır.\n\n"
            f"#### 2. HENDEK VE YANGIN ŞERİDİ AÇMA KOORDİNATLARI (FIREBREAK / TRENCH LINE)\n"
            f"- **Dozer Hendek Çalışması:** **{res['ground_dozer']} Dozer** derhal **{reg['trench_line']}** üzerinde en az 30 metre genişliğinde çıplak toprak hendek / yangın önleme şeridi açarak alev ilerlemesini kesecektir.\n\n"
            f"#### 3. SU SEVKİYATI, İKMAL VE HAVA ATIM KOORDİNATLARI (WATER RESUPPLY & SCOOPING)\n"
            f"- **Su Alım Kaynağı Koordinatı (Source):** **{res['air_amphibious']} Amfibik Uçak** ve **{res['air_heli']} Helikopter** **{reg['water_coord']}** koordinatından sürekli su ikmali yapacaktır.\n"
            f"- **Su Boşaltım / Atım Koordinatı (Target):** Alınan su yükleri periyodik olarak **{reg['head_coord']}** kafa cephesine boşaltılacaktır.\n"
            f"- **Kara Tanker İkmal Rotası:** Su ikmal araçları **{reg['resupply_route']}** koordinat rotasında savunma arazözlerine sürekli su taşıyacaktır.\n\n"
            f"#### 4. TAHLİYE VE ALTYAPI KONTROL KOORDİNATI (EVACUATION & ROAD CONTROL)\n"
            f"- **Tahliye Durumu:** {priority} kapsamında {reg['villages']} için '{evac}' ilan edilmiştir.\n"
            f"- **Yol Kapatma ve Yeşil Koridor Koordinatı:** **{reg['evac_coord']}** sivil trafiğe kapatılarak yalnızca arazöz, itfaiye ve tahliye konvoylarına tahsis edilmiştir.\n\n"
            f"#### 5. MATEMATİKSEL OPTİMİZASYON VE TAMP GEREKÇESİ (RATIONALE)\n"
            f"- **ILP Koordinat Optimizasyonu:** Su alım noktası {reg['water_coord']} ile taarruz sektörü {reg['head_coord']} arasındaki mesafe minimize edilerek hava araçlarının 4.5 dakikalık dönüş periyotlarıyla (turnaround cycle) atım yapması hedeflenmiş, toplam kayıp fonksiyonu %74 düşürülmüştür.\n"
            f"- **TAMP Koordinasyonu:** TAMP Orman Yangınları Müdahale Afet Grubu yönergesi gereği OGM kriz masası ile AFAD koordinasyon koordinatlarında entegrasyon sağlanmıştır."
        )
        
        samples.append({
            "domain": "tactical_dispatch",
            "instruction": instruction,
            "context": context,
            "response": response
        })
    return samples

def generate_doctrinal_and_opt_qa(extracted_corpus: list) -> list:
    """Generates doctrinal QA and optimization reasoning QA pairs from extracted paper chunks."""
    qa_samples = []
    
    # Pre-crafted high-concept QA pairs covering TAMP, OGM, and Mathematical Wildfire Optimization
    base_qa = [
        {
            "domain": "doctrinal",
            "instruction": "TAMP (Türkiye Afet Müdahale Planı) kapsamında orman yangınlarında ana çözüm ortağı ve koordinasyon yetkisi hangi kurumdadır?",
            "context": "Türkiye Afet Müdahale Planı (TAMP) Afet Grubu Operasyon Yönergeleri.",
            "response": "TAMP kapsamında 'Orman Yangınları Müdahale Afet Grubu' ana çözüm ortağı Tarım ve Orman Bakanlığı / Orman Genel Müdürlüğü (OGM)'dür. Destek çözüm ortakları arasında AFAD, Valilikler, Belediyeler (İtfaiye) ve Milli Savunma Bakanlığı yer alır."
        },
        {
            "domain": "doctrinal",
            "instruction": "OGM Yangınla Mücadele Yönergesine göre orman yangınlarında hava araçlarının (uçak ve helikopter) operasyonel rüzgar hızı sınırı nedir?",
            "context": "OGM Orman Yangınlarıyla Mücadele Yönergesi ve Uçuş Emniyet Kuralları.",
            "response": "Hava araçlarında emniyetli müdahale sınırı rüzgar hızına, türbülansa ve görüş mesafesine bağlıdır. Genellikle rüzgar hızının 40-50 km/s (yaklaşık 25-30 knot) üzerine çıktığı aşırı türbülanslı vadilerde hava araçlarının alçak uçuşla su atımı kısıtlanır ve öncelik çevre savunması ile kara birliklerine verilir."
        },
        {
            "domain": "optimization",
            "instruction": "How does an Integer Linear Programming (ILP) model optimize the spatial and temporal allocation of firefighting resources during initial attack?",
            "context": "Academic literature on wildfire suppression optimization and integer programming.",
            "response": "An Integer Linear Programming (ILP) model formulations minimize total expected loss (timber, property, suppression cost) subject to constraints on resource availability, travel/routing times, and fire perimeter growth rates. Binary decision variables assign specific firefighting units (e.g., air tankers, dozer teams) to specific fire sectors at discrete time periods to achieve containment before the fire transitions to extended attack."
        },
        {
            "domain": "optimization",
            "instruction": "Why is initial attack dispatch velocity critical in mathematical models of wildfire containment?",
            "context": "Integrated Simulation and Optimization for Wildfire Containment studies.",
            "response": "Wildfire perimeter area expands quadratically over time under uniform wind conditions. Mathematical optimization models demonstrate that reducing initial dispatch delay by even 10-15 minutes exponentially reduces the total line-building effort required for containment, preventing resource exhaustion across simultaneous multi-fire scenarios."
        }
    ]
    qa_samples.extend(base_qa)
    
    # Automatically generate QA from extracted paper chunks
    for paper in extracted_corpus:
        domain = paper["domain"]
        for i, chunk in enumerate(paper["chunks"]):
            if len(chunk) < 150:
                continue
            if i % 3 != 0: # Take every 3rd chunk to ensure diversity
                continue
                
            if domain == "doctrinal":
                inst = f"Aşağıdaki TAMP / resmi müdahale belgesi metnindeki ilke ve kurallara göre kriz koordinasyon prensibini özetle: ({paper['filename']})"
                resp = f"TAMP / OGM resmi belgesine ({paper['filename']}) göre esaslar şu şekildedir:\n\n{chunk[:600]}\n\nBu kural, yangın müdahalesinde görev yetki dağılımını ve sahadaki kaynakların önceliklendirilmesini belirler."
            else:
                inst = f"Explain the optimization or resource scheduling methodology presented in this wildfire suppression research ({paper['filename']}):"
                resp = f"According to '{paper['filename']}', the analytical framework is defined as follows:\n\n{chunk[:600]}\n\nThis methodology aids emergency dispatchers by mathematically balancing resource constraints against dynamic fire propagation."
                
            qa_samples.append({
                "domain": domain,
                "instruction": inst,
                "context": f"Source document: {paper['filename']} (Section chunk {i+1})",
                "response": resp
            })
            
    return qa_samples

def main():
    base_dir = Path(__file__).resolve().parent
    data_dir = base_dir / "data"
    extracted_path = data_dir / "extracted_papers.json"
    output_path = data_dir / "firefl_dispatch_dataset.jsonl"
    
    print("=" * 70)
    print("  FIREFL-AI: STAGE 2 - SFT TRAINING DATASET GENERATION")
    print("=" * 70)
    
    if not extracted_path.exists():
        print(f"[ERROR] {extracted_path} not found! Please run `python 1_extract_papers.py` first.")
        return
        
    with open(extracted_path, "r", encoding="utf-8") as f:
        extracted_corpus = json.load(f)
        
    print(f"Loaded {len(extracted_corpus)} extracted papers from corpus.\n")
    
    print("Generating Doctrinal QA and Optimization Reasoning QA pairs...")
    qa_samples = generate_doctrinal_and_opt_qa(extracted_corpus)
    print(f"  -> Generated {len(qa_samples)} QA pairs.")
    
    print("Generating Turkish/English Tactical Emergency Dispatch Scenarios...")
    tactical_samples = generate_tactical_scenarios(extracted_corpus, num_samples=250)
    print(f"  -> Generated {len(tactical_samples)} tactical dispatch scenarios.")
    
    full_dataset = qa_samples + tactical_samples
    random.shuffle(full_dataset)
    
    with open(output_path, "w", encoding="utf-8") as f:
        for sample in full_dataset:
            f.write(json.dumps(sample, ensure_ascii=False) + "\n")
            
    print("\n" + "=" * 70)
    print(f"  DATASET GENERATION COMPLETE:")
    print(f"  Total Training Examples    : {len(full_dataset)}")
    print(f"  - Doctrinal & Opt QA       : {len(qa_samples)}")
    print(f"  - Tactical Dispatch Scenarios : {len(tactical_samples)}")
    print(f"  Saved SFT Dataset          : {output_path}")
    print("=" * 70)

if __name__ == "__main__":
    main()
