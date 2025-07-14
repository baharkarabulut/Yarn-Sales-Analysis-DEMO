import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from neuralprophet import NeuralProphet
from datetime import datetime
import calendar
import pyodbc

st.set_page_config(page_title="Satış Analizi", layout="wide")
st.title("Satış Analizi ve Tahmin")

# Tarih çözüm fonksiyonu: farklı formatlardaki tarih girişlerini normalize eder
def tarih_coz(tarih_str):
    if "-" in tarih_str and tarih_str.count("-") == 2:  # Gün-Ay-Yıl formatı
        dt = datetime.strptime(tarih_str, "%d-%m-%Y")
        return dt.strftime("%Y-%m-%d"), dt.strftime("%Y-%m-%d")
    elif "-" in tarih_str and tarih_str.count("-") == 1:  # Ay-Yıl formatı
        dt = datetime.strptime("01-" + tarih_str, "%d-%m-%Y")
        y, m = dt.year, dt.month
        son_gun = calendar.monthrange(y, m)[1]
        return dt.strftime("%Y-%m-%d"), f"{y}-{m:02d}-{son_gun}"
    else:  # Yıl formatı
        y = int(tarih_str)
        return f"{y}-01-01", f"{y}-12-31"

def tarih_araligini_coz(tarih1, tarih2):
    baslangic1, _ = tarih_coz(tarih1)
    _, bitis2 = tarih_coz(tarih2)
    return baslangic1, bitis2

# SQL sorgusu
def sorgu_yap(query, params):
    conn = pyodbc.connect(
        "DRIVER={SQL Server};"
        "SERVER=ServerName;"
        "DATABASE=DatabaseName;"
        "UID=Name;"
        "PWD=PSW;",
        autocommit=True
    )
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    cursor.close()
    conn.close()
    return pd.DataFrame.from_records(rows, columns=columns)

# Kullanıcıdan tarih aralığı al
col1, col2, col3 = st.columns([3,3,1])
with col1:
    giris1 = st.text_input("Başlangıç tarihi (Gün-Ay-Yıl / Ay-Yıl / Yıl)", value="01-01-2023")
with col2:
    giris2 = st.text_input("Bitiş tarihi (Gün-Ay-Yıl / Ay-Yıl / Yıl)", value="06-2024")
with col3:
    buton = st.button("Veriyi Getir")

if buton:
    st.info("Veriler yükleniyor, lütfen bekleyiniz...")
    try:
        baslangic_tarihi, bitis_tarihi = tarih_araligini_coz(giris1, giris2)
        st.write(f"Tarih aralığı: {baslangic_tarihi} - {bitis_tarihi}")

        # SQL sorgusu
        query = """
        SELECT Ay, CariAdi, Miktar1, StokKodu, LotNo
        FROM vw_IplikSatis
        WHERE Ay BETWEEN ? AND ?
        """
        df = sorgu_yap(query, (baslangic_tarihi, bitis_tarihi))

        if df.empty:
            st.warning("Seçilen tarih aralığında veri bulunamadı.")
            st.stop()

        # Miktar1 sütununu sayısala çevir ve NaN satırlarını at
        df['Miktar1_numeric'] = pd.to_numeric(df['Miktar1'], errors='coerce')
        df = df.dropna(subset=['Miktar1_numeric'])

        st.success(f"Veri başarıyla yüklendi! Toplam {len(df)} kayıt.")

        #En çok satış yapan 10 firma
        top10_firma = df.groupby("CariAdi")["Miktar1_numeric"].sum().sort_values(ascending=False).head(10)
        st.subheader("En Çok Satış Yapan 10 Firma")
        fig1, ax1 = plt.subplots(figsize=(10, 6))
        top10_firma.sort_values().plot(kind='barh', ax=ax1, color='mediumseagreen')
        ax1.set_xlabel("Toplam Miktar")
        ax1.set_title("En Çok Satış Yapan 10 Firma")
        for i, v in enumerate(top10_firma.sort_values()):
            ax1.text(v + max(top10_firma.values)*0.01, i, f"{v:,.2f}", va='center')
        st.pyplot(fig1)

        #En çok satılan 10 stok kodu
        top10_stok = df.groupby("StokKodu")["Miktar1_numeric"].sum().sort_values(ascending=False).head(10)
        st.subheader("En Çok Satılan 10 Stok Kodu")
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        top10_stok.sort_values().plot(kind='barh', ax=ax2, color='steelblue')
        ax2.set_xlabel("Toplam Miktar")
        ax2.set_title("En Çok Satılan 10 Stok Kodu")
        for i, v in enumerate(top10_stok.sort_values()):
            ax2.text(v + max(top10_stok.values)*0.01, i, f"{v:,.2f}", va='center')
        st.pyplot(fig2)

        #En çok satılan 10 LotNo
        top10_lot = df.groupby("LotNo")["Miktar1_numeric"].sum().sort_values(ascending=False).head(10)
        st.subheader("En Çok Satılan 10 LotNo")
        fig3, ax3 = plt.subplots(figsize=(10, 6))
        top10_lot.sort_values().plot(kind='barh', ax=ax3, color='darkorange')
        ax3.set_xlabel("Toplam Miktar")
        ax3.set_title("En Çok Satılan 10 LotNo")
        for i, v in enumerate(top10_lot.sort_values()):
            ax3.text(v + max(top10_lot.values)*0.01, i, f"{v:,.2f}", va='center')
        st.pyplot(fig3)


    except Exception as e:
        st.error(f"Hata oluştu: {e}")
