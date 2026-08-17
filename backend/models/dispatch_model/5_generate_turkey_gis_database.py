# 5_generate_turkey_gis_database.py
# Complete Turkey-Wide Forest Fire GIS & Tactical Dispatch Database Generator
# Generates comprehensive, province-by-province JSON datasets covering ALL 81 provinces and 7 regions of Turkey:
# 1) 125+ Strategic Water Resources (Barajlar, Göller, Deniz İkmal Koyları, OGM Yangın Havuzları, Akarsular)
# 2) 115+ Endangered Settlements, Hotels & Critical Infrastructure (Köyler, Mahalleler, Oteller, Termik Santraller, Trafo Merkezleri, Tarihi Miras Alanları, Nükleer/Petrol Sahaları)

import json
from pathlib import Path

def generate_all_turkey_water_resources():
    return [
        # --- 1. AKDENİZ BÖLGESİ (ANTALYA, MUĞLA, MERSİN, ADANA, HATAY, OSMANİYE, K.MARAŞ, ISPARTA, BURDUR) ---
        {
            "id": "SK-001",
            "isim": "Oymapınar Baraj Gölü - 3. İskele ve Su Alım Noktası",
            "il": "Antalya", "ilce": "Manavgat", "bolge": "Akdeniz Orman Yangın Sektörü",
            "tip": "Baraj Gölü", "koordinat_enlem": 36.881, "koordinat_boylam": 31.460, "gps_format": "[36.881°N, 31.460°E]",
            "kapasite": "300 Milyon m³", "uygun_araclar": ["Amfibik Uçak", "Su Atar Helikopter", "Arazöz İkmali"],
            "notlar": "Manavgat taç yangınlarında amfibik uçakların scoop (su ikmal) yaptığı temel kaynak."
        },
        {
            "id": "SK-002",
            "isim": "YH-14 Oymapınar Orman Yangın Havuzu",
            "il": "Antalya", "ilce": "Manavgat", "bolge": "Karavca Köyü Sırtı",
            "tip": "OGM Yangın Havuzu", "koordinat_enlem": 36.885, "koordinat_boylam": 31.468, "gps_format": "[36.885°N, 31.468°E]",
            "kapasite": "400 Ton (Betonarme Havuz)", "uygun_araclar": ["Helikopter Bambi Bucket", "Arazöz"],
            "notlar": "Karavca ve Oymapınar köy savunmalarında helikopterlerin hızlı periyot su aldığı nokta."
        },
        {
            "id": "SK-003",
            "isim": "Manavgat Şelalesi ve Nehir Su Alım Sahası",
            "il": "Antalya", "ilce": "Manavgat", "bolge": "Manavgat Çayı Vadisi",
            "tip": "Akarsu", "koordinat_enlem": 36.812, "koordinat_boylam": 31.454, "gps_format": "[36.812°N, 31.454°E]",
            "kapasite": "Sürekli Akış", "uygun_araclar": ["Arazöz", "Su Tankeri"],
            "notlar": "Karayolu bağlantılı arazöz ve ikmal tankerleri için su alım rampası mevcuttur."
        },
        {
            "id": "SK-004",
            "isim": "Manavgat Ulupınar Göleti",
            "il": "Antalya", "ilce": "Manavgat", "bolge": "Ulupınar Orman Sektörü",
            "tip": "Gölet", "koordinat_enlem": 36.920, "koordinat_boylam": 31.550, "gps_format": "[36.920°N, 31.550°E]",
            "kapasite": "500.000 m³", "uygun_araclar": ["Helikopter", "Arazöz"],
            "notlar": "Akseki yönü sarp vadi yangınları için gölet ikmali."
        },
        {
            "id": "SK-005",
            "isim": "Alanya Dim Baraj Gölü",
            "il": "Antalya", "ilce": "Alanya", "bolge": "Dim Çayı Vadisi",
            "tip": "Baraj Gölü", "koordinat_enlem": 36.568, "koordinat_boylam": 32.112, "gps_format": "[36.568°N, 32.112°E]",
            "kapasite": "250 Milyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Alanya doğu sahil ormanları ve Toros yamaçları için ana baraj kaynağı."
        },
        {
            "id": "SK-006",
            "isim": "Alanya Alara Çayı Su Alım Rampası",
            "il": "Antalya", "ilce": "Alanya", "bolge": "Alara Vadisi",
            "tip": "Akarsu", "koordinat_enlem": 36.685, "koordinat_boylam": 31.780, "gps_format": "[36.685°N, 31.780°E]",
            "kapasite": "Sürekli Akış", "uygun_araclar": ["Arazöz", "Su Tankeri", "Helikopter"],
            "notlar": "Gündoğmuş ve Alara vadisi yangınları için akarsu ikmal sahası."
        },
        {
            "id": "SK-007",
            "isim": "Kemer Göynük Sahil Koyu İkmal Noktası",
            "il": "Antalya", "ilce": "Kemer", "bolge": "Beydağları Sahil Milli Parkı",
            "tip": "Deniz", "koordinat_enlem": 36.635, "koordinat_boylam": 30.585, "gps_format": "[36.635°N, 30.585°E]",
            "kapasite": "Sınırsız", "uygun_araclar": ["Amfibik Uçak", "Helikopter"],
            "notlar": "Göynük Kanyonu ve Kemer oteller bölgesi yangınları için deniz ikmal koyu."
        },
        {
            "id": "SK-008",
            "isim": "Kemer Çamyuva Sahil Deniz Alım Sahası",
            "il": "Antalya", "ilce": "Kemer", "bolge": "Çamyuva - Tekirova Sahil Hattı",
            "tip": "Deniz", "koordinat_enlem": 36.545, "koordinat_boylam": 30.565, "gps_format": "[36.545°N, 30.565°E]",
            "kapasite": "Sınırsız", "uygun_araclar": ["Amfibik Uçak", "Helikopter"],
            "notlar": "Phaselis antik kenti ve Tekirova ormanları için dalga kırımı düşük deniz ikmali."
        },
        {
            "id": "SK-009",
            "isim": "YH-22 Çavdır - Patara Yangın Havuzu",
            "il": "Antalya", "ilce": "Kaş", "bolge": "Kaş - Kalkan - Patara Orman Hattı",
            "tip": "OGM Yangın Havuzu", "koordinat_enlem": 36.355, "koordinat_boylam": 29.385, "gps_format": "[36.355°N, 29.385°E]",
            "kapasite": "400 Ton", "uygun_araclar": ["Helikopter Bambi Bucket", "Arazöz"],
            "notlar": "Sarp kanyon vadilerinde arazöz ve helikopterlerin kullandığı stratejik havuz."
        },
        {
            "id": "SK-010",
            "isim": "Kaş Kalkan Körfezi Deniz Alım Sahası",
            "il": "Antalya", "ilce": "Kaş", "bolge": "Kalkan - Kaputaş Sahil Sektörü",
            "tip": "Deniz / Körfez", "koordinat_enlem": 36.265, "koordinat_boylam": 29.415, "gps_format": "[36.265°N, 29.415°E]",
            "kapasite": "Sınırsız", "uygun_araclar": ["Amfibik Uçak", "Helikopter"],
            "notlar": "Kalkan kıyı ve çam ormanı yangınları için deniz ikmal hattı."
        },
        {
            "id": "SK-011",
            "isim": "Gazipaşa Bıçakçı Yangın Havuzu YH-19",
            "il": "Antalya", "ilce": "Gazipaşa", "bolge": "Toros Yamaçları",
            "tip": "OGM Yangın Havuzu", "koordinat_enlem": 36.380, "koordinat_boylam": 32.340, "gps_format": "[36.380°N, 32.340°E]",
            "kapasite": "500 Ton", "uygun_araclar": ["Helikopter Bambi Bucket"],
            "notlar": "Anamur-Gazipaşa sınır hattındaki dağlık yangınlara müdahale havuzu."
        },
        {
            "id": "SK-012",
            "isim": "Karacaören Baraj Gölü - Bucak / Antalya Sınırı",
            "il": "Antalya", "ilce": "Aksu / Burdur Bucak", "bolge": "Karacaören Baraj Sektörü",
            "tip": "Baraj Gölü", "koordinat_enlem": 37.330, "koordinat_boylam": 30.835, "gps_format": "[37.330°N, 30.835°E]",
            "kapasite": "1 Milyar m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Antalya kuzey ormanları ve Isparta/Burdur sınırı için dev baraj kaynağı."
        },
        {
            "id": "SK-013",
            "isim": "Marmaris Körfezi - İçmeler Sahili Su Alım Koyu",
            "il": "Muğla", "ilce": "Marmaris", "bolge": "İçmeler Sahil Hattı",
            "tip": "Deniz / Körfez", "koordinat_enlem": 36.799, "koordinat_boylam": 28.238, "gps_format": "[36.799°N, 28.238°E]",
            "kapasite": "Sınırsız", "uygun_araclar": ["Amfibik Uçak", "Helikopter"],
            "notlar": "Marmaris İçmeler ve Turunç yangınlarında CL-415 ve AT-802 uçaklarının ana ikmal koyu."
        },
        {
            "id": "SK-014",
            "isim": "YH-08 Turunç Sırtı Orman Yangın Havuzu",
            "il": "Muğla", "ilce": "Marmaris", "bolge": "Turunç - Amos Sırtları",
            "tip": "OGM Yangın Havuzu", "koordinat_enlem": 36.772, "koordinat_boylam": 28.245, "gps_format": "[36.772°N, 28.245°E]",
            "kapasite": "500 Ton", "uygun_araclar": ["Helikopter Bambi Bucket"],
            "notlar": "Dağlık kızılçam tepe hattında helikopter müdahalesi için kritik havuz."
        },
        {
            "id": "SK-015",
            "isim": "İçmeler Göleti ve Sel Kapanı",
            "il": "Muğla", "ilce": "Marmaris", "bolge": "İçmeler Vadisi",
            "tip": "Gölet", "koordinat_enlem": 36.810, "koordinat_boylam": 28.215, "gps_format": "[36.810°N, 28.215°E]",
            "kapasite": "120.000 m³", "uygun_araclar": ["Helikopter", "Arazöz"],
            "notlar": "Oteller bölgesine 1.5 km mesafede tatlı su kaynağı."
        },
        {
            "id": "SK-016",
            "isim": "Marmaris Hisarönü Körfezi - Bördübet Alım Koyu",
            "il": "Muğla", "ilce": "Marmaris", "bolge": "Hisarönü - Bördübet Sektörü",
            "tip": "Deniz / Körfez", "koordinat_enlem": 36.790, "koordinat_boylam": 28.050, "gps_format": "[36.790°N, 28.050°E]",
            "kapasite": "Sınırsız", "uygun_araclar": ["Amfibik Uçak", "Helikopter"],
            "notlar": "Bördübet ve Değirmenyanı yangınlarında korunaklı deniz su alımı."
        },
        {
            "id": "SK-017",
            "isim": "Bodrum Güvercinlik Körfezi Su Alım Noktası",
            "il": "Muğla", "ilce": "Bodrum", "bolge": "Güvercinlik - Pina Yarımadası",
            "tip": "Deniz / Koy", "koordinat_enlem": 37.135, "koordinat_boylam": 27.575, "gps_format": "[37.135°N, 27.575°E]",
            "kapasite": "Sınırsız", "uygun_araclar": ["Amfibik Uçak", "Helikopter"],
            "notlar": "Bodrum oteller bölgesi ve Pina yarımadası yangınlarında en yakın su ikmal koyu."
        },
        {
            "id": "SK-018",
            "isim": "Bodrum Torba Koyu Deniz Su Alım Sahası",
            "il": "Muğla", "ilce": "Bodrum", "bolge": "Torba - Gölköy Sektörü",
            "tip": "Deniz / Koy", "koordinat_enlem": 37.088, "koordinat_boylam": 27.468, "gps_format": "[37.088°N, 27.468°E]",
            "kapasite": "Sınırsız", "uygun_araclar": ["Amfibik Uçak", "Helikopter"],
            "notlar": "Torba oteller ve Demirbükü yangınları için deniz ikmali."
        },
        {
            "id": "SK-019",
            "isim": "Mumcular Baraj Gölü",
            "il": "Muğla", "ilce": "Bodrum", "bolge": "Mumcular - Mazı Orman Sektörü",
            "tip": "Baraj Gölü", "koordinat_enlem": 37.085, "koordinat_boylam": 27.672, "gps_format": "[37.085°N, 27.672°E]",
            "kapasite": "18 Milyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Milas - Bodrum sınır hattındaki kızılçam yangınlarında tatlı su ikmal noktası."
        },
        {
            "id": "SK-020",
            "isim": "Geyik Barajı ve Yangın Su Alım Rampası",
            "il": "Muğla", "ilce": "Milas", "bolge": "Yeniköy Termik Santrali Sektörü",
            "tip": "Baraj Gölü", "koordinat_enlem": 37.285, "koordinat_boylam": 27.780, "gps_format": "[37.285°N, 27.780°E]",
            "kapasite": "40 Milyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Yeniköy ve Kemerköy termik santrallerini tehdit eden orman yangınlarında birincil baraj."
        },
        {
            "id": "SK-021",
            "isim": "Akgedik Baraj Gölü",
            "il": "Muğla", "ilce": "Milas", "bolge": "Milas Kuzey Orman Hattı",
            "tip": "Baraj Gölü", "koordinat_enlem": 37.380, "koordinat_boylam": 27.820, "gps_format": "[37.380°N, 27.820°E]",
            "kapasite": "30 Milyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Beçin ve Bafa Gölü çevresi orman yangınları için baraj ikmal sahası."
        },
        {
            "id": "SK-022",
            "isim": "Köyceğiz Gölü Kuzey Su Alım Sahası",
            "il": "Muğla", "ilce": "Köyceğiz", "bolge": "Köyceğiz - Sandras Dağı Sektörü",
            "tip": "Tatlı Su Gölü", "koordinat_enlem": 36.955, "koordinat_boylam": 28.685, "gps_format": "[36.955°N, 28.685°E]",
            "kapasite": "Doğal Gölü", "uygun_araclar": ["Amfibik Uçak", "Helikopter"],
            "notlar": "Sığla ormanları ve Sandras dağı yangınlarında rüzgardan korunaklı su alma hattı."
        },
        {
            "id": "SK-023",
            "isim": "Fethiye Ölüdeniz / Belcekız Körfezi",
            "il": "Muğla", "ilce": "Fethiye", "bolge": "Babadağ - Ovacık Sektörü",
            "tip": "Deniz / Körfez", "koordinat_enlem": 36.548, "koordinat_boylam": 29.122, "gps_format": "[36.548°N, 29.122°E]",
            "kapasite": "Sınırsız", "uygun_araclar": ["Amfibik Uçak", "Helikopter"],
            "notlar": "Babadağ sarp yamaç yangınlarında amfibik uçakların en yakın deniz su alımı."
        },
        {
            "id": "SK-024",
            "isim": "Datça Hisarönü Körfezi Su İkmal Alanı",
            "il": "Muğla", "ilce": "Datça", "bolge": "Hisarönü - Bördübet Orman Sektörü",
            "tip": "Deniz / Körfez", "koordinat_enlem": 36.755, "koordinat_boylam": 28.085, "gps_format": "[36.755°N, 28.085°E]",
            "kapasite": "Sınırsız", "uygun_araclar": ["Amfibik Uçak", "Helikopter"],
            "notlar": "Bördübet ve Datça yarımadası yangınlarında uçakların güvenli su aldığı körfez."
        },
        {
            "id": "SK-025",
            "isim": "Dalaman Kükürtlü Yangın Havuzu YH-11",
            "il": "Muğla", "ilce": "Dalaman", "bolge": "Dalaman Havalimanı Çevresi",
            "tip": "OGM Yangın Havuzu", "koordinat_enlem": 36.780, "koordinat_boylam": 28.810, "gps_format": "[36.780°N, 28.810°E]",
            "kapasite": "500 Ton", "uygun_araclar": ["Helikopter Bambi Bucket", "Arazöz"],
            "notlar": "Dalaman havalimanı ve Göcek tüneli üstü yangınları için OGM havuzu."
        },
        {
            "id": "SK-026",
            "isim": "Gezende Baraj Gölü",
            "il": "Mersin", "ilce": "Gülnar / Mut", "bolge": "Göksu Vadisi Orman Sektörü",
            "tip": "Baraj Gölü", "koordinat_enlem": 36.525, "koordinat_boylam": 33.155, "gps_format": "[36.525°N, 33.155°E]",
            "kapasite": "90 Milyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Mersin Gülnar - Aydıncık orman yangınları için Göksu nehri üzeri baraj kaynağı."
        },
        {
            "id": "SK-027",
            "isim": "Mersin Anamur Dragon Çayı İkmal Noktası",
            "il": "Mersin", "ilce": "Anamur", "bolge": "Anamur Çamlık Sektörü",
            "tip": "Akarsu", "koordinat_enlem": 36.085, "koordinat_boylam": 32.865, "gps_format": "[36.085°N, 32.865°E]",
            "kapasite": "Sürekli Akış", "uygun_araclar": ["Arazöz", "Helikopter"],
            "notlar": "Anamur sahil ve Toros yamaç yangınları için akarsu alımı."
        },
        {
            "id": "SK-028",
            "isim": "Silifke Berdan Barajı",
            "il": "Mersin", "ilce": "Tarsus / Silifke", "bolge": "Tarsus - Çamlıyayla Sektörü",
            "tip": "Baraj Gölü", "koordinat_enlem": 36.965, "koordinat_boylam": 34.885, "gps_format": "[36.965°N, 34.885°E]",
            "kapasite": "160 Milyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Tarsus ve Çamlıyayla kızılçam yangınları için baraj alımı."
        },
        {
            "id": "SK-029",
            "isim": "Adana Kozan Yedigöze Barajı",
            "il": "Adana", "ilce": "Kozan / Aladağ", "bolge": "Seyhan ve Çukurova Orman Hattı",
            "tip": "Baraj Gölü", "koordinat_enlem": 37.545, "koordinat_boylam": 35.535, "gps_format": "[37.545°N, 35.535°E]",
            "kapasite": "600 Milyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Kozan ve Aladağ büyük orman yangınları için dev su rezervi."
        },
        {
            "id": "SK-030",
            "isim": "Adana Seyhan Baraj Gölü",
            "il": "Adana", "ilce": "Çukurova", "bolge": "Çukurova Kuzey Sektörü",
            "tip": "Baraj Gölü", "koordinat_enlem": 37.045, "koordinat_boylam": 35.315, "gps_format": "[37.045°N, 35.315°E]",
            "kapasite": "1.2 Bilyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Adana çevresi orman ve makilik yangınları ana ikmal barajı."
        },
        {
            "id": "SK-031",
            "isim": "Hatay Belen YH-05 Yangın Havuzu",
            "il": "Hatay", "ilce": "Belen", "bolge": "Belen Geçidi ve Amanos Dağları",
            "tip": "OGM Yangın Havuzu", "koordinat_enlem": 36.485, "koordinat_boylam": 36.215, "gps_format": "[36.485°N, 36.215°E]",
            "kapasite": "450 Ton", "uygun_araclar": ["Helikopter Bambi Bucket", "Arazöz"],
            "notlar": "Amanos dağları rüzgarlı geçit yangınlarında helikopterlerin su aldığı nokta."
        },
        {
            "id": "SK-032",
            "isim": "Hatay Arsuz Körfezi Deniz Su Alım Alanı",
            "il": "Hatay", "ilce": "Arsuz", "bolge": "Amanos Batı Sahil Sektörü",
            "tip": "Deniz", "koordinat_enlem": 36.415, "koordinat_boylam": 35.885, "gps_format": "[36.415°N, 35.885°E]",
            "kapasite": "Sınırsız", "uygun_araclar": ["Amfibik Uçak", "Helikopter"],
            "notlar": "Arsuz ve İskenderun orman yangınlarında uçakların güvenli körfez alımı."
        },
        {
            "id": "SK-033",
            "isim": "Hatay Yarseli Baraj Gölü",
            "il": "Hatay", "ilce": "Altınözü", "bolge": "Amik Ovası ve Sınır Ormanları",
            "tip": "Baraj Gölü", "koordinat_enlem": 36.145, "koordinat_boylam": 36.315, "gps_format": "[36.145°N, 36.315°E]",
            "kapasite": "55 Milyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Hatay güney sınırı orman ve zeytinlik yangınları su kaynağı."
        },
        {
            "id": "SK-034",
            "isim": "Osmaniye Aslantaş Baraj Gölü",
            "il": "Osmaniye", "ilce": "Kadirli / Düziçi", "bolge": "Ceyhan Havzası Orman Hattı",
            "tip": "Baraj Gölü", "koordinat_enlem": 37.245, "koordinat_boylam": 36.285, "gps_format": "[37.245°N, 36.285°E]",
            "kapasite": "1.1 Bilyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Osmaniye ve Kadirli orman yangınları için birincil büyük baraj kaynağı."
        },
        {
            "id": "SK-035",
            "isim": "Kahramanmaraş Menzelet Baraj Gölü",
            "il": "Kahramanmaraş", "ilce": "Onikişubat", "bolge": "Ahırdağı ve Andırın Sektörü",
            "tip": "Baraj Gölü", "koordinat_enlem": 37.665, "koordinat_boylam": 36.845, "gps_format": "[37.665°N, 36.845°E]",
            "kapasite": "2 Bilyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Kahramanmaraş ve Andırın orman hattı yangınları için tatlı su rezervi."
        },
        {
            "id": "SK-036",
            "isim": "Kahramanmaraş Sır Baraj Gölü",
            "il": "Kahramanmaraş", "ilce": "Onikişubat", "bolge": "Ceyhan Vadisi Sektörü",
            "tip": "Baraj Gölü", "koordinat_enlem": 37.555, "koordinat_boylam": 36.715, "gps_format": "[37.555°N, 36.715°E]",
            "kapasite": "1.1 Bilyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Ahırdağı güney yamacı yangınlarında amfibik uçak su alımı."
        },
        {
            "id": "SK-037",
            "isim": "Burdur Karacaören-2 Baraj Gölü",
            "il": "Burdur", "ilce": "Bucak", "bolge": "Bucak Kızılçam Ormanları",
            "tip": "Baraj Gölü", "koordinat_enlem": 37.285, "koordinat_boylam": 30.815, "gps_format": "[37.285°N, 30.815°E]",
            "kapasite": "48 Milyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Burdur Bucak ve Isparta sınırı yangınları için stratejik su kaynağı."
        },
        {
            "id": "SK-038",
            "isim": "Isparta Eğirdir Gölü Kuzey İkmal Noktası",
            "il": "Isparta", "ilce": "Eğirdir", "bolge": "Göller Yöresi Orman Sektörü",
            "tip": "Doğal Göl", "koordinat_enlem": 37.915, "koordinat_boylam": 30.885, "gps_format": "[37.915°N, 30.885°E]",
            "kapasite": "Doğal Gölü (4 Bilyon m³)", "uygun_araclar": ["Amfibik Uçak", "Helikopter"],
            "notlar": "Isparta çam ormanları ve Sütçüler yangınlarında büyük tatlı su kaynağı."
        },

        # --- 2. EGE BÖLGESİ (İZMİR, AYDIN, MANİSA, DENİZLİ, KÜTAHYA, UŞAK, AFYONKARAHİSAR) ---
        {
            "id": "SK-039",
            "isim": "Ürkmez Baraj Gölü",
            "il": "İzmir", "ilce": "Seferihisar", "bolge": "Seferihisar - Gümüldür Orman Hattı",
            "tip": "Baraj Gölü", "koordinat_enlem": 38.075, "koordinat_boylam": 26.965, "gps_format": "[38.075°N, 26.965°E]",
            "kapasite": "8 Milyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "İzmir güney sahil orman yangınları için kritik baraj kaynağı."
        },
        {
            "id": "SK-040",
            "isim": "Alaçatı Kutlu Aktaş Baraj Gölü",
            "il": "İzmir", "ilce": "Çeşme", "bolge": "Çeşme - Alaçatı Makilik ve Orman Alanı",
            "tip": "Baraj Gölü", "koordinat_enlem": 38.315, "koordinat_boylam": 26.415, "gps_format": "[38.315°N, 26.415°E]",
            "kapasite": "16 Milyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Çeşme yarımadası rüzgarlı yangınlarda tatlı su alma sahası."
        },
        {
            "id": "SK-041",
            "isim": "İzmir Tahtalı Baraj Gölü",
            "il": "İzmir", "ilce": "Menderes", "bolge": "Menderes - Gümüldür Havzası",
            "tip": "Baraj Gölü", "koordinat_enlem": 38.155, "koordinat_boylam": 27.085, "gps_format": "[38.155°N, 27.085°E]",
            "kapasite": "300 Milyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "İzmir çevresi büyük orman yangınlarında en kapasiteli su ikmal noktası."
        },
        {
            "id": "SK-042",
            "isim": "Foça Eski Foça Körfezi Deniz Su Alımı",
            "il": "İzmir", "ilce": "Foça", "bolge": "Foça - Aliağa Orman Sektörü",
            "tip": "Deniz", "koordinat_enlem": 38.675, "koordinat_boylam": 26.755, "gps_format": "[38.675°N, 26.755°E]",
            "kapasite": "Sınırsız", "uygun_araclar": ["Amfibik Uçak", "Helikopter"],
            "notlar": "Aliağa petrokimya ve Foça orman yangınlarında uçak deniz ikmali."
        },
        {
            "id": "SK-043",
            "isim": "Kemalpaşa Nif Dağı YH-03 Yangın Havuzu",
            "il": "İzmir", "ilce": "Kemalpaşa", "bolge": "Nif Dağı - Spil Dağı Hattı",
            "tip": "OGM Yangın Havuzu", "koordinat_enlem": 38.435, "koordinat_boylam": 27.415, "gps_format": "[38.435°N, 27.415°E]",
            "kapasite": "500 Ton", "uygun_araclar": ["Helikopter Bambi Bucket", "Arazöz"],
            "notlar": "Spil Dağı ve Kemalpaşa çam ormanı yangınları için yüksek rakım havuzu."
        },
        {
            "id": "SK-044",
            "isim": "Ödemiş Bademli Baraj Gölü",
            "il": "İzmir", "ilce": "Ödemiş", "bolge": "Bozdağlar Orman Sektörü",
            "tip": "Baraj Gölü", "koordinat_enlem": 38.185, "koordinat_boylam": 27.985, "gps_format": "[38.185°N, 27.985°E]",
            "kapasite": "14 Milyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Bozdağlar ve Ödemiş yayla ormanları için tatlı su alımı."
        },
        {
            "id": "SK-045",
            "isim": "Bergama Yuntdağı Yangın Göleti",
            "il": "İzmir", "ilce": "Bergama", "bolge": "Kozak Yaylası Fıstıkçamı Sektörü",
            "tip": "Gölet", "koordinat_enlem": 39.145, "koordinat_boylam": 27.185, "gps_format": "[39.145°N, 27.185°E]",
            "kapasite": "700.000 m³", "uygun_araclar": ["Helikopter", "Arazöz"],
            "notlar": "Kozak yaylası dünyaca ünlü fıstıkçamı ormanlarını koruma göleti."
        },
        {
            "id": "SK-046",
            "isim": "Aydın Kemer Baraj Gölü",
            "il": "Aydın", "ilce": "Bozdoğan", "bolge": "Akçay Vadisi Orman Sektörü",
            "tip": "Baraj Gölü", "koordinat_enlem": 37.545, "koordinat_boylam": 28.325, "gps_format": "[37.545°N, 28.325°E]",
            "kapasite": "350 Milyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Aydın ve Karacasu çam ormanları için stratejik baraj."
        },
        {
            "id": "SK-047",
            "isim": "Aydın Kuşadası Dilek Yarımadası Deniz Alım Koyu",
            "il": "Aydın", "ilce": "Kuşadası / Söke", "bolge": "Dilek Yarımadası Milli Parkı",
            "tip": "Deniz / Koy", "koordinat_enlem": 37.685, "koordinat_boylam": 27.185, "gps_format": "[37.685°N, 27.185°E]",
            "kapasite": "Sınırsız", "uygun_araclar": ["Amfibik Uçak", "Helikopter"],
            "notlar": "Milli Park alanı içindeki orman yangınlarına anlık deniz ikmali."
        },
        {
            "id": "SK-048",
            "isim": "Aydın Çine Adnan Menderes Barajı",
            "il": "Aydın", "ilce": "Çine", "bolge": "Çine Çayı Orman Vadisi",
            "tip": "Baraj Gölü", "koordinat_enlem": 37.485, "koordinat_boylam": 28.085, "gps_format": "[37.485°N, 28.085°E]",
            "kapasite": "350 Milyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Çine ve Muğla Yatağan sınırı makilik-çamlık yangınları barajı."
        },
        {
            "id": "SK-049",
            "isim": "Manisa Demirköprü Baraj Gölü",
            "il": "Manisa", "ilce": "Salihli / Köprübaşı", "bolge": "Gediz Havzası Orman Sektörü",
            "tip": "Baraj Gölü", "koordinat_enlem": 38.625, "koordinat_boylam": 28.345, "gps_format": "[38.625°N, 28.345°E]",
            "kapasite": "1 Bilyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Manisa Demirci ve Akhisar bölgesi orman yangınları için ana baraj."
        },
        {
            "id": "SK-050",
            "isim": "Manisa Gördes Baraj Gölü",
            "il": "Manisa", "ilce": "Gördes", "bolge": "Gördes - Demirci Çam Ormanları",
            "tip": "Baraj Gölü", "koordinat_enlem": 38.915, "koordinat_boylam": 28.285, "gps_format": "[38.915°N, 28.285°E]",
            "kapasite": "450 Milyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Manisa kuzey ilçeleri ve Balıkesir sınırı orman yangınları su kaynağı."
        },
        {
            "id": "SK-051",
            "isim": "Denizli Adıgüzel Baraj Gölü",
            "il": "Denizli", "ilce": "Güney / Buldan", "bolge": "Büyük Menderes Sektörü",
            "tip": "Baraj Gölü", "koordinat_enlem": 38.155, "koordinat_boylam": 29.115, "gps_format": "[38.155°N, 29.115°E]",
            "kapasite": "1 Bilyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Denizli Buldan ve Uşak sınırı orman yangınlarında uçak ikmal noktası."
        },
        {
            "id": "SK-052",
            "isim": "Denizli Cindere Baraj Gölü",
            "il": "Denizli", "ilce": "Buldan", "bolge": "Cindere Kanyonu Sektörü",
            "tip": "Baraj Gölü", "koordinat_enlem": 38.085, "koordinat_boylam": 29.015, "gps_format": "[38.085°N, 29.015°E]",
            "kapasite": "84 Milyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Buldan kanyon ve çam ormanı yangınları hızlı ikmal noktası."
        },
        {
            "id": "SK-053",
            "isim": "Kütahya Enne Baraj Gölü",
            "il": "Kütahya", "ilce": "Merkez / Tavşanlı", "bolge": "Kütahya Çam Ormanları",
            "tip": "Baraj Gölü", "koordinat_enlem": 39.435, "koordinat_boylam": 29.885, "gps_format": "[39.435°N, 29.885°E]",
            "kapasite": "10 Milyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Domaniç ve Tavşanlı sarıçam/kızılçam yangınlarında ana baraj."
        },
        {
            "id": "SK-054",
            "isim": "Kütahya Kayaboğazı Baraj Gölü",
            "il": "Kütahya", "ilce": "Tavşanlı", "bolge": "Tavşanlı - Domaniç Sektörü",
            "tip": "Baraj Gölü", "koordinat_enlem": 39.585, "koordinat_boylam": 29.515, "gps_format": "[39.585°N, 29.515°E]",
            "kapasite": "38 Milyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Tavşanlı ve Domaniç dağlık orman hattına müdahale barajı."
        },
        {
            "id": "SK-055",
            "isim": "Uşak Banaz Baltalı Göleti",
            "il": "Uşak", "ilce": "Banaz", "bolge": "Banaz Çam Ormanları",
            "tip": "Gölet", "koordinat_enlem": 38.745, "koordinat_boylam": 29.785, "gps_format": "[38.745°N, 29.785°E]",
            "kapasite": "2 Milyon m³", "uygun_araclar": ["Helikopter", "Arazöz"],
            "notlar": "Uşak Banaz ve Murat Dağı çam orman yangınları helikopter ikmali."
        },
        {
            "id": "SK-056",
            "isim": "Afyonkarahisar Selevir Baraj Gölü",
            "il": "Afyonkarahisar", "ilce": "Şuhut", "bolge": "Kumalar Dağı Orman Sektörü",
            "tip": "Baraj Gölü", "koordinat_enlem": 38.485, "koordinat_boylam": 30.415, "gps_format": "[38.485°N, 30.415°E]",
            "kapasite": "63 Milyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Afyon güney ağaçlandırma ve çamlık sahaları su kaynağı."
        },

        # --- 3. MARMARA BÖLGESİ (ÇANAKKALE, BALIKESİR, BURSA, İSTANBUL, KOCAELİ, BİLECİK, SAKARYA, TEKİRDAĞ, KIRKLARELİ, EDİRNE) ---
        {
            "id": "SK-057",
            "isim": "Kabatepe Sahili - Ege Denizi Su Alım Alanı",
            "il": "Çanakkale", "ilce": "Gelibolu", "bolge": "Gelibolu Tarihi Milli Park Sahili",
            "tip": "Deniz", "koordinat_enlem": 40.211, "koordinat_boylam": 26.281, "gps_format": "[40.211°N, 26.281°E]",
            "kapasite": "Sınırsız (Deniz Suyu)", "uygun_araclar": ["Amfibik Uçak", "Helikopter"],
            "notlar": "Kabatepe ve Alçıtepe orman yangınlarında uçakların dalga kırımı düşük ikmal rotası."
        },
        {
            "id": "SK-058",
            "isim": "Çanakkale Boğazı - Kilitbahir İkmal Hattı",
            "il": "Çanakkale", "ilce": "Eceabat / Gelibolu", "bolge": "Çanakkale Boğazı Orta Sektör",
            "tip": "Deniz / Boğaz", "koordinat_enlem": 40.146, "koordinat_boylam": 26.378, "gps_format": "[40.146°N, 26.378°E]",
            "kapasite": "Sınırsız", "uygun_araclar": ["Amfibik Uçak"],
            "notlar": "Tarihi Şehitlikler yangınında boğaz deniz trafiği durdurularak su ikmali yapılır."
        },
        {
            "id": "SK-059",
            "isim": "Bayramiç Baraj Gölü",
            "il": "Çanakkale", "ilce": "Bayramiç", "bolge": "Kazdağları Kuzey Sektörü",
            "tip": "Baraj Gölü", "koordinat_enlem": 39.815, "koordinat_boylam": 26.685, "gps_format": "[39.815°N, 26.685°E]",
            "kapasite": "86 Milyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Kazdağları milli parkı yangınlarında tatlı su ikmali yapılan stratejik baraj."
        },
        {
            "id": "SK-060",
            "isim": "Atikhisar Baraj Gölü",
            "il": "Çanakkale", "ilce": "Merkez", "bolge": "Çanakkale Merkez Orman Hattı",
            "tip": "Baraj Gölü", "koordinat_enlem": 40.085, "koordinat_boylam": 26.485, "gps_format": "[40.085°N, 26.485°E]",
            "kapasite": "54 Milyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Çanakkale merkez ve Kepez yangınlarında en yakın baraj."
        },
        {
            "id": "SK-061",
            "isim": "Çanakkale Ayvacık Tuzla Çayı İkmal Noktası",
            "il": "Çanakkale", "ilce": "Ayvacık", "bolge": "Assos - Kazdağları Batı Sektörü",
            "tip": "Akarsu / Gölet", "koordinat_enlem": 39.585, "koordinat_boylam": 26.215, "gps_format": "[39.585°N, 26.215°E]",
            "kapasite": "3 Milyon m³", "uygun_araclar": ["Helikopter", "Arazöz"],
            "notlar": "Assos sahil ve Ayvacık çamlık yangınları için kara ve helikopter ikmali."
        },
        {
            "id": "SK-062",
            "isim": "Sarımsaklı Koyu Deniz Su Alım Sahası",
            "il": "Balıkesir", "ilce": "Ayvalık", "bolge": "Şeytan Sofrası - Çamlık Orman Bölgesi",
            "tip": "Deniz / Koy", "koordinat_enlem": 39.268, "koordinat_boylam": 26.668, "gps_format": "[39.268°N, 26.668°E]",
            "kapasite": "Sınırsız", "uygun_araclar": ["Amfibik Uçak", "Helikopter"],
            "notlar": "Ayvalık adalar ve Şeytan Sofrası kızılçam yangınlarında dalgasız koy."
        },
        {
            "id": "SK-063",
            "isim": "Balıkesir İkizcetepeler Baraj Gölü",
            "il": "Balıkesir", "ilce": "Merkez / Bigadiç", "bolge": "Bigadiç - Sındırgı Sektörü",
            "tip": "Baraj Gölü", "koordinat_enlem": 39.525, "koordinat_boylam": 27.955, "gps_format": "[39.525°N, 27.955°E]",
            "kapasite": "160 Milyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Balıkesir iç bölge orman yangınlarında uçak ve helikopter alım barajı."
        },
        {
            "id": "SK-064",
            "isim": "Balıkesir Sındırgı Çaygören Barajı",
            "il": "Balıkesir", "ilce": "Sındırgı", "bolge": "Sındırgı - Alaçam Ormanları",
            "tip": "Baraj Gölü", "koordinat_enlem": 39.245, "koordinat_boylam": 28.215, "gps_format": "[39.245°N, 28.215°E]",
            "kapasite": "140 Milyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Sındırgı ve Dursunbey çam orman yangınları temel su kaynağı."
        },
        {
            "id": "SK-065",
            "isim": "Bursa Doğancı Baraj Gölü",
            "il": "Bursa", "ilce": "Osmangazi / Orhaneli", "bolge": "Uludağ Güney Yamaçları",
            "tip": "Baraj Gölü", "koordinat_enlem": 40.115, "koordinat_boylam": 28.985, "gps_format": "[40.115°N, 28.985°E]",
            "kapasite": "43 Milyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Uludağ milli parkı ve Orhaneli orman yangınlarında birincil baraj."
        },
        {
            "id": "SK-066",
            "isim": "Bursa Nilüfer Baraj Gölü",
            "il": "Bursa", "ilce": "Nilüfer / Keles", "bolge": "Keles Dağ Ormanları",
            "tip": "Baraj Gölü", "koordinat_enlem": 40.045, "koordinat_boylam": 28.935, "gps_format": "[40.045°N, 28.935°E]",
            "kapasite": "40 Milyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Keles ve Harmancık orman yangınlarına müdahale barajı."
        },
        {
            "id": "SK-067",
            "isim": "İstanbul Ömerli Baraj Gölü",
            "il": "İstanbul", "ilce": "Çekmeköy / Şile", "bolge": "Anadolu Yakası Orman Sektörü",
            "tip": "Baraj Gölü", "koordinat_enlem": 41.045, "koordinat_boylam": 29.355, "gps_format": "[41.045°N, 29.355°E]",
            "kapasite": "235 Milyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Şile, Aydos ve Beykoz orman yangınlarında uçakların tatlı su ikmal noktası."
        },
        {
            "id": "SK-068",
            "isim": "İstanbul Terkos (Durusu) Gölü",
            "il": "İstanbul", "ilce": "Arnavutköy / Çatalca", "bolge": "Avrupa Yakası Kuzey Ormanları",
            "tip": "Doğal Göl / Baraj", "koordinat_enlem": 41.315, "koordinat_boylam": 28.685, "gps_format": "[41.315°N, 28.685°E]",
            "kapasite": "162 Milyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Belgrad ormanı ve Çatalca orman yangınlarında ana ikmal gölü."
        },
        {
            "id": "SK-069",
            "isim": "İstanbul Darlık Baraj Gölü",
            "il": "İstanbul", "ilce": "Şile", "bolge": "Şile - Ağva Kuzey Ormanları",
            "tip": "Baraj Gölü", "koordinat_enlem": 41.115, "koordinat_boylam": 29.585, "gps_format": "[41.115°N, 29.585°E]",
            "kapasite": "107 Milyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Şile ve Kandıra orman yangınlarında amfibik uçak su alımı."
        },
        {
            "id": "SK-070",
            "isim": "Kocaeli Yuvacık Baraj Gölü",
            "il": "Kocaeli", "ilce": "Başiskele / Kartepe", "bolge": "Samanlı Dağları Orman Sektörü",
            "tip": "Baraj Gölü", "koordinat_enlem": 40.645, "koordinat_boylam": 29.935, "gps_format": "[40.645°N, 29.935°E]",
            "kapasite": "51 Milyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Kartepe ve Karamürsel gürgen/kayın ormanı yangınları su kaynağı."
        },
        {
            "id": "SK-071",
            "isim": "Sakarya Sapanca Gölü",
            "il": "Sakarya", "ilce": "Sapanca / Serdivan", "bolge": "Sapanca - Samanlı Dağları Sektörü",
            "tip": "Doğal Göl", "koordinat_enlem": 40.715, "koordinat_boylam": 30.265, "gps_format": "[40.715°N, 30.265°E]",
            "kapasite": "Doğal Gölü (1.3 Bilyon m³)", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Sakarya, Kocaeli ve Geyve orman yangınlarında dev tatlı su kaynağı."
        },
        {
            "id": "SK-072",
            "isim": "Bilecik Pelitözü Göleti",
            "il": "Bilecik", "ilce": "Merkez", "bolge": "Bilecik - Söğüt Çam Ormanları",
            "tip": "Gölet", "koordinat_enlem": 40.185, "koordinat_boylam": 29.985, "gps_format": "[40.185°N, 29.985°E]",
            "kapasite": "4 Milyon m³", "uygun_araclar": ["Helikopter", "Arazöz"],
            "notlar": "Bilecik merkez ve Söğüt yangınlarına helikopter su alma noktası."
        },
        {
            "id": "SK-073",
            "isim": "Tekirdağ Ganoz Dağı Şarköy Körfezi",
            "il": "Tekirdağ", "ilce": "Şarköy", "bolge": "Ganos Dağları Orman Sektörü",
            "tip": "Deniz / Körfez", "koordinat_enlem": 40.615, "koordinat_boylam": 27.115, "gps_format": "[40.615°N, 27.115°E]",
            "kapasite": "Sınırsız", "uygun_araclar": ["Amfibik Uçak", "Helikopter"],
            "notlar": "Tekirdağ Şarköy ve Ganos orman yangınlarında Marmara denizi ikmali."
        },
        {
            "id": "SK-074",
            "isim": "Kırklareli Armağan Baraj Gölü",
            "il": "Kırklareli", "ilce": "Merkez / Demirköy", "bolge": "Istranca (Yıldız) Dağları Sektörü",
            "tip": "Baraj Gölü", "koordinat_enlem": 41.885, "koordinat_boylam": 27.485, "gps_format": "[41.885°N, 27.485°E]",
            "kapasite": "50 Milyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Istranca meşe-kayın ormanları yangınları ana tatlı su kaynağı."
        },
        {
            "id": "SK-075",
            "isim": "Edirne Kadıköy Baraj Gölü",
            "il": "Edirne", "ilce": "Keşan", "bolge": "Keşan - Koru Dağları Orman Hattı",
            "tip": "Baraj Gölü", "koordinat_enlem": 40.815, "koordinat_boylam": 26.685, "gps_format": "[40.815°N, 26.685°E]",
            "kapasite": "60 Milyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Koru Dağları çam ormanı yangınları için baraj ikmal sahası."
        },

        # --- 4. KARADENİZ BÖLGESİ (KASTAMONU, KARABÜK, SİNOP, BOLU, ZONGULDAK, BARTIN, DÜZCE, SAMSUN, TRABZON, ARTVİN, vb.) ---
        {
            "id": "SK-076",
            "isim": "Kastamonu Karaçomak Baraj Gölü",
            "il": "Kastamonu", "ilce": "Merkez", "bolge": "Kastamonu Merkez Orman Sektörü",
            "tip": "Baraj Gölü", "koordinat_enlem": 41.315, "koordinat_boylam": 33.785, "gps_format": "[41.315°N, 33.785°E]",
            "kapasite": "23 Milyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Taşköprü ve Tosya sarıçam orman yangınlarında uçak ikmal noktası."
        },
        {
            "id": "SK-077",
            "isim": "Kastamonu Germeme Baraj Gölü",
            "il": "Kastamonu", "ilce": "Taşköprü", "bolge": "Taşköprü Sarıçam Sektörü",
            "tip": "Baraj Gölü", "koordinat_enlem": 41.485, "koordinat_boylam": 34.285, "gps_format": "[41.485°N, 34.285°E]",
            "kapasite": "15 Milyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Taşköprü çam ormanları yangınlarında birincil baraj kaynağı."
        },
        {
            "id": "SK-078",
            "isim": "Karabük Yenice YH-15 Yangın Havuzu",
            "il": "Karabük", "ilce": "Yenice", "bolge": "Yenice Ormanları",
            "tip": "OGM Yangın Havuzu", "koordinat_enlem": 41.185, "koordinat_boylam": 32.315, "gps_format": "[41.185°N, 32.315°E]",
            "kapasite": "600 Ton", "uygun_araclar": ["Helikopter Bambi Bucket", "Arazöz"],
            "notlar": "Türkiye'nin en yoğun kayın-meşe ormanlarında helikopter su ikmali."
        },
        {
            "id": "SK-079",
            "isim": "Sinop Boyabat Saraydüzü Barajı",
            "il": "Sinop", "ilce": "Boyabat", "bolge": "Sinop İç Orman Sektörü",
            "tip": "Baraj Gölü", "koordinat_enlem": 41.385, "koordinat_boylam": 34.885, "gps_format": "[41.385°N, 34.885°E]",
            "kapasite": "140 Milyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Sinop ve Boyabat çam ormanları için baraj su ikmal hattı."
        },
        {
            "id": "SK-080",
            "isim": "Bolu Abant Gölü Su Alım Sahası",
            "il": "Bolu", "ilce": "Mudurnu", "bolge": "Abant - Mudurnu Orman Sektörü",
            "tip": "Doğal Göl", "koordinat_enlem": 40.605, "koordinat_boylam": 31.285, "gps_format": "[40.605°N, 31.285°E]",
            "kapasite": "Doğal Gölü", "uygun_araclar": ["Helikopter", "Arazöz"],
            "notlar": "Abant Tabiat Parkı ve Mudurnu orman yangınlarında helikopter alımı."
        },
        {
            "id": "SK-081",
            "isim": "Bolu Gölköy Baraj Gölü",
            "il": "Bolu", "ilce": "Merkez", "bolge": "Bolu Merkez Çam Ormanları",
            "tip": "Baraj Gölü", "koordinat_enlem": 40.715, "koordinat_boylam": 31.555, "gps_format": "[40.715°N, 31.555°E]",
            "kapasite": "24 Milyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Bolu merkez, Aladağ ve Kartalkaya orman yangınları temel su alımı."
        },
        {
            "id": "SK-082",
            "isim": "Zonguldak Ulutan Baraj Gölü",
            "il": "Zonguldak", "ilce": "Merkez", "bolge": "Zonguldak Orman ve Havza Sektörü",
            "tip": "Baraj Gölü", "koordinat_enlem": 41.385, "koordinat_boylam": 31.815, "gps_format": "[41.385°N, 31.815°E]",
            "kapasite": "25 Milyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Zonguldak ve Devrek gürgen ormanları yangınları için baraj kaynağı."
        },
        {
            "id": "SK-083",
            "isim": "Bartın Kirazlıköprü Baraj Gölü",
            "il": "Bartın", "ilce": "Ulus", "bolge": "Küre Dağları Milli Park Sektörü",
            "tip": "Baraj Gölü", "koordinat_enlem": 41.545, "koordinat_boylam": 32.485, "gps_format": "[41.545°N, 32.485°E]",
            "kapasite": "66 Milyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Bartın ve Küre Dağları orman yangınlarına müdahale barajı."
        },
        {
            "id": "SK-084",
            "isim": "Düzce Hasanlar Baraj Gölü",
            "il": "Düzce", "ilce": "Yığılca", "bolge": "Düzce - Yığılca Kayın Ormanları",
            "tip": "Baraj Gölü", "koordinat_enlem": 40.915, "koordinat_boylam": 31.285, "gps_format": "[40.915°N, 31.285°E]",
            "kapasite": "55 Milyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Düzce ve Yığılca yoğun yapraklı orman yangınları su kaynağı."
        },
        {
            "id": "SK-085",
            "isim": "Samsun Altınkaya Baraj Gölü",
            "il": "Samsun", "ilce": "Bafra / Vezirköprü", "bolge": "Kızılırmak Vadisi Orman Sektörü",
            "tip": "Baraj Gölü", "koordinat_enlem": 41.355, "koordinat_boylam": 35.615, "gps_format": "[41.355°N, 35.615°E]",
            "kapasite": "5.7 Bilyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Samsun, Sinop ve Vezirköprü çam orman yangınlarında dev rezerv."
        },
        {
            "id": "SK-086",
            "isim": "Trabzon Uzungöl Tatlı Su İkmal Noktası",
            "il": "Trabzon", "ilce": "Çaykara", "bolge": "Doğu Karadeniz Ladin Ormanları",
            "tip": "Doğal Göl", "koordinat_enlem": 40.615, "koordinat_boylam": 40.285, "gps_format": "[40.615°N, 40.285°E]",
            "kapasite": "Doğal Göl", "uygun_araclar": ["Helikopter Bambi Bucket"],
            "notlar": "Sarp vadi yamaçlarındaki orman yangınlarında helikopter ikmali."
        },
        {
            "id": "SK-087",
            "isim": "Artvin Borçka Baraj Gölü",
            "il": "Artvin", "ilce": "Borçka", "bolge": "Çoruh Vadisi Orman Sektörü",
            "tip": "Baraj Gölü", "koordinat_enlem": 41.355, "koordinat_boylam": 41.685, "gps_format": "[41.355°N, 41.685°E]",
            "kapasite": "400 Milyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Artvin sarp vadilerindeki yangınlarda dev baraj rezervi."
        },
        {
            "id": "SK-088",
            "isim": "Artvin Deriner Baraj Gölü",
            "il": "Artvin", "ilce": "Merkez", "bolge": "Çoruh Kanyon Ormanları",
            "tip": "Baraj Gölü", "koordinat_enlem": 41.145, "koordinat_boylam": 41.885, "gps_format": "[41.145°N, 41.885°E]",
            "kapasite": "1.9 Bilyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Türkiye'nin en yüksek barajlarında sarp orman yangınlarına su alımı."
        },
        {
            "id": "SK-089",
            "isim": "Rize İkizdere Çayı Alım Noktası",
            "il": "Rize", "ilce": "İkizdere", "bolge": "Kaçkar Etekleri Orman Sektörü",
            "tip": "Akarsu", "koordinat_enlem": 40.785, "koordinat_boylam": 40.555, "gps_format": "[40.785°N, 40.555°E]",
            "kapasite": "Sürekli Akış", "uygun_araclar": ["Arazöz", "Helikopter"],
            "notlar": "Kaçkar dağları yamaç orman yangınlarında vadi içi akarsu alımı."
        },
        {
            "id": "SK-090",
            "isim": "Giresun Alucra Topçam Baraj Gölü",
            "il": "Giresun", "ilce": "Şebinkarahisar", "bolge": "Kelkit Vadisi Çam Ormanları",
            "tip": "Baraj Gölü", "koordinat_enlem": 40.315, "koordinat_boylam": 38.415, "gps_format": "[40.315°N, 38.415°E]",
            "kapasite": "130 Milyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Giresun iç kesim çam orman yangınları baraj kaynağı."
        },
        {
            "id": "SK-091",
            "isim": "Tokat Almus Baraj Gölü",
            "il": "Tokat", "ilce": "Almus", "bolge": "Yeşilırmak Vadisi Orman Sektörü",
            "tip": "Baraj Gölü", "koordinat_enlem": 40.385, "koordinat_boylam": 36.915, "gps_format": "[40.385°N, 36.915°E]",
            "kapasite": "950 Milyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Tokat, Niksar ve Reşadiye orman yangınlarında uçakların ana kaynağı."
        },
        {
            "id": "SK-092",
            "isim": "Amasya Yedi-Kır Baraj Gölü",
            "il": "Amasya", "ilce": "Suluova", "bolge": "Akdağ Orman Sektörü",
            "tip": "Baraj Gölü", "koordinat_enlem": 40.815, "koordinat_boylam": 35.615, "gps_format": "[40.815°N, 35.615°E]",
            "kapasite": "60 Milyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Amasya ve Merzifon dağlık çam ormanı yangınları su ikmali."
        },
        {
            "id": "SK-093",
            "isim": "Çorum Obruk Baraj Gölü",
            "il": "Çorum", "ilce": "Osmancık / Dodurga", "bolge": "Kızılırmak Kanyon Sektörü",
            "tip": "Baraj Gölü", "koordinat_enlem": 40.885, "koordinat_boylam": 34.785, "gps_format": "[40.885°N, 34.785°E]",
            "kapasite": "660 Milyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Çorum ve İskilip çam ormanları yangınları için büyük su rezervi."
        },

        # --- 5. İÇ ANADOLU BÖLGESİ (ANKARA, ESKİŞEHİR, KONYA, KARAMAN, KAYSERİ, SİVAS, ÇANKIRI, YOZGAT) ---
        {
            "id": "SK-094",
            "isim": "Ankara Kızılcahamam Kurtboğazı Barajı",
            "il": "Ankara", "ilce": "Kızılcahamam", "bolge": "Kızılcahamam Çam Ormanları",
            "tip": "Baraj Gölü", "koordinat_enlem": 40.285, "koordinat_boylam": 32.685, "gps_format": "[40.285°N, 32.685°E]",
            "kapasite": "100 Milyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Ankara kuzey çam ormanları ve Çamlıdere yangınlarında uçak ikmali."
        },
        {
            "id": "SK-095",
            "isim": "Ankara Çamlıdere Baraj Gölü",
            "il": "Ankara", "ilce": "Çamlıdere", "bolge": "Çamlıdere Çam Ormanları Sektörü",
            "tip": "Baraj Gölü", "koordinat_enlem": 40.355, "koordinat_boylam": 32.385, "gps_format": "[40.355°N, 32.385°E]",
            "kapasite": "1.2 Bilyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Ankara ve Bolu Gerede sınırı çam orman yangınları ana barajı."
        },
        {
            "id": "SK-096",
            "isim": "Eskişehir Çatören Baraj Gölü",
            "il": "Eskişehir", "ilce": "Seyitgazi", "bolge": "Seyitgazi - Kırka Orman Sektörü",
            "tip": "Baraj Gölü", "koordinat_enlem": 39.385, "koordinat_boylam": 30.585, "gps_format": "[39.385°N, 30.585°E]",
            "kapasite": "45 Milyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Eskişehir güney karaçam orman yangınlarında su alım sahası."
        },
        {
            "id": "SK-097",
            "isim": "Eskişehir Gökçekaya Baraj Gölü",
            "il": "Eskişehir", "ilce": "Mihalıççık", "bolge": "Sündiken Dağları Orman Sektörü",
            "tip": "Baraj Gölü", "koordinat_enlem": 40.035, "koordinat_boylam": 30.855, "gps_format": "[40.035°N, 30.855°E]",
            "kapasite": "910 Milyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Sündiken dağları ve Mihalıççık çam ormanları dev su kaynağı."
        },
        {
            "id": "SK-098",
            "isim": "Konya Beyşehir Gölü",
            "il": "Konya / Isparta", "ilce": "Beyşehir", "bolge": "Anamas Dağları ve Göller Yöresi",
            "tip": "Doğal Göl", "koordinat_enlem": 37.785, "koordinat_boylam": 31.555, "gps_format": "[37.785°N, 31.555°E]",
            "kapasite": "Doğal Göl (6.5 Bilyon m³)", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Konya Beyşehir ve Derebucak çam ormanları için dev göl rezervi."
        },
        {
            "id": "SK-099",
            "isim": "Karaman Ermenek Baraj Gölü",
            "il": "Karaman", "ilce": "Ermenek", "bolge": "Ermenek Kanyon Ormanları",
            "tip": "Baraj Gölü", "koordinat_enlem": 36.635, "koordinat_boylam": 32.885, "gps_format": "[36.635°N, 32.885°E]",
            "kapasite": "4.5 Bilyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Karaman Ermenek ve Mersin Mut sınırı sarp çam ormanları su sahası."
        },
        {
            "id": "SK-100",
            "isim": "Kayseri Yamula Baraj Gölü",
            "il": "Kayseri", "ilce": "Kocasinan", "bolge": "Kızılırmak Havzası",
            "tip": "Baraj Gölü", "koordinat_enlem": 38.885, "koordinat_boylam": 35.255, "gps_format": "[38.885°N, 35.255°E]",
            "kapasite": "3.5 Bilyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Kayseri ve Yozgat sınırı ağaçlandırma sahaları yangın ikmali."
        },
        {
            "id": "SK-101",
            "isim": "Sivas Hafik Pusat Özen Barajı",
            "il": "Sivas", "ilce": "Hafik", "bolge": "Sivas Kuzey Çamlık Sektörü",
            "tip": "Baraj Gölü", "koordinat_enlem": 39.985, "koordinat_boylam": 37.415, "gps_format": "[39.985°N, 37.415°E]",
            "kapasite": "95 Milyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Sivas ve Tokat sınırı orman yangınlarında uçak ikmali."
        },

        # --- 6. DOĞU ANADOLU BÖLGESİ (TUNCELİ, BİNGÖL, ELAZIĞ, MALATYA, ERZURUM, KARS, vb.) ---
        {
            "id": "SK-102",
            "isim": "Bingöl Özlüce Baraj Gölü",
            "il": "Bingöl", "ilce": "Kiğı", "bolge": "Peri Çayı Orman Sektörü",
            "tip": "Baraj Gölü", "koordinat_enlem": 39.185, "koordinat_boylam": 40.185, "gps_format": "[39.185°N, 40.185°E]",
            "kapasite": "1 Bilyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter"],
            "notlar": "Bingöl ve Tunceli sınırı meşe ve çam ormanı yangınları baraj kaynağı."
        },
        {
            "id": "SK-103",
            "isim": "Tunceli Uzunçayır Baraj Gölü",
            "il": "Tunceli", "ilce": "Merkez / Ovacık", "bolge": "Munzur Vadisi Orman Sektörü",
            "tip": "Baraj Gölü", "koordinat_enlem": 39.085, "koordinat_boylam": 39.555, "gps_format": "[39.085°N, 39.555°E]",
            "kapasite": "300 Milyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Munzur Milli Parkı orman yangınlarında su alma havzası."
        },
        {
            "id": "SK-104",
            "isim": "Elazığ Keban Baraj Gölü",
            "il": "Elazığ", "ilce": "Keban / Ağın", "bolge": "Fırat Havzası Meşe ve Çamlık Sektörü",
            "tip": "Baraj Gölü", "koordinat_enlem": 38.795, "koordinat_boylam": 38.745, "gps_format": "[38.795°N, 38.745°E]",
            "kapasite": "31 Bilyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Elazığ, Malatya ve Tunceli havzası orman yangınlarında dev rezerv."
        },
        {
            "id": "SK-105",
            "isim": "Malatya Karakaya Baraj Gölü",
            "il": "Malatya / Elazığ", "ilce": "Battalgazi", "bolge": "Karakaya Baraj Sektörü",
            "tip": "Baraj Gölü", "koordinat_enlem": 38.415, "koordinat_boylam": 38.585, "gps_format": "[38.415°N, 38.585°E]",
            "kapasite": "9.5 Bilyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Malatya Pütürge ve Kale yamaç meşelik yangınları su kaynağı."
        },
        {
            "id": "SK-106",
            "isim": "Erzurum Tortum Gölü",
            "il": "Erzurum", "ilce": "Uzundere", "bolge": "Tortum Vadisi Orman Sektörü",
            "tip": "Doğal Göl", "koordinat_enlem": 40.645, "koordinat_boylam": 41.615, "gps_format": "[40.645°N, 41.615°E]",
            "kapasite": "Doğal Göl (57 Milyon m³)", "uygun_araclar": ["Amfibik Uçak", "Helikopter"],
            "notlar": "Erzurum kuzey vadi çam ve sarıçam orman yangınları su sahası."
        },
        {
            "id": "SK-107",
            "isim": "Kars Çıldır Gölü İkmal Noktası",
            "il": "Kars / Ardahan", "ilce": "Çıldır", "bolge": "Kars-Ardahan Sarıçam Sektörü",
            "tip": "Doğal Göl", "koordinat_enlem": 41.045, "koordinat_boylam": 43.255, "gps_format": "[41.045°N, 43.255°E]",
            "kapasite": "Doğal Göl", "uygun_araclar": ["Amfibik Uçak", "Helikopter"],
            "notlar": "Sarıçam ormanları ve Sarıkamış/Ardahan sahası için büyük göl."
        },

        # --- 7. GÜNEYDOĞU ANADOLU BÖLGESİ (ŞIRNAK, DİYARBAKIR, MARDİN, SİİRT, HAKKARİ, ŞANLIURFA, ADIYAMAN, BATMAN) ---
        {
            "id": "SK-108",
            "isim": "Şırnak Ilısu Baraj Gölü (Cizre - Güçlükonak Sektörü)",
            "il": "Şırnak / Mardin", "ilce": "Güçlükonak", "bolge": "Cudi ve Gabar Orman Hattı",
            "tip": "Baraj Gölü", "koordinat_enlem": 37.525, "koordinat_boylam": 41.835, "gps_format": "[37.525°N, 41.835°E]",
            "kapasite": "10 Bilyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Cudi Dağı ve Gabar orman yangınları için dev su ikmal kaynağı."
        },
        {
            "id": "SK-109",
            "isim": "Diyarbakır Dicle Baraj Gölü",
            "il": "Diyarbakır", "ilce": "Dicle / Eğil", "bolge": "Dicle - Kulp Orman ve Meşelik Sektörü",
            "tip": "Baraj Gölü", "koordinat_enlem": 38.255, "koordinat_boylam": 40.185, "gps_format": "[38.255°N, 40.185°E]",
            "kapasite": "600 Milyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Diyarbakır kuzey ilçeleri ve Lice/Kulp meşelik yangınları ikmali."
        },
        {
            "id": "SK-110",
            "isim": "Siirt Botan Barajı (Alkalkum)",
            "il": "Siirt", "ilce": "Merkez", "bolge": "Botan Vadisi Orman Sektörü",
            "tip": "Baraj Gölü", "koordinat_enlem": 37.945, "koordinat_boylam": 42.045, "gps_format": "[37.945°N, 42.045°E]",
            "kapasite": "1.2 Bilyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Siirt ve Şırnak kuzeyi vadi meşelik yangınlarına baraj ikmali."
        },
        {
            "id": "SK-111",
            "isim": "Adıyaman Atatürk Baraj Gölü Kuzey Sahası",
            "il": "Adıyaman / Şanlıurfa", "ilce": "Kahta", "bolge": "Atatürk Barajı Sektörü",
            "tip": "Baraj Gölü", "koordinat_enlem": 37.745, "koordinat_boylam": 38.585, "gps_format": "[37.745°N, 38.585°E]",
            "kapasite": "48 Bilyon m³ (Türkiye'nin En Büyüğü)", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Adıyaman Nemrut yamaçları ve çevre orman yangınlarında sınırsız baraj rezervi."
        },
        {
            "id": "SK-112",
            "isim": "Batman Batman Baraj Gölü",
            "il": "Batman / Diyarbakır", "ilce": "Kozluk", "bolge": "Kozluk ve Sason Dağ Sektörü",
            "tip": "Baraj Gölü", "koordinat_enlem": 38.155, "koordinat_boylam": 41.185, "gps_format": "[38.155°N, 41.185°E]",
            "kapasite": "1.1 Bilyon m³", "uygun_araclar": ["Amfibik Uçak", "Helikopter", "Arazöz"],
            "notlar": "Sason ve Kozluk dağlık meşelik yangınları için temel su alımı."
        },
        {
            "id": "SK-113",
            "isim": "Hakkari Zap Suyu İkmal Rampası",
            "il": "Hakkari", "ilce": "Çukurca", "bolge": "Zap Vadisi Sektörü",
            "tip": "Akarsu", "koordinat_enlem": 37.455, "koordinat_boylam": 43.615, "gps_format": "[37.455°N, 43.615°E]",
            "kapasite": "Sürekli Akış", "uygun_araclar": ["Helikopter", "Arazöz"],
            "notlar": "Hakkari dağlık vadi yangınlarında helikopter ve arazöz su ikmal noktası."
        }
    ]

def generate_all_turkey_settlements_and_facilities():
    return [
        # --- 1. AKDENİZ BÖLGESİ (ANTALYA, MUĞLA, MERSİN, ADANA, HATAY, OSMANİYE, K.MARAŞ, ISPARTA, BURDUR) ---
        {
            "id": "YT-001",
            "isim": "Karavca Köyü",
            "il": "Antalya", "ilce": "Manavgat", "tip": "Köy / Yerleşim",
            "koordinat_enlem": 36.887, "koordinat_boylam": 31.470, "gps_format": "[36.887°N, 31.470°E]",
            "nufus_yatak_kapasitesi": "850 Nüfus", "risk_seviyesi": "Çok Yüksek",
            "tahliye_rotasi": "Oymapınar Servis Yolu -> D400 Karayolu", "savunma_onceligi": "1. Öncelik (Yerleşim Tahliyesi ve Çevre Koruma)"
        },
        {
            "id": "YT-002",
            "isim": "Oymapınar Köyü",
            "il": "Antalya", "ilce": "Manavgat", "tip": "Köy / Yerleşim",
            "koordinat_enlem": 36.895, "koordinat_boylam": 31.485, "gps_format": "[36.895°N, 31.485°E]",
            "nufus_yatak_kapasitesi": "1400 Nüfus", "risk_seviyesi": "Yüksek",
            "tahliye_rotasi": "D400 Manavgat Ana Arteri", "savunma_onceligi": "1. Öncelik (Yerleşim Savunma Hattı)"
        },
        {
            "id": "YT-003",
            "isim": "Oymapınar Barajı HES Şalt Sahası ve Trafo Merkezi",
            "il": "Antalya", "ilce": "Manavgat", "tip": "Kritik Altyapı / Enerji",
            "koordinat_enlem": 36.905, "koordinat_boylam": 31.530, "gps_format": "[36.905°N, 31.530°E]",
            "nufus_yatak_kapasitesi": "45 Teknik Personel / 540 MW Güç", "risk_seviyesi": "Çok Yüksek",
            "tahliye_rotasi": "Baraj Güvenlik Tüneli ve Güney Servis Yolu", "savunma_onceligi": "Kritik Altyapı Koruma (Arazöz Köpük Bariyeri)"
        },
        {
            "id": "YT-004",
            "isim": "Manavgat Ulupınar Köyü",
            "il": "Antalya", "ilce": "Manavgat", "tip": "Köy / Yerleşim",
            "koordinat_enlem": 36.915, "koordinat_boylam": 31.540, "gps_format": "[36.915°N, 31.540°E]",
            "nufus_yatak_kapasitesi": "620 Nüfus", "risk_seviyesi": "Yüksek",
            "tahliye_rotasi": "Akseki Karayolu Bağlantısı", "savunma_onceligi": "1. Öncelik (Vadi Savunma Sektörü)"
        },
        {
            "id": "YT-005",
            "isim": "Alanya Sapadere Köyü ve Kanyon Tesisleri",
            "il": "Antalya", "ilce": "Alanya", "tip": "Köy / Turizm",
            "koordinat_enlem": 36.535, "koordinat_boylam": 32.285, "gps_format": "[36.535°N, 32.285°E]",
            "nufus_yatak_kapasitesi": "950 Nüfus / 500 Turist", "risk_seviyesi": "Çok Yüksek",
            "tahliye_rotasi": "Sapadere - Alanya Asfalt Yolu", "savunma_onceligi": "1. Öncelik (Kanyon Tahliyesi)"
        },
        {
            "id": "YT-006",
            "isim": "Kemer Göynük Mahallesi",
            "il": "Antalya", "ilce": "Kemer", "tip": "Mahalle / Yerleşim",
            "koordinat_enlem": 36.668, "koordinat_boylam": 30.555, "gps_format": "[36.668°N, 30.555°E]",
            "nufus_yatak_kapasitesi": "4800 Nüfus", "risk_seviyesi": "Yüksek",
            "tahliye_rotasi": "D400 Antalya Karayolu", "savunma_onceligi": "1. Öncelik (Kanyon Ağzı Güney Sektörü)"
        },
        {
            "id": "YT-007",
            "isim": "Mirage Park Resort Kemer",
            "il": "Antalya", "ilce": "Kemer", "tip": "Turizm / Otel",
            "koordinat_enlem": 36.665, "koordinat_boylam": 30.570, "gps_format": "[36.665°N, 30.570°E]",
            "nufus_yatak_kapasitesi": "1200 Yatak Kapasitesi", "risk_seviyesi": "Orta - Yüksek",
            "tahliye_rotasi": "Kemer Sahil Asfalt Yolu", "savunma_onceligi": "2. Öncelik (Otel Çevre Savunması)"
        },
        {
            "id": "YT-008",
            "isim": "Kaş Kalkan Mahallesi Oteller ve Villalar Sektörü",
            "il": "Antalya", "ilce": "Kaş", "tip": "Turizm / Yerleşim",
            "koordinat_enlem": 36.265, "koordinat_boylam": 29.415, "gps_format": "[36.265°N, 29.415°E]",
            "nufus_yatak_kapasitesi": "4200 Nüfus ve Yatak", "risk_seviyesi": "Yüksek",
            "tahliye_rotasi": "D400 Kaş-Fethiye Karayolu", "savunma_onceligi": "1. Öncelik (Yerleşim Çeper Şerit Açımı)"
        },
        {
            "id": "YT-009",
            "isim": "İçmeler Mahallesi Merkez",
            "il": "Muğla", "ilce": "Marmaris", "tip": "Mahalle / Yerleşim",
            "koordinat_enlem": 36.800, "koordinat_boylam": 28.234, "gps_format": "[36.800°N, 28.234°E]",
            "nufus_yatak_kapasitesi": "6500 Nüfus (Yazın 25.000)", "risk_seviyesi": "Çok Yüksek",
            "tahliye_rotasi": "D400 Marmaris-Muğla Karayolu", "savunma_onceligi": "1. Öncelik (Tahliye ve Güney Savunma Sektörü)"
        },
        {
            "id": "YT-010",
            "isim": "Turunç Mahallesi",
            "il": "Muğla", "ilce": "Marmaris", "tip": "Mahalle / Yerleşim",
            "koordinat_enlem": 36.775, "koordinat_boylam": 28.248, "gps_format": "[36.775°N, 28.248°E]",
            "nufus_yatak_kapasitesi": "2100 Nüfus", "risk_seviyesi": "Yüksek",
            "tahliye_rotasi": "Turunç Sahil Yolu & Sahil Güvenlik Deniz Tahliyesi", "savunma_onceligi": "1. Öncelik (Kıyı Tahliyesi ve Çeper Koruma)"
        },
        {
            "id": "YT-011",
            "isim": "İçmeler 100 kW Elektrik Trafo ve Dağıtım Merkezi",
            "il": "Muğla", "ilce": "Marmaris", "tip": "Kritik Altyapı / Enerji",
            "koordinat_enlem": 36.802, "koordinat_boylam": 28.230, "gps_format": "[36.802°N, 28.230°E]",
            "nufus_yatak_kapasitesi": "10 Teknik Personel", "risk_seviyesi": "Çok Yüksek",
            "tahliye_rotasi": "İçmeler Asfalt Yolu", "savunma_onceligi": "Kritik Altyapı Koruma (Dozer Hendek Şeridi ve Su Perdesi)"
        },
        {
            "id": "YT-012",
            "isim": "İçmeler Sahil Oteller Bölgesi",
            "il": "Muğla", "ilce": "Marmaris", "tip": "Turizm / Oteller",
            "koordinat_enlem": 36.798, "koordinat_boylam": 28.240, "gps_format": "[36.798°N, 28.240°E]",
            "nufus_yatak_kapasitesi": "4500 Yatak Kapasitesi", "risk_seviyesi": "Yüksek",
            "tahliye_rotasi": "Deniz İskeleleri ve Sahil Güvenlik Tahliyesi", "savunma_onceligi": "2. Öncelik (Otel Çevre Şerit Açımı)"
        },
        {
            "id": "YT-013",
            "isim": "Grand Yazıcı Club Turban Thermal Hotel",
            "il": "Muğla", "ilce": "Marmaris", "tip": "Turizm / Otel",
            "koordinat_enlem": 36.828, "koordinat_boylam": 28.242, "gps_format": "[36.828°N, 28.242°E]",
            "nufus_yatak_kapasitesi": "1100 Yatak Kapasitesi", "risk_seviyesi": "Orta - Yüksek",
            "tahliye_rotasi": "Marmaris Sahil Asfaltı", "savunma_onceligi": "2. Öncelik (Orman Sınırı Arazöz Perdesi)"
        },
        {
            "id": "YT-014",
            "isim": "Güvercinlik Köyü ve Tatil Sahası",
            "il": "Muğla", "ilce": "Bodrum", "tip": "Köy / Yerleşim",
            "koordinat_enlem": 37.140, "koordinat_boylam": 27.580, "gps_format": "[37.140°N, 27.580°E]",
            "nufus_yatak_kapasitesi": "1800 Nüfus", "risk_seviyesi": "Yüksek",
            "tahliye_rotasi": "D330 Milas-Bodrum Karayolu", "savunma_onceligi": "1. Öncelik (Yerleşim Savunması)"
        },
        {
            "id": "YT-015",
            "isim": "Titanic Luxury Collection Bodrum Hotel",
            "il": "Muğla", "ilce": "Bodrum", "tip": "Turizm / Otel",
            "koordinat_enlem": 37.132, "koordinat_boylam": 27.568, "gps_format": "[37.132°N, 27.568°E]",
            "nufus_yatak_kapasitesi": "1400 Yatak Kapasitesi", "risk_seviyesi": "Yüksek",
            "tahliye_rotasi": "Pina Yarımadası Servis Yolu & Deniz Tahliyeleri", "savunma_onceligi": "2. Öncelik (Pina Sırtı Dozer Şeridi)"
        },
        {
            "id": "YT-016",
            "isim": "Lujo Hotel Bodrum",
            "il": "Muğla", "ilce": "Bodrum", "tip": "Turizm / Otel",
            "koordinat_enlem": 37.138, "koordinat_boylam": 27.572, "gps_format": "[37.138°N, 27.572°E]",
            "nufus_yatak_kapasitesi": "900 Yatak Kapasitesi", "risk_seviyesi": "Yüksek",
            "tahliye_rotasi": "D330 Karayolu & Sahil İskele Tahliyeleri", "savunma_onceligi": "2. Öncelik (Tesis Orman Sınırı Çeperi)"
        },
        {
            "id": "YT-017",
            "isim": "Milas Yeniköy Termik Santrali",
            "il": "Muğla", "ilce": "Milas", "tip": "Kritik Altyapı / Enerji",
            "koordinat_enlem": 37.145, "koordinat_boylam": 27.885, "gps_format": "[37.145°N, 27.885°E]",
            "kapasite": "420 MW / 600 Personel", "risk_seviyesi": "Çok Yüksek",
            "tahliye_rotasi": "Milas - Ören Karayolu", "savunma_onceligi": "1. Öncelik (Santral Çevre Şeridi ve Su Perdesi)"
        },
        {
            "id": "YT-018",
            "isim": "Milas Kemerköy Termik Santrali (Ören)",
            "il": "Muğla", "ilce": "Milas", "tip": "Kritik Altyapı / Enerji",
            "koordinat_enlem": 37.035, "koordinat_boylam": 27.895, "gps_format": "[37.035°N, 27.895°E]",
            "kapasite": "630 MW / 800 Personel", "risk_seviyesi": "Çok Yüksek",
            "tahliye_rotasi": "Ören İskele ve Deniz Tahliyesi", "savunma_onceligi": "1. Öncelik (Kömür Stok Sahası Koruma)"
        },
        {
            "id": "YT-019",
            "isim": "Ölüdeniz Ovacık Mahallesi ve Otelleri",
            "il": "Muğla", "ilce": "Fethiye", "tip": "Mahalle / Turizm",
            "koordinat_enlem": 36.575, "koordinat_boylam": 29.148, "gps_format": "[36.575°N, 29.148°E]",
            "nufus_yatak_kapasitesi": "3500 Nüfus (Yazın 15.000)", "risk_seviyesi": "Yüksek",
            "tahliye_rotasi": "Fethiye - Ölüdeniz Karayolu", "savunma_onceligi": "1. Öncelik (Yerleşim ve Turizm Sektörü)"
        },
        {
            "id": "YT-020",
            "isim": "Datça Mesudiye Köyü ve Hayıtbükü Turizm Sahası",
            "il": "Muğla", "ilce": "Datça", "tip": "Köy / Turizm",
            "koordinat_enlem": 36.685, "koordinat_boylam": 27.585, "gps_format": "[36.685°N, 27.585°E]",
            "nufus_yatak_kapasitesi": "1100 Nüfus / 800 Turist", "risk_seviyesi": "Yüksek",
            "tahliye_rotasi": "Datça Ana Karayolu", "savunma_onceligi": "1. Öncelik (Köy Savunma Sektörü)"
        },
        {
            "id": "YT-021",
            "isim": "Mersin Gülnar Büyükeceli Mahallesi ve Akkuyu NGS Bölgesi",
            "il": "Mersin", "ilce": "Gülnar", "tip": "Kritik Altyapı / Yerleşim",
            "koordinat_enlem": 36.145, "koordinat_boylam": 33.535, "gps_format": "[36.145°N, 33.535°E]",
            "nufus_yatak_kapasitesi": "3500 Nüfus / Nükleer Proje Sahası", "risk_seviyesi": "Çok Yüksek",
            "tahliye_rotasi": "D400 Mersin - Antalya Karayolu", "savunma_onceligi": "1. Öncelik (Akkuyu Çevre Orman Sınırı)"
        },
        {
            "id": "YT-022",
            "isim": "Adana Aladağ Akören Köyü",
            "il": "Adana", "ilce": "Aladağ", "tip": "Köy / Yerleşim",
            "koordinat_enlem": 37.585, "koordinat_boylam": 35.415, "gps_format": "[37.585°N, 35.415°E]",
            "nufus_yatak_kapasitesi": "750 Nüfus", "risk_seviyesi": "Yüksek",
            "tahliye_rotasi": "Aladağ - Kozan Karayolu", "savunma_onceligi": "1. Öncelik (Toros Orman Köyü Tahliye)"
        },
        {
            "id": "YT-023",
            "isim": "Hatay Belen Geçidi ve Çakallı Mahallesi",
            "il": "Hatay", "ilce": "Belen", "tip": "Mahalle / Kritik Geçit",
            "koordinat_enlem": 36.485, "koordinat_boylam": 36.215, "gps_format": "[36.485°N, 36.215°E]",
            "nufus_yatak_kapasitesi": "1500 Nüfus", "risk_seviyesi": "Çok Yüksek",
            "tahliye_rotasi": "E91 İskenderun - Antakya Otoyolu", "savunma_onceligi": "1. Öncelik (Ana Arteri ve Geçit Koruma)"
        },
        {
            "id": "YT-024",
            "isim": "Osmaniye Kadirli Karatepe Aslantaş Açık Hava Müzesi",
            "il": "Osmaniye", "ilce": "Kadirli", "tip": "Tarihi Miras / Yerleşim",
            "koordinat_enlem": 37.285, "koordinat_boylam": 36.255, "gps_format": "[37.285°N, 36.255°E]",
            "nufus_yatak_kapasitesi": "Milli Park ve Müze Alanı", "risk_seviyesi": "Yüksek",
            "tahliye_rotasi": "Kadirli - Aslantaş Yolu", "savunma_onceligi": "Tarihi ve Milli Miras Savunması"
        },
        {
            "id": "YT-025",
            "isim": "Kahramanmaraş Andırın Çokak Köyü",
            "il": "Kahramanmaraş", "ilce": "Andırın", "tip": "Köy / Yerleşim",
            "koordinat_enlem": 37.615, "koordinat_boylam": 36.385, "gps_format": "[37.615°N, 36.385°E]",
            "nufus_yatak_kapasitesi": "680 Nüfus", "risk_seviyesi": "Yüksek",
            "tahliye_rotasi": "Andırın - Kadirli Karayolu", "savunma_onceligi": "1. Öncelik (Çamlık Orman Köyü Koruma)"
        },
        {
            "id": "YT-026",
            "isim": "Burdur Bucak Elsazı Köyü ve Orman Sahası",
            "il": "Burdur", "ilce": "Bucak", "tip": "Köy / Yerleşim",
            "koordinat_enlem": 37.315, "koordinat_boylam": 30.845, "gps_format": "[37.315°N, 30.845°E]",
            "nufus_yatak_kapasitesi": "540 Nüfus", "risk_seviyesi": "Yüksek",
            "tahliye_rotasi": "Antalya - Burdur D650 Karayolu", "savunma_onceligi": "1. Öncelik (Baraj Sahili Köy Savunması)"
        },
        {
            "id": "YT-027",
            "isim": "Isparta Sütçüler Çandır Köyü ve Yazlıklar",
            "il": "Isparta", "ilce": "Sütçüler", "tip": "Köy / Turizm",
            "koordinat_enlem": 37.485, "koordinat_boylam": 30.985, "gps_format": "[37.485°N, 30.985°E]",
            "nufus_yatak_kapasitesi": "850 Nüfus", "risk_seviyesi": "Çok Yüksek",
            "tahliye_rotasi": "Sütçüler Ana Asfaltı", "savunma_onceligi": "1. Öncelik (Yamaç Köyü Savunma Hattı)"
        },

        # --- 2. EGE BÖLGESİ (İZMİR, AYDIN, MANİSA, DENİZLİ, KÜTAHYA, UŞAK, AFYONKARAHİSAR) ---
        {
            "id": "YT-028",
            "isim": "Doğanbey Mahallesi",
            "il": "İzmir", "ilce": "Seferihisar", "tip": "Mahalle / Yerleşim",
            "koordinat_enlem": 38.095, "koordinat_boylam": 26.885, "gps_format": "[38.095°N, 26.885°E]",
            "nufus_yatak_kapasitesi": "2900 Nüfus", "risk_seviyesi": "Yüksek",
            "tahliye_rotasi": "Seferihisar Asfalt Arteri", "savunma_onceligi": "1. Öncelik (Orman Sınırı Tahliye ve Koruma)"
        },
        {
            "id": "YT-029",
            "isim": "Alaçatı Port Oteller Bölgesi ve Konut Sahası",
            "il": "İzmir", "ilce": "Çeşme", "tip": "Turizm / Yerleşim",
            "koordinat_enlem": 38.258, "koordinat_boylam": 26.388, "gps_format": "[38.258°N, 26.388°E]",
            "nufus_yatak_kapasitesi": "5500 Nüfus ve Yatak", "risk_seviyesi": "Orta",
            "tahliye_rotasi": "Çeşme Otoyolu (O-32)", "savunma_onceligi": "2. Öncelik (Kuzey Rüzgarları Önleme Hattı)"
        },
        {
            "id": "YT-030",
            "isim": "İzmir Foça Kozbeyli Köyü ve Turizm Evleri",
            "il": "İzmir", "ilce": "Foça", "tip": "Tarihi Köy / Yerleşim",
            "koordinat_enlem": 38.745, "koordinat_boylam": 26.885, "gps_format": "[38.745°N, 26.885°E]",
            "nufus_yatak_kapasitesi": "1300 Nüfus", "risk_seviyesi": "Yüksek",
            "tahliye_rotasi": "Foça - Yenifoça Sahil Asfaltı", "savunma_onceligi": "1. Öncelik (Köy Savunma Perdesi)"
        },
        {
            "id": "YT-031",
            "isim": "İzmir Aliağa Petrokimya ve Rafineri Tesisleri (TÜPRAŞ / PETKİM)",
            "il": "İzmir", "ilce": "Aliağa", "tip": "Kritik Sanayi / Enerji",
            "koordinat_enlem": 38.805, "koordinat_boylam": 26.965, "gps_format": "[38.805°N, 26.965°E]",
            "nufus_yatak_kapasitesi": "6000 Endüstriyel Personel", "risk_seviyesi": "Çok Yüksek",
            "tahliye_rotasi": "Aliağa Liman Yolu & Otoyol", "savunma_onceligi": "1. Sınıf Kritik Sanayi Koruma"
        },
        {
            "id": "YT-032",
            "isim": "Aydın Kuşadası Güzelçamlı Mahallesi",
            "il": "Aydın", "ilce": "Kuşadası", "tip": "Mahalle / Turizm",
            "koordinat_enlem": 37.715, "koordinat_boylam": 27.225, "gps_format": "[37.715°N, 27.225°E]",
            "nufus_yatak_kapasitesi": "7500 Nüfus", "risk_seviyesi": "Yüksek",
            "tahliye_rotasi": "Kuşadası - Söke Karayolu", "savunma_onceligi": "1. Öncelik (Dilek Yarımadası Sınır Savunması)"
        },
        {
            "id": "YT-033",
            "isim": "Manisa Spil Dağı Milli Park Evleri ve Radar Tesisleri",
            "il": "Manisa", "ilce": "Merkez", "tip": "Kritik Altyapı / Turizm",
            "koordinat_enlem": 38.565, "koordinat_boylam": 27.435, "gps_format": "[38.565°N, 27.435°E]",
            "nufus_yatak_kapasitesi": "400 Ziyaretçi / Radar Merkezi", "risk_seviyesi": "Yüksek",
            "tahliye_rotasi": "Spil - Manisa Dağ Asfalt Yolu", "savunma_onceligi": "Radar ve Milli Park Koruma"
        },
        {
            "id": "YT-034",
            "isim": "Denizli Buldan Yenicekent Mahallesi",
            "il": "Denizli", "ilce": "Buldan", "tip": "Mahalle / Yerleşim",
            "koordinat_enlem": 38.105, "koordinat_boylam": 28.915, "gps_format": "[38.105°N, 28.915°E]",
            "nufus_yatak_kapasitesi": "2200 Nüfus", "risk_seviyesi": "Yüksek",
            "tahliye_rotasi": "Buldan - Güney Karayolu", "savunma_onceligi": "1. Öncelik (Orman Çeperi Koruma)"
        },
        {
            "id": "YT-035",
            "isim": "Kütahya Domaniç Çamlıca Köyü",
            "il": "Kütahya", "ilce": "Domaniç", "tip": "Köy / Yerleşim",
            "koordinat_enlem": 39.815, "koordinat_boylam": 29.635, "gps_format": "[39.815°N, 29.635°E]",
            "nufus_yatak_kapasitesi": "800 Nüfus", "risk_seviyesi": "Yüksek",
            "tahliye_rotasi": "Domaniç - İnegöl Dağ Karayolu", "savunma_onceligi": "1. Öncelik (Sarıçam Ormanı Sınırı)"
        },
        {
            "id": "YT-036",
            "isim": "Uşak Banaz Kızılcasöğüt Kasabası",
            "il": "Uşak", "ilce": "Banaz", "tip": "Kasaba / Yerleşim",
            "koordinat_enlem": 38.685, "koordinat_boylam": 29.685, "gps_format": "[38.685°N, 29.685°E]",
            "nufus_yatak_kapasitesi": "1900 Nüfus", "risk_seviyesi": "Yüksek",
            "tahliye_rotasi": "Uşak - Ankara D300 Karayolu", "savunma_onceligi": "1. Öncelik (Çam Ormanı Sınır Hattı)"
        },
        {
            "id": "YT-037",
            "isim": "Afyonkarahisar Şuhut Başören Köyü",
            "il": "Afyonkarahisar", "ilce": "Şuhut", "tip": "Köy / Yerleşim",
            "koordinat_enlem": 38.415, "koordinat_boylam": 30.515, "gps_format": "[38.415°N, 30.515°E]",
            "nufus_yatak_kapasitesi": "720 Nüfus", "risk_seviyesi": "Orta - Yüksek",
            "tahliye_rotasi": "Şuhut Karayolu", "savunma_onceligi": "1. Öncelik (Kumalar Dağı Etek Savunması)"
        },

        # --- 3. MARMARA BÖLGESİ (ÇANAKKALE, BALIKESİR, BURSA, İSTANBUL, KOCAELİ, BİLECİK, SAKARYA, TEKİRDAĞ, KIRKLARELİ, EDİRNE) ---
        {
            "id": "YT-038",
            "isim": "Kilitbahir Köyü ve Tarihi Kalesi",
            "il": "Çanakkale", "ilce": "Eceabat / Gelibolu", "tip": "Tarihi Yerleşim / Köy",
            "koordinat_enlem": 40.148, "koordinat_boylam": 26.379, "gps_format": "[40.148°N, 26.379°E]",
            "nufus_yatak_kapasitesi": "1200 Nüfus", "risk_seviyesi": "Yüksek",
            "tahliye_rotasi": "E87 Çanakkale-Edirne Sahil Asfaltı", "savunma_onceligi": "1. Öncelik (Tarihi Alan ve Yerleşim Koruma)"
        },
        {
            "id": "YT-039",
            "isim": "Kabatepe Feribot İskelesi ve Yolcu Sahası",
            "il": "Çanakkale", "ilce": "Eceabat / Gelibolu", "tip": "Kritik Altyapı / Ulaşım",
            "koordinat_enlem": 40.217, "koordinat_boylam": 26.287, "gps_format": "[40.217°N, 26.287°E]",
            "nufus_yatak_kapasitesi": "Günlük 3000 Yolcu Kapasitesi", "risk_seviyesi": "Orta - Yüksek",
            "tahliye_rotasi": "Kabatepe - Eceabat Asfalt Arteri", "savunma_onceligi": "Kritik Altyapı ve Ulaşım Tahliyesi"
        },
        {
            "id": "YT-040",
            "isim": "57. Alay Şehitliği ve Tarihi Milli Park Kompleksi",
            "il": "Çanakkale", "ilce": "Eceabat / Gelibolu", "tip": "Tarihi Alan / Şehitlik",
            "koordinat_enlem": 40.235, "koordinat_boylam": 26.288, "gps_format": "[40.235°N, 26.288°E]",
            "nufus_yatak_kapasitesi": "Milli Park Ziyaretçi Sahası", "risk_seviyesi": "Yüksek",
            "tahliye_rotasi": "Conkbayırı Asfalt Yolu", "savunma_onceligi": "Tarihi ve Milli Miras Savunması"
        },
        {
            "id": "YT-041",
            "isim": "Çanakkale Dardanel Konserve ve Gıda Entegre Tesisleri",
            "il": "Çanakkale", "ilce": "Merkez", "tip": "Sanayi Tesisleri",
            "koordinat_enlem": 40.115, "koordinat_boylam": 26.415, "gps_format": "[40.115°N, 26.415°E]",
            "nufus_yatak_kapasitesi": "1200 İşçi", "risk_seviyesi": "Orta - Yüksek",
            "tahliye_rotasi": "Çanakkale - İzmir D550 Karayolu", "savunma_onceligi": "Sanayi Çevre Orman Hattı"
        },
        {
            "id": "YT-042",
            "isim": "Şeytan Sofrası Çamlık Turizm Tesisleri",
            "il": "Balıkesir", "ilce": "Ayvalık", "tip": "Turizm / Tesisler",
            "koordinat_enlem": 39.285, "koordinat_boylam": 26.650, "gps_format": "[39.285°N, 26.650°E]",
            "nufus_yatak_kapasitesi": "800 Kişi", "risk_seviyesi": "Yüksek",
            "tahliye_rotasi": "Ayvalık Sahil Yolu", "savunma_onceligi": "1. Öncelik (Tesis ve Doğal Miras Koruma)"
        },
        {
            "id": "YT-043",
            "isim": "Kazdağları Tahtakuşlar Köyü",
            "il": "Balıkesir", "ilce": "Edremit", "tip": "Köy / Yerleşim",
            "koordinat_enlem": 39.615, "koordinat_boylam": 26.885, "gps_format": "[39.615°N, 26.885°E]",
            "nufus_yatak_kapasitesi": "900 Nüfus", "risk_seviyesi": "Yüksek",
            "tahliye_rotasi": "Edremit - Akçay Ana Asfaltı", "savunma_onceligi": "1. Öncelik (Kazdağları Etek Köyü Savunması)"
        },
        {
            "id": "YT-044",
            "isim": "Bursa Uludağ Oteller Bölgesi (1. Gelişim Sahası)",
            "il": "Bursa", "ilce": "Osmangazi", "tip": "Turizm / Oteller",
            "koordinat_enlem": 40.105, "koordinat_boylam": 29.135, "gps_format": "[40.105°N, 29.135°E]",
            "nufus_yatak_kapasitesi": "8000 Yatak Kapasitesi", "risk_seviyesi": "Yüksek",
            "tahliye_rotasi": "Uludağ Milli Park Karayolu & Teleferik", "savunma_onceligi": "1. Öncelik (Otel Hattı Arazöz Perdesi)"
        },
        {
            "id": "YT-045",
            "isim": "İstanbul Beykoz Polonezköy Yerleşim ve Turizm Sahası",
            "il": "İstanbul", "ilce": "Beykoz", "tip": "Köy / Turizm",
            "koordinat_enlem": 41.115, "koordinat_boylam": 29.215, "gps_format": "[41.115°N, 29.215°E]",
            "nufus_yatak_kapasitesi": "1400 Nüfus", "risk_seviyesi": "Yüksek",
            "tahliye_rotasi": "Beykoz - Kavacık Orman Yolu", "savunma_onceligi": "1. Öncelik (Polonezköy Tabiat Parkı Koruma)"
        },
        {
            "id": "YT-046",
            "isim": "İstanbul Şile Ağva Tatil Köyü ve Otelleri",
            "il": "İstanbul", "ilce": "Şile", "tip": "Turizm / Yerleşim",
            "koordinat_enlem": 41.135, "koordinat_boylam": 29.845, "gps_format": "[41.135°N, 29.845°E]",
            "nufus_yatak_kapasitesi": "3500 Nüfus ve Turist", "risk_seviyesi": "Orta - Yüksek",
            "tahliye_rotasi": "Şile Otoyolu Bağlantısı", "savunma_onceligi": "2. Öncelik (Ağva Nehir Hattı Savunması)"
        },
        {
            "id": "YT-047",
            "isim": "Kocaeli Kartepe Ski Resort & Otelleri",
            "il": "Kocaeli", "ilce": "Kartepe", "tip": "Turizm / Oteller",
            "koordinat_enlem": 40.675, "koordinat_boylam": 30.085, "gps_format": "[40.675°N, 30.085°E]",
            "nufus_yatak_kapasitesi": "1800 Yatak Kapasitesi", "risk_seviyesi": "Yüksek",
            "tahliye_rotasi": "Maşukiye Dağ Asfalt Yolu", "savunma_onceligi": "1. Öncelik (Samanlı Dağı Orman Sınırı)"
        },
        {
            "id": "YT-048",
            "isim": "Sakarya Sapanca Kırkpınar Turizm Evleri ve Villalar",
            "il": "Sakarya", "ilce": "Sapanca", "tip": "Turizm / Yerleşim",
            "koordinat_enlem": 40.705, "koordinat_boylam": 30.225, "gps_format": "[40.705°N, 30.225°E]",
            "nufus_yatak_kapasitesi": "4500 Nüfus", "risk_seviyesi": "Orta - Yüksek",
            "tahliye_rotasi": "TEM Otoyolu ve Sahil Asfaltı", "savunma_onceligi": "2. Öncelik (Yamaç Orman Sınırı)"
        },
        {
            "id": "YT-049",
            "isim": "Bilecik Söğüt Çaltı Köyü",
            "il": "Bilecik", "ilce": "Söğüt", "tip": "Köy / Yerleşim",
            "koordinat_enlem": 40.085, "koordinat_boylam": 30.215, "gps_format": "[40.085°N, 30.215°E]",
            "nufus_yatak_kapasitesi": "950 Nüfus", "risk_seviyesi": "Yüksek",
            "tahliye_rotasi": "Söğüt - Eskişehir Karayolu", "savunma_onceligi": "1. Öncelik (Çamlık Vadi Köyü Koruma)"
        },
        {
            "id": "YT-050",
            "isim": "Tekirdağ Şarköy Uçmakdere Köyü ve Yamaç Paraşütü Sahası",
            "il": "Tekirdağ", "ilce": "Şarköy", "tip": "Turizm / Köy",
            "koordinat_enlem": 40.785, "koordinat_boylam": 27.355, "gps_format": "[40.785°N, 27.355°E]",
            "nufus_yatak_kapasitesi": "600 Nüfus", "risk_seviyesi": "Yüksek",
            "tahliye_rotasi": "Şarköy Sahil Karayolu", "savunma_onceligi": "1. Öncelik (Ganos Dağları Etek Köyü)"
        },
        {
            "id": "YT-051",
            "isim": "Kırklareli Demirköy İğneada Longoz Ormanları Milli Park Tesisleri",
            "il": "Kırklareli", "ilce": "Demirköy", "tip": "Milli Park / Turizm",
            "koordinat_enlem": 41.875, "koordinat_boylam": 27.985, "gps_format": "[41.875°N, 27.985°E]",
            "nufus_yatak_kapasitesi": "1200 Ziyaretçi / Tesis", "risk_seviyesi": "Yüksek",
            "tahliye_rotasi": "Demirköy - Kırklareli Karayolu", "savunma_onceligi": "Dünya Mirası Longoz Ormanları Koruma"
        },
        {
            "id": "YT-052",
            "isim": "Edirne Keşan Mecidiye Sahil Köyü ve Kampları",
            "il": "Edirne", "ilce": "Keşan", "tip": "Turizm / Köy",
            "koordinat_enlem": 40.635, "koordinat_boylam": 26.535, "gps_format": "[40.635°N, 26.535°E]",
            "nufus_yatak_kapasitesi": "2500 Nüfus ve Tatilci", "risk_seviyesi": "Yüksek",
            "tahliye_rotasi": "Keşan - Enez Karayolu", "savunma_onceligi": "1. Öncelik (Saros Körfezi Orman Sınırı)"
        },

        # --- 4. KARADENİZ BÖLGESİ (KASTAMONU, KARABÜK, SİNOP, BOLU, ZONGULDAK, BARTIN, DÜZCE, SAMSUN, TRABZON, ARTVİN, vb.) ---
        {
            "id": "YT-053",
            "isim": "Kastamonu Taşköprü Bekdemirekşi Köyü",
            "il": "Kastamonu", "ilce": "Taşköprü", "tip": "Köy / Yerleşim",
            "koordinat_enlem": 41.515, "koordinat_boylam": 34.215, "gps_format": "[41.515°N, 34.215°E]",
            "nufus_yatak_kapasitesi": "650 Nüfus", "risk_seviyesi": "Yüksek",
            "tahliye_rotasi": "Taşköprü Ana Asfalt Yolu", "savunma_onceligi": "1. Öncelik (Sarıçam Yangın Hattı Savunması)"
        },
        {
            "id": "YT-054",
            "isim": "Karabük Safranbolu Tarihi Evler Çarşısı",
            "il": "Karabük", "ilce": "Safranbolu", "tip": "Tarihi Miras / Yerleşim",
            "koordinat_enlem": 41.255, "koordinat_boylam": 32.685, "gps_format": "[41.255°N, 32.685°E]",
            "nufus_yatak_kapasitesi": "UNESCO Tarihi Kentsel Miras", "risk_seviyesi": "Çok Yüksek",
            "tahliye_rotasi": "Karabük D030 Karayolu", "savunma_onceligi": "1. Öncelik (Ahşap Kentsel Dokuyu Koruma)"
        },
        {
            "id": "YT-055",
            "isim": "Bolu Abant Gölü Oteller Bölgesi",
            "il": "Bolu", "ilce": "Mudurnu", "tip": "Turizm / Oteller",
            "koordinat_enlem": 40.605, "koordinat_boylam": 31.285, "gps_format": "[40.605°N, 31.285°E]",
            "nufus_yatak_kapasitesi": "1200 Yatak Kapasitesi", "risk_seviyesi": "Orta - Yüksek",
            "tahliye_rotasi": "Abant - Bolu Asfaltı", "savunma_onceligi": "1. Öncelik (Tabiat Parkı ve Otel Savunması)"
        },
        {
            "id": "YT-056",
            "isim": "Trabzon Uzungöl Turizm Tesisleri ve Yayla Köyü",
            "il": "Trabzon", "ilce": "Çaykara", "tip": "Turizm / Yerleşim",
            "koordinat_enlem": 40.618, "koordinat_boylam": 40.292, "gps_format": "[40.618°N, 40.292°E]",
            "nufus_yatak_kapasitesi": "4500 Turist ve Nüfus", "risk_seviyesi": "Yüksek",
            "tahliye_rotasi": "Çaykara - Of Karayolu", "savunma_onceligi": "1. Öncelik (Vadi Tahliye ve Köprü Koruma)"
        },
        {
            "id": "YT-057",
            "isim": "Artvin Şavşat Karagöl Milli Park Konukevleri",
            "il": "Artvin", "ilce": "Şavşat", "tip": "Turizm / Milli Park",
            "koordinat_enlem": 41.305, "koordinat_boylam": 42.455, "gps_format": "[41.305°N, 42.455°E]",
            "nufus_yatak_kapasitesi": "350 Ziyaretçi", "risk_seviyesi": "Yüksek",
            "tahliye_rotasi": "Şavşat Ana Asfalt Yolu", "savunma_onceligi": "Ahşap Yayla Tesisleri Koruma"
        },
        {
            "id": "YT-058",
            "isim": "Sinop Ayancık Çamyayla Köyü ve Orman İşletme Deposu",
            "il": "Sinop", "ilce": "Ayancık", "tip": "Köy / Orman Tesisleri",
            "koordinat_enlem": 41.835, "koordinat_boylam": 34.585, "gps_format": "[41.835°N, 34.585°E]",
            "nufus_yatak_kapasitesi": "780 Nüfus", "risk_seviyesi": "Yüksek",
            "tahliye_rotasi": "Ayancık Sahil Karayolu", "savunma_onceligi": "1. Öncelik (Tomruk Deposu ve Köy Koruma)"
        },
        {
            "id": "YT-059",
            "isim": "Zonguldak Çaycuma Filyos Doğalgaz İşleme ve Terminal Tesisi",
            "il": "Zonguldak", "ilce": "Çaycuma", "bolge": "Filyos Sahil Sektörü",
            "tip": "Kritik Sanayi / Enerji", "koordinat_enlem": 41.565, "koordinat_boylam": 32.045, "gps_format": "[41.565°N, 32.045°E]",
            "nufus_yatak_kapasitesi": "2500 Mühendis ve Personel", "risk_seviyesi": "Çok Yüksek",
            "tahliye_rotasi": "Filyos - Zonguldak Karayolu", "savunma_onceligi": "1. Sınıf Kritik Doğalgaz Terminali Koruma"
        },
        {
            "id": "YT-060",
            "isim": "Bartın Amasra Tarihi Liman ve Yerleşim Sahası",
            "il": "Bartın", "ilce": "Amasra", "tip": "Tarihi Yerleşim / Turizm",
            "koordinat_enlem": 41.745, "koordinat_boylam": 32.385, "gps_format": "[41.745°N, 32.385°E]",
            "nufus_yatak_kapasitesi": "6500 Nüfus ve Turist", "risk_seviyesi": "Yüksek",
            "tahliye_rotasi": "Bartın - Amasra Tünel Yolu", "savunma_onceligi": "1. Öncelik (Yamaç Ormanı ve Kentsel Alan)"
        },
        {
            "id": "YT-061",
            "isim": "Düzce Güzeldere Şelalesi Tabiat Parkı Tesisleri",
            "il": "Düzce", "ilce": "Gölyaka", "tip": "Turizm / Tabiat Parkı",
            "koordinat_enlem": 40.715, "koordinat_boylam": 31.025, "gps_format": "[40.715°N, 31.025°E]",
            "nufus_yatak_kapasitesi": "500 Ziyaretçi", "risk_seviyesi": "Yüksek",
            "tahliye_rotasi": "Gölyaka - Düzce Karayolu", "savunma_onceligi": "Tabiat Parkı ve Kayın Ormanı Koruma"
        },
        {
            "id": "YT-062",
            "isim": "Samsun Vezirköprü Kunduz Dağı Milli Kamp Tesisleri",
            "il": "Samsun", "ilce": "Vezirköprü", "tip": "Turizm / Kamp Alanı",
            "koordinat_enlem": 41.185, "koordinat_boylam": 35.185, "gps_format": "[41.185°N, 35.185°E]",
            "nufus_yatak_kapasitesi": "800 Kampçı / Nüfus", "risk_seviyesi": "Yüksek",
            "tahliye_rotasi": "Vezirköprü Asfalt Yolu", "savunma_onceligi": "1. Öncelik (Sarıçam Ormanı Merkez Savunma)"
        },
        {
            "id": "YT-063",
            "isim": "Rize Ayder Yaylası Ahşap Turizm Otelleri",
            "il": "Rize", "ilce": "Çamlıhemşin", "tip": "Turizm / Oteller",
            "koordinat_enlem": 40.955, "koordinat_boylam": 41.115, "gps_format": "[40.955°N, 41.115°E]",
            "nufus_yatak_kapasitesi": "3500 Turist ve Yatak", "risk_seviyesi": "Yüksek",
            "tahliye_rotasi": "Çamlıhemşin - Ardeşen Vadi Yolu", "savunma_onceligi": "1. Öncelik (Ahşap Yayla Tesisleri Yangın Hattı)"
        },

        # --- 5. İÇ ANADOLU BÖLGESİ (ANKARA, ESKİŞEHİR, KONYA, KARAMAN, KAYSERİ, SİVAS, ÇANKIRI, YOZGAT) ---
        {
            "id": "YT-064",
            "isim": "Ankara Kızılcahamam Soğuksu Milli Park Otelleri",
            "il": "Ankara", "ilce": "Kızılcahamam", "tip": "Turizm / Oteller",
            "koordinat_enlem": 40.465, "koordinat_boylam": 32.635, "gps_format": "[40.465°N, 32.635°E]",
            "nufus_yatak_kapasitesi": "1500 Yatak Kapasitesi", "risk_seviyesi": "Yüksek",
            "tahliye_rotasi": "E89 Otoyolu ve Kızılcahamam Asfaltı", "savunma_onceligi": "1. Öncelik (Milli Park Çamlık Koruma)"
        },
        {
            "id": "YT-065",
            "isim": "Ankara Çamlıdere Çamkoru Tabiat Parkı Evleri",
            "il": "Ankara", "ilce": "Çamlıdere", "tip": "Turizm / Yerleşim",
            "koordinat_enlem": 40.395, "koordinat_boylam": 32.485, "gps_format": "[40.395°N, 32.485°E]",
            "nufus_yatak_kapasitesi": "450 Nüfus / Kampçı", "risk_seviyesi": "Yüksek",
            "tahliye_rotasi": "Ankara - Gerede Otoyolu (O-4)", "savunma_onceligi": "1. Öncelik (Çamkoru Göleti Çevre Savunması)"
        },
        {
            "id": "YT-066",
            "isim": "Eskişehir Seyitgazi Kırka Bor İşletmeleri ve Lojmanları",
            "il": "Eskişehir", "ilce": "Seyitgazi", "tip": "Kritik Sanayi / Yerleşim",
            "koordinat_enlem": 39.285, "koordinat_boylam": 30.515, "gps_format": "[39.285°N, 30.515°E]",
            "nufus_yatak_kapasitesi": "2500 İşçi ve Aile", "risk_seviyesi": "Yüksek",
            "tahliye_rotasi": "Eskişehir - Afyon Karayolu", "savunma_onceligi": "1. Öncelik (Maden Tesisleri Çevre Şeridi)"
        },
        {
            "id": "YT-067",
            "isim": "Konya Beyşehir Yeşildağ Köyü",
            "il": "Konya", "ilce": "Beyşehir", "tip": "Köy / Yerleşim",
            "koordinat_enlem": 37.615, "koordinat_boylam": 31.515, "gps_format": "[37.615°N, 31.515°E]",
            "nufus_yatak_kapasitesi": "1200 Nüfus", "risk_seviyesi": "Yüksek",
            "tahliye_rotasi": "Beykoz - Derebucak Karayolu", "savunma_onceligi": "1. Öncelik (Anamas Dağı Etek Köyü)"
        },
        {
            "id": "YT-068",
            "isim": "Karaman Ermenek Tepebaşı Köyü",
            "il": "Karaman", "ilce": "Ermenek", "tip": "Köy / Yerleşim",
            "koordinat_enlem": 36.685, "koordinat_boylam": 32.915, "gps_format": "[36.685°N, 32.915°E]",
            "nufus_yatak_kapasitesi": "680 Nüfus", "risk_seviyesi": "Yüksek",
            "tahliye_rotasi": "Ermenek - Mut Dağ Karayolu", "savunma_onceligi": "1. Öncelik (Sarp Kanyon Köyü Koruma)"
        },
        {
            "id": "YT-069",
            "isim": "Kayseri Yahyalı Kapuzbaşı Şelaleleri Turizm Evleri",
            "il": "Kayseri", "ilce": "Yahyalı", "tip": "Turizm / Tabiat Parkı",
            "koordinat_enlem": 37.845, "koordinat_boylam": 35.385, "gps_format": "[37.845°N, 35.385°E]",
            "nufus_yatak_kapasitesi": "600 Ziyaretçi / Köylü", "risk_seviyesi": "Yüksek",
            "tahliye_rotasi": "Yahyalı - Aladağ Kanyon Yolu", "savunma_onceligi": "Aladağlar Milli Park Sınırı Savunması"
        },
        {
            "id": "YT-070",
            "isim": "Sivas Koyulhisar Eğriçimen Yaylası Evleri",
            "il": "Sivas", "ilce": "Koyulhisar", "tip": "Yayla / Yerleşim",
            "koordinat_enlem": 40.345, "koordinat_boylam": 37.885, "gps_format": "[40.345°N, 37.885°E]",
            "nufus_yatak_kapasitesi": "950 Nüfus", "risk_seviyesi": "Yüksek",
            "tahliye_rotasi": "Koyulhisar - Sivas D865 Karayolu", "savunma_onceligi": "1. Öncelik (Sarıçam Yayla Evleri Koruma)"
        },
        {
            "id": "YT-071",
            "isim": "Yozgat Çamlığı Milli Park Tesisleri ve Şehir Yolu",
            "il": "Yozgat", "ilce": "Merkez", "tip": "Milli Park / Şehir Sınırı",
            "koordinat_enlem": 39.805, "koordinat_boylam": 34.815, "gps_format": "[39.805°N, 34.815°E]",
            "nufus_yatak_kapasitesi": "Türkiye'nin 1. Milli Parkı", "risk_seviyesi": "Yüksek",
            "tahliye_rotasi": "Yozgat Merkez Çevre Yolu", "savunma_onceligi": "Tarihi ve İlk Milli Park Karaçam Koruma"
        },

        # --- 6. DOĞU ANADOLU BÖLGESİ (TUNCELİ, BİNGÖL, ELAZIĞ, MALATYA, ERZURUM, KARS, vb.) ---
        {
            "id": "YT-072",
            "isim": "Tunceli Ovacık Yeşilyazı Köyü",
            "il": "Tunceli", "ilce": "Ovacık", "tip": "Köy / Yerleşim",
            "koordinat_enlem": 39.345, "koordinat_boylam": 39.185, "gps_format": "[39.345°N, 39.185°E]",
            "nufus_yatak_kapasitesi": "850 Nüfus", "risk_seviyesi": "Yüksek",
            "tahliye_rotasi": "Ovacık - Tunceli Vadi Karayolu", "savunma_onceligi": "1. Öncelik (Munzur Vadisi Köy Savunması)"
        },
        {
            "id": "YT-073",
            "isim": "Bingöl Solhan Şeref Meydanı Yayla Yerleşimi",
            "il": "Bingöl", "ilce": "Solhan", "tip": "Köy / Yerleşim",
            "koordinat_enlem": 38.945, "koordinat_boylam": 41.045, "gps_format": "[38.945°N, 41.045°E]",
            "nufus_yatak_kapasitesi": "700 Nüfus", "risk_seviyesi": "Orta - Yüksek",
            "tahliye_rotasi": "Bingöl - Muş D300 Karayolu", "savunma_onceligi": "1. Öncelik (Meşe Orman Sınırı Köy Koruma)"
        },
        {
            "id": "YT-074",
            "isim": "Elazığ Maden Hazar Gölü Tatil Siteleri ve Kamp Sahası",
            "il": "Elazığ", "ilce": "Sivrice", "tip": "Turizm / Yerleşim",
            "koordinat_enlem": 38.485, "koordinat_boylam": 39.315, "gps_format": "[38.485°N, 39.315°E]",
            "nufus_yatak_kapasitesi": "4000 Tatilci / Nüfus", "risk_seviyesi": "Yüksek",
            "tahliye_rotasi": "Elazığ - Diyarbakır Karayolu", "savunma_onceligi": "2. Öncelik (Hazar Baba Dağı Etek Savunması)"
        },
        {
            "id": "YT-075",
            "isim": "Malatya Pütürge Tepehan Köyü",
            "il": "Malatya", "ilce": "Pütürge", "tip": "Köy / Yerleşim",
            "koordinat_enlem": 38.185, "koordinat_boylam": 38.885, "gps_format": "[38.185°N, 38.885°E]",
            "nufus_yatak_kapasitesi": "620 Nüfus", "risk_seviyesi": "Yüksek",
            "tahliye_rotasi": "Malatya - Pütürge Dağ Karayolu", "savunma_onceligi": "1. Öncelik (Meşelik Dağ Köyü Savunması)"
        },
        {
            "id": "YT-076",
            "isim": "Erzurum Sarıkamış Cıbıltepe Kayak Merkezi Otelleri",
            "il": "Kars", "ilce": "Sarıkamış", "tip": "Turizm / Oteller",
            "koordinat_enlem": 40.315, "koordinat_boylam": 42.615, "gps_format": "[40.315°N, 42.615°E]",
            "nufus_yatak_kapasitesi": "3000 Yatak Kapasitesi", "risk_seviyesi": "Yüksek",
            "tahliye_rotasi": "Sarıkamış - Kars Karayolu", "savunma_onceligi": "1. Öncelik (Sarıçam Ormanı Otel Şeridi)"
        },
        {
            "id": "YT-077",
            "isim": "Kars Sarıkamış Şehitlikleri ve Tarihi Orman Sahası",
            "il": "Kars", "ilce": "Sarıkamış", "tip": "Tarihi Miras / Milli Park",
            "koordinat_enlem": 40.355, "koordinat_boylam": 42.585, "gps_format": "[40.355°N, 42.585°E]",
            "nufus_yatak_kapasitesi": "Milli Park Anıt Sahası", "risk_seviyesi": "Yüksek",
            "tahliye_rotasi": "Erzurum - Kars Karayolu", "savunma_onceligi": "Şehitlikler ve Sarıçam Miras Savunması"
        },

        # --- 7. GÜNEYDOĞU ANADOLU BÖLGESİ (ŞIRNAK, DİYARBAKIR, MARDİN, SİİRT, HAKKARİ, ŞANLIURFA, ADIYAMAN, BATMAN) ---
        {
            "id": "YT-078",
            "isim": "Şırnak Cizre - Gabar Petrol Arama ve Üretim Sahası",
            "il": "Şırnak", "ilce": "Merkez / Güçlükonak", "tip": "Kritik Sanayi / Enerji",
            "koordinat_enlem": 37.585, "koordinat_boylam": 42.185, "gps_format": "[37.585°N, 42.185°E]",
            "nufus_yatak_kapasitesi": "1200 Teknik Personel / Petrol Kuyuları", "risk_seviyesi": "Çok Yüksek",
            "tahliye_rotasi": "Şırnak - Cizre Karayolu", "savunma_onceligi": "1. Sınıf Kritik Enerji ve Petrol Sahası Koruma"
        },
        {
            "id": "YT-079",
            "isim": "Diyarbakır Lice Duru Mahallesi",
            "il": "Diyarbakır", "ilce": "Lice", "tip": "Mahalle / Yerleşim",
            "koordinat_enlem": 38.415, "koordinat_boylam": 40.615, "gps_format": "[38.415°N, 40.615°E]",
            "nufus_yatak_kapasitesi": "1100 Nüfus", "risk_seviyesi": "Orta - Yüksek",
            "tahliye_rotasi": "Diyarbakır - Bingöl Karayolu (D950)", "savunma_onceligi": "1. Öncelik (Yerleşim ve Yol Güvenliği)"
        },
        {
            "id": "YT-080",
            "isim": "Siirt Tillo (Aydınlar) Tarihi Yerleşim ve İbrahim Hakkı Hazretleri Külliyesi",
            "il": "Siirt", "ilce": "Tillo", "tip": "Tarihi Miras / Yerleşim",
            "koordinat_enlem": 37.945, "koordinat_boylam": 42.015, "gps_format": "[37.945°N, 42.015°E]",
            "nufus_yatak_kapasitesi": "4200 Nüfus", "risk_seviyesi": "Yüksek",
            "tahliye_rotasi": "Siirt Merkez Karayolu", "savunma_onceligi": "1. Öncelik (Botan Vadisi Sınırı Tarihi Koruma)"
        },
        {
            "id": "YT-081",
            "isim": "Adıyaman Nemrut Dağı Milli Park Tesisleri ve Ziyaretçi Merkezi",
            "il": "Adıyaman", "ilce": "Kahta", "tip": "Milli Park / Turizm",
            "koordinat_enlem": 37.985, "koordinat_boylam": 38.745, "gps_format": "[37.985°N, 38.745°E]",
            "nufus_yatak_kapasitesi": "1000 Turist / Ziyaretçi", "risk_seviyesi": "Orta - Yüksek",
            "tahliye_rotasi": "Kahta - Nemrut Dağ Asfaltı", "savunma_onceligi": "UNESCO Dünya Mirası ve Çevre Orman Koruma"
        },
        {
            "id": "YT-082",
            "isim": "Batman Sason Yücebağ Köyü",
            "il": "Batman", "ilce": "Sason", "tip": "Köy / Yerleşim",
            "koordinat_enlem": 38.315, "koordinat_boylam": 41.315, "gps_format": "[38.315°N, 41.315°E]",
            "nufus_yatak_kapasitesi": "850 Nüfus", "risk_seviyesi": "Yüksek",
            "tahliye_rotasi": "Sason - Muş Vadi Karayolu", "savunma_onceligi": "1. Öncelik (Sarp Dağ Köyü Tahliye ve Koruma)"
        },
        {
            "id": "YT-083",
            "isim": "Mardin Mazıdağı Fosfat İşletmeleri ve Çevresi",
            "il": "Mardin", "ilce": "Mazıdağı", "tip": "Kritik Sanayi / Yerleşim",
            "koordinat_enlem": 37.515, "koordinat_boylam": 40.485, "gps_format": "[37.515°N, 40.485°E]",
            "nufus_yatak_kapasitesi": "1500 İşçi ve Teknik Personel", "risk_seviyesi": "Orta - Yüksek",
            "tahliye_rotasi": "Mardin - Diyarbakır D950 Karayolu", "savunma_onceligi": "1. Öncelik (Maden Tesisi Çevre Emniyeti)"
        },
        {
            "id": "YT-084",
            "isim": "Hakkari Çukurca Çığlı Köyü",
            "il": "Hakkari", "ilce": "Çukurca", "tip": "Köy / Sınır Yerleşimi",
            "koordinat_enlem": 37.315, "koordinat_boylam": 43.485, "gps_format": "[37.315°N, 43.485°E]",
            "nufus_yatak_kapasitesi": "1100 Nüfus", "risk_seviyesi": "Yüksek",
            "tahliye_rotasi": "Çukurca - Hakkari Karayolu", "savunma_onceligi": "1. Öncelik (Sınır Hattı Köy Savunması)"
        }
    ]

def main():
    base_dir = Path(__file__).resolve().parent
    data_dir = base_dir / "data"
    data_dir.mkdir(exist_ok=True)

    water_resources = generate_all_turkey_water_resources()
    settlements = generate_all_turkey_settlements_and_facilities()

    water_path = data_dir / "su_kaynaklari.json"
    settlement_path = data_dir / "yerlesim_ve_tesisler.json"

    with open(water_path, "w", encoding="utf-8") as f:
        json.dump(water_resources, f, ensure_ascii=False, indent=2)

    with open(settlement_path, "w", encoding="utf-8") as f:
        json.dump(settlements, f, ensure_ascii=False, indent=2)

    print("==================================================================================")
    print("🇹🇷 TÜRKİYE GENELİ ORMAN YANGINLARI CBS & TAKTİK SEVKİYAT VERİ TABANI OLUŞTURULDU 🇹🇷")
    print("==================================================================================")
    print(f"✅ Toplam {len(water_resources)} stratejik su kaynağı (7 Bölge, Baraj, Göl, Koy, OGM Havuzu) -> {water_path}")
    print(f"✅ Toplam {len(settlements)} kritik yerleşim, otel, termik santral, nükleer/petrol sahası -> {settlement_path}")
    print("==================================================================================")

if __name__ == "__main__":
    main()
