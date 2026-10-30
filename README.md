# E-Commerce Performance Dashboard (2017) 📈

Selamat datang di proyek akhir analisis data E-Commerce Public Dataset. Proyek ini mencakup analisis tren transaksi, kepuasan pelanggan pada kategori produk terpopuler, analisis RFM pelanggan, serta visualisasi pemetaan geografis di Brasil sepanjang tahun 2017.

## 📝 Rangkuman Analisis & Insight Utama
- **Tren Finansial**: Pendapatan e-commerce tumbuh konsisten dari awal tahun ($120.3k pada Januari) hingga meledak drastis di bulan November mencapai puncak $1.01M karena pengaruh festival promosi *Black Friday*.
- **Kualitas vs Kuantitas**: Kategori perlengkapan rumah tangga (`bed_bath_table` dan `furniture_decor`) mencatatkan volume penjualan tertinggi (> 4.000 unit) namun mendapatkan rata-rata skor ulasan terendah (3.91). Berbanding terbalik dengan kategori `sports_leisure` dan `health_beauty` yang memiliki performa seimbang (penjualan tinggi & rating kepuasan > 4.13).
- **Profil RFM Pelanggan**: Mayoritas pelanggan tahun 2017 merupakan *Regular Customer* (44.3%) dan pelanggan satu kali beli yang pasif (*Hibernating/Churned* - 33.3%). Hanya 11.5% pelanggan yang tergolong dalam *Core High Spenders*.
- **Sebaran Geografis**: Sebagian besar pesanan terkonsentrasi di wilayah pesisir timur dan tenggara Brasil, khususnya di sekitar kota-kota besar seperti São Paulo dan Rio de Janeiro.

---

## 🖥️ Struktur Direktori Kerja
```text
├── dashboard/
│   ├── dashboard.py
│   ├── monthly_revenue_clean.csv
│   ├── top_5_analysis_clean.csv
│   ├── rfm_clean.csv
│   └── geo_clean.csv
├── data/
│   ├── customers_dataset.csv
│   ├── geolocation_dataset.csv
│   ├── order_items_dataset.csv
│   ├── order_payments_dataset.csv
│   ├── order_reviews_dataset.csv
│   ├── orders_dataset.csv
│   ├── product_category_name_translation.csv
│   ├── products_dataset.csv
│   └── sellers_dataset.csv
├── notebook.ipynb
├── README.md 
├── requirements.txt
└── url.txt 
```

---

## 🚀 Cara Menjalankan Dashboard Secara Lokal

### 1. Instalasi Library Dependensi
Buka terminal/command prompt komputer Anda, lalu jalankan perintah instalasi berikut:
```bash
pip install -r requirements.txt
```

### 2. Menjalankan Dashboard Streamlit
Masuk ke dalam folder tempat Anda menyimpan berkas `dashboard.py` dan seluruh file `.csv` bersih, kemudian eksekusi perintah berikut:
```bash
streamlit run dashboard\dashboard.py
```

atau

```bash
python -m streamlit run dashboard\dashboard.py
```


Secara otomatis, aplikasi dashboard interaktif akan terbuka di browser internet Anda pada alamat default `http://localhost:8501`!
