import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Konfigurasi halaman
st.set_page_config(
    page_title="E-Commerce 2017 Interactive Dashboard",
    page_icon="🛒",
    layout="wide"
)

# Membaca data
@st.cache_data
def load_data():
    monthly_revenue = pd.read_csv('dashboard/monthly_revenue_clean.csv')
    top_5_analysis = pd.read_csv('dashboard/top_5_analysis_clean.csv')
    rfm_df = pd.read_csv('dashboard/rfm_clean.csv')
    geo_df = pd.read_csv('dashboard/geo_clean.csv')
    return monthly_revenue, top_5_analysis, rfm_df, geo_df

try:
    # Membaca dari folder 'dashboard/' sesuai direktori standar baru
    monthly_rev, top_5, rfm, geo = load_data()
except FileNotFoundError:
    # Fallback ke root jika file belum dipindahkan di local PC
    monthly_rev = pd.read_csv('monthly_revenue_clean.csv')
    top_5 = pd.read_csv('top_5_analysis_clean.csv')
    rfm = pd.read_csv('rfm_clean.csv')
    geo = pd.read_csv('geo_clean.csv')

# --- SISI SIDEBAR ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/dicodingacademy/assets/main/logo.png", width=150)
    st.title("Opsi Filter & Navigasi")

    menu = st.selectbox(
        "Pilih Menu Utama:",
        ["Ringkasan Umum & Tren", "Kepuasan Produk", "Analisis RFM", "Peta Sebaran Geografis"]
    )

    st.markdown("--- ")
    st.markdown("**Informasi Pengembang:**")
    st.markdown("- **Nama**: Muhamad Ifsal Fadhilah")
    st.markdown("- **Email**: mifsalfadhilah26@gmail.com")

# --- MENU 1: RINGKASAN UMUM & TREN ---
if menu == "Ringkasan Umum & Tren":
    st.header("📈 Tren Penjualan & Performa Finansial")
    st.markdown("Pantau performa pendapatan bulanan platform e-commerce sepanjang tahun 2017.")

    # Menghitung Metrik Utama
    total_revenue = monthly_rev['total_revenue'].sum()
    avg_revenue = monthly_rev['total_revenue'].mean()
    peak_month = monthly_rev.loc[monthly_rev['total_revenue'].idxmax()]

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Total Pendapatan (2017)", value=f"${total_revenue:,.2f}")
    with col2:
        st.metric(label="Rata-rata Bulanan", value=f"${avg_revenue:,.2f}")
    with col3:
        st.metric(label="Bulan Penjualan Tertinggi", value=f"{peak_month['order_month']} (${peak_month['total_revenue']:,.2f})")

    st.markdown("--- ")

    # Interaktivitas: Memilih opsi warna grafik
    warna_tren = st.color_picker("Pilih Tema Warna Garis Tren:", "#1f77b4")

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(
        monthly_rev['order_month'].astype(str),
        monthly_rev['total_revenue'],
        marker='o',
        linewidth=2.5,
        color=warna_tren
    )
    for i, txt in enumerate(monthly_rev['total_revenue']):
        ax.annotate(f"${txt/1000:.1f}k", (monthly_rev['order_month'][i], monthly_rev['total_revenue'][i]), 
                    textcoords="offset points", xytext=(0,10), ha='center', fontsize=8, fontweight='semibold')

    ax.set_ylim(0, monthly_rev['total_revenue'].max() * 1.18)
    ax.set_xlabel("Bulan")
    ax.set_ylabel("Total Penjualan ($)")
    st.pyplot(fig)

    with st.expander("Tampilkan Tabel Data Tren"):
        st.dataframe(monthly_rev)

# --- MENU 2: KEPUASAN PRODUK ---
elif menu == "Kepuasan Produk":
    st.header("🛍️ Analisis Kepuasan Kategori Terlaris")
    st.markdown("Bandingkan volume penjualan (*barchart*) dengan tingkat kepuasan ulasan pelanggan (*linechart*).")

    # Interaktivitas: Filter Multi-select kategori produk
    kategori_pilihan = st.multiselect(
        "Filter Kategori Produk Terlaris:",
        options=top_5['product_category_name_english'].tolist(),
        default=top_5['product_category_name_english'].tolist()
    )

    filtered_top_5 = top_5[top_5['product_category_name_english'].isin(kategori_pilihan)]

    if not filtered_top_5.empty:
        fig, ax1 = plt.subplots(figsize=(10, 5))

        # Plot Bar (Sumbu Y 1)
        sns.barplot(x='product_category_name_english', y='sales_volume', data=filtered_top_5, ax=ax1, color='#85c1e9', alpha=0.9)
        ax1.set_ylabel('Volume Penjualan (Unit)', color='navy', fontweight='bold')
        ax1.set_xlabel('Kategori Produk')
        ax1.tick_params(axis='y', labelcolor='navy')

        # Plot Line (Sumbu Y 2)
        ax2 = ax1.twinx()
        sns.lineplot(x='product_category_name_english', y='average_review_score', data=filtered_top_5, ax=ax2, color='#e74c3c', marker='o', linewidth=3, markersize=8)
        ax2.set_ylabel('Rata-rata Skor Ulasan (1-5)', color='#e74c3c', fontweight='bold')
        ax2.tick_params(axis='y', labelcolor='#e74c3c')
        ax2.set_ylim(3.5, 4.5)

        st.pyplot(fig)
    else:
        st.warning("Silakan pilih minimal satu kategori untuk menampilkan visualisasi!")

# --- MENU 3: ANALISIS RFM ---
elif menu == "Analisis RFM":
    st.header("👥 Segmentasi Perilaku Pelanggan (RFM Analysis)")

    # Interaktivitas: Filter Segmen Pelanggan
    segmen_list = rfm['customer_segment'].unique().tolist()
    segmen_pilihan = st.multiselect(
        "Pilih Segmen Pelanggan yang Ingin Ditampilkan:",
        options=segmen_list,
        default=segmen_list
    )

    filtered_rfm = rfm[rfm['customer_segment'].isin(segmen_pilihan)]

    segment_counts = filtered_rfm['customer_segment'].value_counts().reset_index()
    segment_counts.columns = ['Segment', 'Count']

    col1, col2 = st.columns([2, 1])
    with col1:
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.barplot(x='Count', y='Segment', data=segment_counts, palette='viridis', hue='Segment', legend=False, ax=ax)
        for index, value in enumerate(segment_counts['Count']):
            ax.text(value + 50, index, f"{value}", va='center', fontweight='bold')
        st.pyplot(fig)

    with col2:
        st.markdown("**Informasi Segmen:**")
        st.write(f"Total Pelanggan Terfilter: **{len(filtered_rfm)}**")
        st.dataframe(segment_counts)

# --- MENU 4: SEBARAN GEOGRAFIS ---
elif menu == "Sebaran Geografis":
    st.header("🗺️ Peta Interaktif Sebaran Geografis Pelanggan")
    st.markdown("Memetakan konsentrasi pesanan di seluruh wilayah negara Brasil menggunakan visualisasi peta koordinat interaktif.")

    # Interaktivitas: Filter Slider Sampel Data Koordinat untuk mempercepat load peta
    jumlah_titik = st.slider("Pilih Jumlah Titik Koordinat yang Ditampilkan:", 1000, len(geo), 15000, step=1000)
    geo_sample = geo.sample(n=jumlah_titik, random_state=42)

    map_data = geo_sample.rename(columns={'geolocation_lat': 'lat', 'geolocation_lng': 'lon'})
    st.map(map_data, zoom=3)

    st.caption(f"Menampilkan sampel acak sebanyak {jumlah_titik} titik koordinat dari total {len(geo)} data geospasial." )
