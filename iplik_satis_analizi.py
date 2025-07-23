import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import calendar
import pyodbc
from prophet import Prophet

st.set_page_config(page_title="Satış Analizi", layout="wide")
st.title("Satış Analizi ve Tahmin")

# Tarih çözüm fonksiyonu 
def tarih_coz(tarih_str):
    if "-" in tarih_str and tarih_str.count("-") == 2:
        dt = datetime.strptime(tarih_str, "%d-%m-%Y")
        return dt.strftime("%Y-%m-%d"), dt.strftime("%Y-%m-%d")
    elif "-" in tarih_str and tarih_str.count("-") == 1:
        dt = datetime.strptime("01-" + tarih_str, "%d-%m-%Y")
        y, m = dt.year, dt.month
        son_gun = calendar.monthrange(y, m)[1]
        return dt.strftime("%Y-%m-%d"), f"{y}-{m:02d}-{son_gun}"
    else:
        y = int(tarih_str)
        return f"{y}-01-01", f"{y}-12-31"

def tarih_araligini_coz(t1, t2):
    b1, _ = tarih_coz(t1)
    _, b2 = tarih_coz(t2)
    return b1, b2

# SQL sorgu fonksiyonu
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
    columns = [col[0] for col in cursor.description]
    cursor.close()
    conn.close()
    return pd.DataFrame.from_records(rows, columns=columns)

# Tarih girişi (kullanıcıdan)
col1, col2 = st.columns([3, 3])
with col1:
    giris1 = st.text_input("Başlangıç tarihi (Gün-Ay-Yıl / Ay-Yıl / Yıl)", value="01-01-2024")
with col2:
    giris2 = st.text_input("Bitiş tarihi (Gün-Ay-Yıl / Ay-Yıl / Yıl)", value="06-2025")

st.markdown("### Gösterilecek Grafik(ler)i Seçin")
grafik_secimleri = st.multiselect(
    "Hangi grafik(ler)i görmek istiyorsunuz?",
    [
        "En Çok Satış Yapan 10 Firma",
        "En Çok Satılan 10 Stok Kodu",
        "En Çok Satılan 10 Stok Adı",   
        "En Çok Satılan 10 LotNo",
        "Gelecek 6 Aylık Satış Tahmini"
    ],
    default=["En Çok Satış Yapan 10 Firma"]
)

buton = st.button("Veriyi Getir")

if buton:
    st.info("Veriler yükleniyor, lütfen bekleyiniz..")
    try:
        baslangic_tarihi, bitis_tarihi = tarih_araligini_coz(giris1, giris2)

        query = """
        SELECT Ay, CariAdi, Miktar1, StokKodu, LotNo, StokAdi
        FROM vw_IplikSatis
        WHERE Ay BETWEEN ? AND ?
        """
        df = sorgu_yap(query, (baslangic_tarihi, bitis_tarihi))

        if df.empty:
            st.warning("Seçilen tarih aralığında veri bulunamadı.")
            st.stop()

        df['Miktar1_numeric'] = pd.to_numeric(df['Miktar1'], errors='coerce')
        df = df.dropna(subset=['Miktar1_numeric', 'Ay'])

        st.success(f"Veri başarıyla yüklendi! Toplam {len(df)} kayıt.")

        # Grafik 1: En Çok Satış Yapan 10 Firma
        if "En Çok Satış Yapan 10 Firma" in grafik_secimleri:
            top10_firma = df.groupby("CariAdi")["Miktar1_numeric"].sum().sort_values(ascending=False).head(10)
            st.subheader("En Çok Satış Yapan 10 Firma")
            fig1, ax1 = plt.subplots(figsize=(10, 6))
            top10_firma.sort_values().plot(kind='barh', ax=ax1, color='mediumseagreen')
            ax1.set_xlabel("Toplam Miktar")
            for i, v in enumerate(top10_firma.sort_values()):
                ax1.text(v + max(top10_firma.values)*0.01, i, f"{v:,.2f}", va='center')
            st.pyplot(fig1)

        # Grafik 2: En Çok Satılan 10 Stok Kodu
        if "En Çok Satılan 10 Stok Kodu" in grafik_secimleri:
            top10_stok = df.groupby("StokKodu")["Miktar1_numeric"].sum().sort_values(ascending=False).head(10)
            st.subheader("En Çok Satılan 10 Stok Kodu")
            fig2, ax2 = plt.subplots(figsize=(10, 6))
            top10_stok.sort_values().plot(kind='barh', ax=ax2, color='steelblue')
            ax2.set_xlabel("Toplam Miktar")
            for i, v in enumerate(top10_stok.sort_values()):
                ax2.text(v + max(top10_stok.values)*0.01, i, f"{v:,.2f}", va='center')
            st.pyplot(fig2)

        # Grafik 3: En Çok Satılan 10 Stok Adı
        if "En Çok Satılan 10 Stok Adı" in grafik_secimleri:
            top10_stokadi = df.groupby("StokAdi")["Miktar1_numeric"].sum().sort_values(ascending=False).head(10)
            st.subheader("En Çok Satılan 10 Stok Adı")
            fig4, ax4 = plt.subplots(figsize=(10, 6))
            top10_stokadi.sort_values().plot(kind='barh', ax=ax4, color='purple')
            ax4.set_xlabel("Toplam Miktar")
            for i, v in enumerate(top10_stokadi.sort_values()):
                ax4.text(v + max(top10_stokadi.values)*0.01, i, f"{v:,.2f}", va='center')
            st.pyplot(fig4)

        # Grafik 4: En Çok Satılan 10 LotNo
        if "En Çok Satılan 10 LotNo" in grafik_secimleri:
            top10_lot = df.groupby("LotNo")["Miktar1_numeric"].sum().sort_values(ascending=False).head(10)
            st.subheader("En Çok Satılan 10 LotNo")
            fig3, ax3 = plt.subplots(figsize=(10, 6))
            top10_lot.sort_values().plot(kind='barh', ax=ax3, color='darkorange')
            ax3.set_xlabel("Toplam Miktar")
            for i, v in enumerate(top10_lot.sort_values()):
                ax3.text(v + max(top10_lot.values)*0.01, i, f"{v:,.2f}", va='center')
            st.pyplot(fig3)

        # Grafik 5: Gelecek 6 Aylık Satış Tahmini (Prophet)
        if "Gelecek 6 Aylık Satış Tahmini" in grafik_secimleri:
            df_monthly = df.groupby("Ay")["Miktar1_numeric"].sum().reset_index()
            df_monthly.rename(columns={'Ay': 'ds', 'Miktar1_numeric': 'y'}, inplace=True)
            df_monthly['ds'] = pd.to_datetime(df_monthly['ds'])
            df_monthly['y'] = df_monthly['y'] / 1e6 

            if len(df_monthly) < 6:
                st.warning("Tahmin için en az 6 aylık veri gereklidir.")
            else:
                model = Prophet(yearly_seasonality=True, seasonality_mode='multiplicative')
                model.fit(df_monthly)

                future = model.make_future_dataframe(periods=6, freq='MS')
                forecast = model.predict(future)
                forecast_future = forecast[forecast['ds'] > df_monthly['ds'].max()].copy()

                for col in ['yhat', 'yhat_lower', 'yhat_upper']:
                    forecast_future[col] = (forecast_future[col] * 1e6).clip(lower=0)
                df_monthly['y'] = df_monthly['y'] * 1e6

                st.subheader("Gelecek 6 Aylık Satış Tahmini Grafiği")
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.plot(df_monthly['ds'], df_monthly['y'], label='Gerçek Satış', color='blue')
                ax.plot(forecast_future['ds'], forecast_future['yhat'], label='Tahmin', color='green', marker='o')
                ax.fill_between(forecast_future['ds'], forecast_future['yhat_lower'], forecast_future['yhat_upper'], color='green', alpha=0.3)
                ax.set_title("Prophet ile Tahmini Satışlar (6 Ay)")
                ax.set_xlabel("Tarih")
                ax.set_ylabel("Miktar")
                ax.grid(True)
                ax.legend()
                for i, v in enumerate(forecast_future['yhat']):
                    ax.text(forecast_future['ds'].iloc[i], v, f"{v:,.0f}", ha='center', va='bottom', fontsize=8)
                st.pyplot(fig)

    except Exception as e:
        st.error(f"Hata oluştu: {e}")



