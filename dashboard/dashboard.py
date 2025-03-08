import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns



# Load dataset
hour = pd.read_csv("hour.csv")
day = pd.read_csv("day.csv")

# Ubah tipe data dteday menjadi date time
day['dteday'] = pd.to_datetime(day['dteday'])
hour['dteday'] = pd.to_datetime(hour['dteday'])

# Membuat subset dataframe yang dibutuhkan (jumlah frekuensi peminjaman bds jenis pengguna)
users_frequency_prop = hour[['casual', 'registered']].sum() / hour['cnt'].sum()
users_frequency_prop = users_frequency_prop.to_frame().rename(columns={0: 'Proportion'})

# Menghitung proporsi jumlah pengguna Unik
unique_users_count = hour[['casual', 'registered']].nunique()
unique_users_prop = unique_users_count / unique_users_count.sum()
unique_users_prop = unique_users_prop.to_frame().rename(columns={0: 'Proportion'})

# Subset dataframe cuaca dan count
hour_subset = hour[['cnt', 'temp', 'atemp', 'hum', 'windspeed']]

# Mapping variabel season dan weather ke dalam variabel baru yang berisi label nama lengkap untuk tiap-tiap kategori
season_mapping = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
hour["season_label"] = hour["season"].map(season_mapping)
day["season_label"] = day["season"].map(season_mapping)

weather_mapping = {
    1: "Clear/Partly Cloudy",
    2: "Mist/Cloudy",
    3: "Light Rain/Snow",
    4: "Heavy Rain/Snow/Thunderstorm"
}

hour["weathersit_name"] = hour["weathersit"].map(weather_mapping)
day["weathersit_name"] = day["weathersit"].map(weather_mapping)

# Korelasi faktor lingkungan dan jumlah penyewa
weather_and_count_corr = hour_subset.corr()

# DASHBOARD
st.title("🚲 Dashboard Penyewaan Sepeda")
st.markdown("##### **Dibuat oleh: Putri Sekar Ayu**")

# 1. Total Penyewaan Sepeda per Hari
st.subheader("📊 Penyewaan Sepeda per Hari")

days_mapping = {0: "Minggu", 1: "Senin", 2: "Selasa", 3: "Rabu", 4: "Kamis", 5: "Jumat", 6: "Sabtu"}
hour["weekday_label"] = hour["weekday"].map(days_mapping)
order = ["Minggu", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"]
hour["weekday_label"] = pd.Categorical(hour["weekday_label"], categories=order, ordered=True)
total_per_weekday = hour.groupby("weekday_label")["cnt"].sum().reindex(order)

# visualisasi
fig, ax = plt.subplots(figsize=(13, 5))
total_per_weekday.plot(kind="barh", color="blue", edgecolor="black", ax=ax)

for index, value in enumerate(total_per_weekday):
    ax.text(value + 500, index, str(value), va="center", fontsize=10)

ax.set_xlabel("Jumlah Penyewaan")
ax.set_ylabel("Hari")
ax.set_title("Total Penyewaan Sepeda per Hari")
st.pyplot(fig)

# interpretasi
with st.expander("Penjelasan"):
    st.markdown(
        """
        - Dalam dua tahun terakhir, jumlah penyewaan sepeda paling banyak ada di hari Kamis dan Jumat, dimana hari Kamis mencapai 485.395 penyewaan secara keseluruhan dalam 2 tahun terakhir sedangkan Jumat mencapai 487.790 secara keseluruhan.
        """
    )
st.write("")
st.write("")

# 2. Tren Penyewaan Sepeda (Line Chart)
st.subheader("📈 Tren Penyewaan Sepeda per Jam untuk Hari Jumat")

# filter data untuk hari Jumat (weekday == 5)
df_jumat = hour[hour["weekday"] == 5].groupby("hr")["cnt"].sum()

# plot dengan Matplotlib
fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(df_jumat.index, df_jumat.values, marker="o", linestyle="-", color="blue")
ax.set_title("Kenaikan dan Penurunan Jumlah Penyewaan Sepeda (Jumat)")
ax.set_ylabel("Jumlah Penyewaan")
ax.set_xticks(range(0, 24))
ax.grid(axis="y", linestyle="--", alpha=0.7)
ax.legend()

st.pyplot(fig)

# interpretasi
with st.expander("Penjelasan"):
    st.markdown(
        """
        - Peak hour terjadi pada pukul 08:00 AM, yang kemungkinan besar bertepatan dengan jam berangkat kerja. Selain itu, terjadi lonjakan kembali pada pukul 05:00 PM dan 06:00 PM, yang dapat diasumsikan sebagai waktu pulang kerja.
        """
    )
st.write("")
st.write("")


# 3. Perbandingan Casual vs Registered Users
st.subheader("👥 Perbandingan Casual vs Registered Users")

col1, col2 = st.columns(2)

with col1:
    fig1, ax1 = plt.subplots(figsize=(4, 4))
    ax1.pie(users_frequency_prop.squeeze(), labels=['Casual Users', 'Registered Users'], autopct='%1.1f%%', 
            colors=['orange', 'blue'], startangle=140)
    ax1.set_title("Frekuensi Penyewaan Sepeda\n Tahun 2011-2012", fontsize=14)
    st.pyplot(fig1)

with col2:
    fig2, ax2 = plt.subplots(figsize=(4, 4))
    ax2.pie(unique_users_prop.squeeze(), labels=['Casual Users', 'Registered Users'], autopct='%1.1f%%', 
            colors=['orange', 'blue'], startangle=140)
    ax2.set_title("Jumlah Users Penyewaan Sepeda \n Tahun 2011-2012", fontsize=14)  
    st.pyplot(fig2)

with st.expander("Penjelasan"):
    st.write("""
    - Selama tahun 2011-2012, sekitar 81.2% dari total aktivitas penyewaan sepeda dilakukan oleh Registered Users dan 18.8% sisanya dilakukan oleh Casual Users.
    - Pada tahun 2011-2012, sebanyak 70.7% dari seluruh pengguna penyewaan sepeda berasal dari kategori Registered Users, sementara sisanya merupakan Casual Users (19.7%).
    """)
st.write("")
st.write("")


# 4. Tren Penyewaan Sepeda dalam 2 Tahun Terakhir (2011 - 2013)
st.subheader("📈 Tren Jumlah Pelanggan Selama 2 Tahun Terakhir (2011-2013)")

fig, ax = plt.subplots(figsize=(15, 5))  # Ukuran tetap

# Hitung jumlah penyewaan maksimum per bulan
monthly_counts = day['cnt'].groupby(day['dteday']).max()

# Buat line chart maksimum penyewaan per bulan
ax.scatter(monthly_counts.index, monthly_counts.values, c="#90CAF9", s=10, marker='o')
ax.plot(monthly_counts.index, monthly_counts.values)

ax.set_xlabel('Bulan')
ax.set_ylabel('Jumlah')
ax.set_title('Tren Jumlah Pelanggan Selama 2 Tahun Terakhir\n(2011-2013)', fontsize=15)

st.pyplot(fig)

with st.expander("Penjelasan"):
    st.write("""
    - Jumlah penyewa sepeda cenderung fluktuatif setiap bulannya. Namun, secara keseluruhan, dalam dua tahun terakhir, tren penyewaan sepeda menunjukkan peningkatan, dengan pola kenaikan signifikan pada pertengahan tahun.
    """)
st.write("")
st.write("")

# 5. Korelasi Faktor Lingkungan dan Jumlah Penyewa
st.subheader("🔍 Korelasi Faktor Lingkungan dan Jumlah Penyewa") 

# Grafik Correlation Heat Map
st.markdown("##### Heatmap Korelasi Faktor Cuaca dan Jumlah Penyewa")
fig1, ax1 = plt.subplots(figsize=(10, 6))
sns.heatmap(weather_and_count_corr, annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5, ax=ax1)
st.pyplot(fig1)

# Grafik scatter 
st.markdown("##### Scatter Plot Korelasi Variabel dengan Penyewaan Sepeda")
fig2 = plt.figure(figsize=(12, 10))
for i, col in enumerate(['temp', 'atemp', 'hum', 'windspeed'], 1):
    ax = fig2.add_subplot(2, 2, i)
    sns.scatterplot(x=hour_subset[col], y=hour_subset['cnt'], alpha=0.5, ax=ax)
    ax.set_xlabel(col.capitalize())
    ax.set_ylabel("Penyewaan Sepeda (cnt)")
    ax.set_title(f"Korelasi {col.capitalize()} vs Jumlah Penyewaan")
plt.tight_layout()
st.pyplot(fig2)

with st.expander("Penjelasan"):
    st.markdown("""
    - Korelasi antara jumlah penyewaan sepeda dengan **Humidity**, **Windspeed**, **Temperature**, dan **Atemp** cenderung berada pada tingkat rendah hingga sedang.
    - Variabel suhu (*Temperature* maupun *Atemp*) berkorelasi positif dengan jumlah penyewaan sepeda. Artinya, semakin tinggi suhu di suatu tempat, maka kecenderungan penyewaan sepeda akan meningkat.
    - Sebaliknya, variabel **Humidity** berkorelasi negatif dengan jumlah penyewaan sepeda, yang berarti semakin rendah kelembapan di hari tersebut, maka jumlah penyewaan sepeda cenderung meningkat.
    - Untuk **Windspeed** (kecepatan angin), semakin rendah kecepatan angin di hari itu, maka jumlah penyewaan sepeda akan meningkat.
    """)
st.write("")
st.write("")

# 6. Analisis lanjutan (Klustering)
# Binning suhu
# Rentang: Dingin: <15°C, Sedang: 15°C – 30°C, Ekstrem: >30°C
# Karena 0-1 adalah hasil normalisasi dari 0-41°C,
# maka rentang pada skala 0-1:
# Dingin: 0 - 0.366   (0-15°C)
# Sedang: 0.366 - 0.732 (15-30°C)
# Ekstrem: 0.732 - 1.0  (>30°C)

bins = [0, 0.366, 0.732, 1.0]
labels = ['Dingin', 'Sedang', 'Ekstrem']

day['temp_category'] = pd.cut(day['temp'], bins=bins, labels=labels, include_lowest=True)

# --- Hitung jumlah hari untuk tiap kategori suhu ---
temp_counts = day["temp_category"].value_counts().sort_index()

# Warna dasar: lightblue, highlight kategori dengan jumlah maksimum dengan warna biru tua
base_color = "lightblue"  
highlight_color = "#003366"
highlight_index = temp_counts.idxmax()  # Kategori dengan jumlah hari terbanyak

# Buat daftar warna untuk tiap kategori
bar_colors = [
    highlight_color if category == highlight_index else base_color
    for category in temp_counts.index
]

# Plot Bar Chart Kategori Suhu
st.subheader("🌡️ [ANALISIS LANJUTAN] Binning/Pengkategorian Suhu")

fig, ax = plt.subplots(figsize=(6, 4))
sns.barplot(x=temp_counts.index, y=temp_counts.values, palette=bar_colors, edgecolor="black", ax=ax)
ax.set_title("Jumlah Hari berdasarkan Kategori Suhu", fontsize=12)
ax.set_xlabel("Kategori Suhu", fontsize=10)
ax.set_ylabel("Jumlah Hari", fontsize=10)
for i, v in enumerate(temp_counts):
    ax.text(i, v + 2, str(v), ha="center", fontsize=10, fontweight="bold")

st.pyplot(fig)

with st.expander("Penjelasan"):
    st.markdown("""
    **Rentang Binning:**
    - **Dingin:** 0 – 0.366, yang merupakan hasil normalisasi dari suhu **< 15°C**.
    - **Sedang:** 0.366 – 0.732, yang merupakan hasil normalisasi dari suhu **15°C – 30°C**.
    - **Ekstrem:** 0.732 – 1.0, yang merupakan hasil normalisasi dari suhu **> 30°C**.
    
    **Interpretasi:**  
    Hari dimana para penyewa melakukan penyewaan sepeda banyak dilakukan di hari dengan suhu **sedang**, yang dalam rentang normalisasi berada pada angka **0.366-0.732** atau pada rentang biasa di angka **15-30 derajat Celsius**.
    """)

