import feedparser
import pandas as pd
import urllib.parse
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import re

def veri_cek_ve_analiz_et(marka):
    su_an = 2026
    veriler = []
    
    # Kelime ağırlıkları (Krizin şiddetini belirler)
    agirliklar = {'boykot': 10, 'israil': 10, 'filistin': 10, 'protesto': 8, 'etik': 7, 
                  'zam': 5, 'pahalı': 5, 'asit': 4, 'böcek': 6, 'fare': 7, 'şeker': 4}

    print(f"🕵️ {marka} Dijital Arşivi Analiz Ediliyor (2016 - {su_an})...\n")

    for yil in range(su_an - 10, su_an + 1):
        sorgu = f'{marka} "boykot" OR "şikayet" OR "kriz" after:{yil}-01-01 before:{yil}-12-31'
        url = f"https://news.google.com/rss/search?q={urllib.parse.quote(sorgu)}&hl=tr&gl=TR&ceid=TR:tr"
        
        besleme = feedparser.parse(url)
        yil_basliklari = []
        yil_skoru = 0
        
        for entry in besleme.entries[:20]:
            baslik = entry.title.lower()
            yil_basliklari.append(baslik)
            # Skorlama
            skor = sum(v for k, v in agirliklar.items() if k in baslik)
            yil_skoru += (skor if skor > 0 else 1)
            
        # O yılın en popüler/olumsuz anahtar kelimesini bulma
        if yil_basliklari:
            kelimeler = " ".join(yil_basliklari)
            # Marka ismini (ikea) ve genel kelimeleri filtrele
            temiz_kelimeler = [w for w in re.findall(r'\w+', kelimeler) if len(w) > 3 and w not in [marka.lower(), 'haber', 'yeni', 'sonra', 'türkiye']]
            en_cok_gecen = Counter(temiz_kelimeler).most_common(1)
            anahtar_kriz = en_cok_gecen[0][0] if en_cok_gecen else "Belirsiz"
        else:
            anahtar_kriz = "Veri Yok"

        veriler.append({
            'Yil': yil,
            'CCI_Skor': yil_skoru,
            'Kritik_Kelimeler': anahtar_kriz,
            'Veri_Sayisi': len(yil_basliklari)
        })
        print(f"✅ {yil} Analiz Edildi: En Kritik Kelime -> {anahtar_kriz.upper()}")

    return pd.DataFrame(veriler)

def profesyonel_dashboard(df, marka):
    # Görsel Ayarlar
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(15, 8))
    
    # 1. Kriz Şiddeti Bar Grafiği
    bar_plot = sns.barplot(data=df, x='Yil', y='CCI_Skor', palette='Reds_r', ax=ax)
    
    # 2. Her Barın Üzerine "O Yılın Kriz Kelimesini" Yazma
    for i, p in enumerate(bar_plot.patches):
        kriz_kelimesi = df.iloc[i]['Kritik_Kelimeler'].upper()
        ax.annotate(f"⚠️ {kriz_kelimesi}", 
                    (p.get_x() + p.get_width() / 2., p.get_height()), 
                    ha = 'center', va = 'center', 
                    xytext = (0, 15), 
                    textcoords = 'offset points',
                    fontsize=11, color='yellow', fontweight='bold', rotation=0)

    # Estetik Dokunuşlar
    plt.title(f"{marka.upper()} 10 YILLIK KRİZ HAFIZASI VE ANAHTAR ŞİKAYETLER", fontsize=20, color='white', fontweight='bold', pad=30)
    plt.ylabel("Kritik Kriz Endeksi (CCI)", fontsize=14)
    plt.xlabel("Yıllar", fontsize=14)
    plt.ylim(0, df['CCI_Skor'].max() * 1.3) # Yazılar sığsın diye tavanı yükselt
    
    # Eleştirel Çıkarım Notu (Annotation)
    zirve_yil = df.loc[df['CCI_Skor'].idxmax()]
    plt.figtext(0.15, 0.02, f"🚩 ANALİST NOTU: {int(zirve_yil['Yil'])} yılındaki '{zirve_yil['Kritik_Kelimeler']}' krizi, marka algısındaki en kritik kırılmadır.", 
                color='red', fontsize=12, fontweight='bold', bbox=dict(facecolor='white', alpha=0.1))

    plt.tight_layout()
    plt.show()

# ÇALIŞTIR
if __name__ == "__main__":
    hedef_marka = "IKEA"
    df_final = veri_cek_ve_analiz_et(hedef_marka)
    profesyonel_dashboard(df_final, hedef_marka)