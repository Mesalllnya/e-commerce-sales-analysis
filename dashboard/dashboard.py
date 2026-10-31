import os
import datetime as dt

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

sns.set_theme(style="whitegrid")

st.set_page_config(page_title="E-Commerce 2017 Dashboard", page_icon="🛒", layout="wide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


@st.cache_data
def load_data():
    df = pd.read_csv(os.path.join(BASE_DIR, "main_data.csv"))
    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
    return df


main_df = load_data()

# SIDEBAR (FILTER)
with st.sidebar:
    st.title("🛒 Filter Data")

    min_date = main_df["order_purchase_timestamp"].min().date()
    max_date = main_df["order_purchase_timestamp"].max().date()

    date_range = st.date_input(
        "Rentang Tanggal",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    all_categories = sorted(main_df["product_category_name_english"].dropna().unique())
    selected_categories = st.multiselect(
        "Kategori Produk (kosong = semua)", options=all_categories
    )

    all_states = sorted(main_df["customer_state"].dropna().unique())
    selected_states = st.multiselect("State Pelanggan (kosong = semua)", options=all_states)

    top_n = st.slider("Jumlah Kategori Teratas", min_value=3, max_value=15, value=5)

    st.markdown("---")
    st.caption("**Muhamad Ifsal Fadhilah**  \nmifsalfadhilah26@gmail.com")

# date_input bisa mengembalikan 1 tanggal saat user baru memilih tanggal awal
if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = end_date = date_range[0] if isinstance(date_range, (tuple, list)) else date_range

mask = (
    (main_df["order_purchase_timestamp"].dt.date >= start_date)
    & (main_df["order_purchase_timestamp"].dt.date <= end_date)
)
if selected_categories:
    mask &= main_df["product_category_name_english"].isin(selected_categories)
if selected_states:
    mask &= main_df["customer_state"].isin(selected_states)

df = main_df[mask].copy()

# ---------------------------------------------------------------- HEADER
tahun_min = main_df["order_purchase_timestamp"].dt.year.min()
tahun_max = main_df["order_purchase_timestamp"].dt.year.max()
rentang_tahun = str(tahun_min) if tahun_min == tahun_max else f"{tahun_min}-{tahun_max}"
st.title(f"Dashboard Analisis E-Commerce {rentang_tahun}")
st.caption(f"Periode: {start_date} s.d. {end_date}  |  {len(df):,} item transaksi terpilih")

if df.empty:
    st.warning("Tidak ada data untuk filter yang dipilih. Silakan ubah filter di sidebar.")
    st.stop()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue", f"${df['price'].sum():,.0f}")
col2.metric("Total Pesanan", f"{df['order_id'].nunique():,}")
col3.metric("Total Pelanggan", f"{df['customer_id'].nunique():,}")
col4.metric("Rata-rata Review", f"{df['review_score'].mean():.2f} / 5")

# PERTANYAAN 1: TREN REVENUE
st.subheader("Pertanyaan 1: Tren Total Penjualan Bulanan")

monthly = (
    df.groupby(df["order_purchase_timestamp"].dt.to_period("M"))["price"]
    .sum()
    .reset_index()
)
monthly.columns = ["month", "revenue"]
monthly["month"] = monthly["month"].astype(str)

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(monthly["month"], monthly["revenue"], marker="o", linewidth=2.5, color="#1f77b4")
for x, y in zip(monthly["month"], monthly["revenue"]):
    ax.annotate(f"${y/1000:.1f}k", (x, y), textcoords="offset points", xytext=(0, 10),
                ha="center", fontsize=9)
ax.set_ylim(0, monthly["revenue"].max() * 1.18)
ax.set_xlabel("Bulan")
ax.set_ylabel("Total Penjualan ($)")
plt.xticks(rotation=45)
st.pyplot(fig)

low = monthly.loc[monthly["revenue"].idxmin()]
high = monthly.loc[monthly["revenue"].idxmax()]
st.info(
    f"Revenue terendah pada **{low['month']}** (${low['revenue']:,.0f}), "
    f"tertinggi pada **{high['month']}** (${high['revenue']:,.0f})."
)

# PERTANYAAN 2: KEPUASAN
st.subheader(f"Pertanyaan 2: Volume Penjualan vs Kepuasan pada Top {top_n} Kategori")

cat = (
    df.groupby("product_category_name_english")
    .agg(sales_volume=("order_item_id", "count"), avg_review=("review_score", "mean"))
    .sort_values("sales_volume", ascending=False)
    .head(top_n)
    .reset_index()
)

fig, ax1 = plt.subplots(figsize=(12, 5))
sns.barplot(x="product_category_name_english", y="sales_volume", data=cat, ax=ax1,
            color="#85c1e9")
ax1.set_xlabel("Kategori Produk")
ax1.set_ylabel("Volume Penjualan (Unit)", color="navy")
plt.setp(ax1.get_xticklabels(), rotation=30, ha="right")
for p in ax1.patches:
    ax1.annotate(f"{int(p.get_height())}", (p.get_x() + p.get_width() / 2, p.get_height()),
                 ha="center", va="bottom", fontsize=9, fontweight="bold")

ax2 = ax1.twinx()
ax2.plot(cat["product_category_name_english"], cat["avg_review"], color="#e74c3c",
         marker="o", linewidth=3, markersize=8)
ax2.set_ylabel("Rata-rata Skor Ulasan (1-5)", color="#e74c3c")
ax2.set_ylim(1, 5)
ax2.grid(False)
for x, y in zip(cat["product_category_name_english"], cat["avg_review"]):
    ax2.annotate(f"{y:.2f}", (x, y), textcoords="offset points", xytext=(0, 10),
                 ha="center", fontweight="semibold")
st.pyplot(fig)

# RFM
st.subheader("Analisis Lanjutan: Segmentasi Pelanggan (RFM)")

ref_date = df["order_purchase_timestamp"].max() + dt.timedelta(days=1)
rfm = (
    df.groupby("customer_id")
    .agg(
        recency=("order_purchase_timestamp", lambda x: (ref_date - x.max()).days),
        frequency=("order_id", "nunique"),
        monetary=("price", "sum"),
    )
    .reset_index()
)

# rank(method="first") mencegah error qcut saat nilai duplikat / data sedikit
rfm["r_score"] = pd.qcut(rfm["recency"].rank(method="first"), 3, labels=[3, 2, 1]).astype(int)
rfm["m_score"] = pd.qcut(rfm["monetary"].rank(method="first"), 3, labels=[1, 2, 3]).astype(int) \
    if len(rfm) >= 3 else 1


def segment(row):
    if row["r_score"] == 3 and row["m_score"] == 3:
        return "Core - Recent & High Spender"
    if row["r_score"] == 1:
        return "Hibernating / Churned"
    if row["m_score"] == 3:
        return "High Value Target"
    return "Regular Customer"


if len(rfm) >= 3:
    rfm["segment"] = rfm.apply(segment, axis=1)
    seg = rfm["segment"].value_counts().reset_index()
    seg.columns = ["Segment", "Count"]

    c1, c2 = st.columns([2, 1])
    with c1:
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.barplot(x="Count", y="Segment", data=seg, palette="viridis", hue="Segment",
                    legend=False, ax=ax)
        for i, v in enumerate(seg["Count"]):
            ax.text(v, i, f" {v} ({v / len(rfm) * 100:.1f}%)", va="center", fontweight="semibold")
        ax.set_xlim(0, seg["Count"].max() * 1.25)
        st.pyplot(fig)
    with c2:
        st.metric("Rata-rata Recency (hari)", f"{rfm['recency'].mean():.0f}")
        st.metric("Rata-rata Monetary ($)", f"{rfm['monetary'].mean():,.2f}")
else:
    st.info("Data terlalu sedikit untuk segmentasi RFM. Perluas filter.")

# GEO
st.subheader("Analisis Lanjutan: Sebaran Geografis Pelanggan")

geo = df.dropna(subset=["geolocation_lat", "geolocation_lng"])
if not geo.empty:
    st.map(
        geo.rename(columns={"geolocation_lat": "lat", "geolocation_lng": "lon"})[["lat", "lon"]],
        zoom=3,
    )
    top_states = df.groupby("customer_state")["order_id"].nunique().sort_values(ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.barplot(x=top_states.index, y=top_states.values, color="#1f77b4", ax=ax)
    ax.set_xlabel("State")
    ax.set_ylabel("Jumlah Pesanan")
    ax.set_title("10 State dengan Pesanan Terbanyak")
    st.pyplot(fig)
else:
    st.info("Tidak ada data koordinat untuk filter ini.")

st.caption("Proyek Analisis Data — Dicoding | Muhamad Ifsal Fadhilah")
