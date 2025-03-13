import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Konfigurasi Tampilan
st.set_page_config(page_title="Analisis Penyewaan Sepeda", layout="wide")

# Load Dataset
@st.cache_data
def load_data():

    # Local
    # df_hour = pd.read_csv("../data/hour.csv")  # Dataset per jam
    # df_day = pd.read_csv("../data/day.csv")    # Dataset per hari

    # Apabila relative path tidak berjalan
    df_hour = pd.read_csv("data/hour.csv")  # Dataset per jam
    df_day = pd.read_csv("data/day.csv")    # Dataset per hari

    return df_hour, df_day

df_hour, df_day = load_data()

# Data Preprocessing
df_hour['dteday'] = pd.to_datetime(df_hour['dteday'])
df_day['dteday'] = pd.to_datetime(df_day['dteday'])

# Mapping nama hari
day_map = {0: "Minggu", 1: "Senin", 2: "Selasa", 3: "Rabu", 
           4: "Kamis", 5: "Jumat", 6: "Sabtu"}

df_hour['weekday'] = df_hour['weekday'].map(day_map)
df_day['weekday'] = df_day['weekday'].map(day_map)

# Tabel proporsi user
users_frequency_prop = df_hour[['casual', 'registered']].sum() / df_hour['cnt'].sum()
users_frequency_prop = users_frequency_prop.to_frame().rename(columns={0: 'Proportion'})

unique_users_count = df_hour[['casual', 'registered']].nunique()
unique_users_prop = unique_users_count / unique_users_count.sum()
unique_users_prop = unique_users_prop.to_frame().rename(columns={0: 'Proportion'})

# Subset data untuk cuaca
hour_subset = df_hour[['cnt', 'temp', 'atemp', 'hum', 'windspeed']]

# Mapping angka ke nama musim
season_mapping = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}

# Buat variabel baru di DataFrame hour dan day
df_hour["season_label"] = df_hour["season"].map(season_mapping)
df_day["season_label"] = df_day["season"].map(season_mapping)

# Binning suhu temp
# Dingin: < 15°C, Sedang: 15°C – 30°C, Ekstrem: > 30°C. Hasil dibawah merupakan hasil perkalian dari temperature normalisasi
bins = [0, 0.366, 0.732, 1.0]
labels = ['Dingin', 'Sedang', 'Ekstrem']

# Simpan hasil binning ke kolom baru
df_day['temp_category'] = pd.cut(df_day['temp'], bins=bins, labels=labels, include_lowest=True)


# Sidebar Navigation
st.sidebar.markdown("<h1 style='color: darkblue; font-weight: bold;'>Dashboard Penyewaan Sepeda</h1>", unsafe_allow_html=True)
st.sidebar.markdown("##### Made by: Putri Sekar Ayu")

if 'menu' not in st.session_state:
    st.session_state.menu = "interaktif"

if st.sidebar.button("📊 Dashboard Interaktif"):
    st.session_state.menu = "interaktif"
if st.sidebar.button("📊 Statistik Penyewaan Sepeda"):
    st.session_state.menu = "penyewaan"
if st.sidebar.button("👥 Statistik Pengguna"):
    st.session_state.menu = "user"
if st.sidebar.button("☀️ Analisis Cuaca"):
    st.session_state.menu = "cuaca"

# Konten Halaman
if st.session_state.menu == "interaktif":
    st.title("Dashboard Penyewaan Sepeda")

    fil1, fil2 = st.columns([1, 1])  # Atur lebar kolom agar seimbang

    with fil1:
        selected_dates = st.date_input(
            "Pilih Rentang Tanggal",
            [df_day['dteday'].min(), df_day['dteday'].max()],
            min_value=df_day['dteday'].min(),
            max_value=df_day['dteday'].max()
        )

    with fil2:
        selected_season = st.multiselect(
            "Pilih Musim",
            df_day['season_label'].unique(),
            default=df_day['season_label'].unique()
        )


    # Filter data berdasarkan input
    filtered_df = df_day[
        (df_day['dteday'] >= pd.Timestamp(selected_dates[0])) &
        (df_day['dteday'] <= pd.Timestamp(selected_dates[1])) &
        (df_day['season_label'].isin(selected_season))
    ]

    # Hitung rata-rata penyewaan per hari
    grouped_df = filtered_df.groupby("weekday", observed=True)["cnt"].mean().reset_index()

    # Urutkan sesuai urutan hari
    ordered_days = ["Minggu", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"]
    grouped_df["weekday"] = pd.Categorical(grouped_df["weekday"], categories=ordered_days, ordered=True)
    grouped_df = grouped_df.sort_values("weekday")

    # Tampilkan informasi rentang tanggal yang dipilih
    st.markdown("<br>", unsafe_allow_html=True)

    st.write(f"**Data dari {selected_dates[0]} hingga {selected_dates[1]}**")

    # Visualisasi dengan bar plot
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(data=grouped_df, x="weekday", y="cnt", ax=ax, color="skyblue")
    ax.set_title("Rata-rata Penyewaan Sepeda per Hari dalam Seminggu")
    ax.set_ylabel("Jumlah Penyewaan")
    ax.set_xlabel("")
    st.pyplot(fig)

if st.session_state.menu == "penyewaan":
    #1. Visualisasi rata-rata penyewa harian
    st.subheader("📊 Rata-rata Penyewaan Sepeda per Hari")

    # Menghitung rata-rata penyewaan per hari
    avg_per_weekday = df_hour.groupby("weekday")["cnt"].mean()

    # Pastikan urutan hari Minggu - Sabtu
    order = ["Minggu", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"]
    avg_per_weekday = avg_per_weekday.reindex(order)

    # Menentukan dua hari dengan penyewaan tertinggi
    top2_days = avg_per_weekday.nlargest(2).index

    colors = ["darkblue" if day in top2_days else "skyblue" for day in avg_per_weekday.index]

    # Membuat bar chart horizontal
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.barh(avg_per_weekday.index, avg_per_weekday, color=colors, edgecolor="black")

    # Menambahkan label di dalam bar
    for index, value in enumerate(avg_per_weekday):
        ax.text(value, index, f"{value:.2f}", va="center", fontsize=10, color="black")

    ax.set_ylabel("")
    ax.set_title("Rata-rata Penyewaan Sepeda per Hari", fontsize=10, fontweight="bold")
    st.pyplot(fig)

    with st.expander("📌 Penjelasan", expanded=True):
        st.markdown(f"""
        Dalam dua tahun terakhir, jumlah penyewaan sepeda paling banyak ada di hari **Kamis dan Jumat**, dimana hari Kamis mencapai 196,44 orang atau sekitar 196-197 orang penyewaan secara keseluruhan dalam 2 tahun terakhir sedangkan Jumat mencapai 196,14 secara keseluruhan. Rentang jumlah peminjam sepeda mirip dengan perbedaan yang sangat kecil. 
        """)
    

    st.markdown("<br>", unsafe_allow_html=True)

    #2. Visualisasi tren penyewa dalam sehari tiap jam    
    st.subheader("⏰ Pola Peminjaman Sepeda per Jam")

    # Pilih hari untuk ditampilkan grafiknya
    selected_day = st.selectbox("Pilih Hari", list(day_map.values()), index=0)

    # Df sementara untuk hari terpilih
    df_selected_day = df_hour[df_hour["weekday"] == selected_day].groupby("hr")["cnt"].sum()

    # Plot
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(df_selected_day.index, df_selected_day.values, marker="o", linestyle="-", color="blue", label=selected_day)
    ax.set_title(f"Kenaikan dan Penurunan Jumlah Penyewaan Sepeda ({selected_day})", fontsize=14)
    ax.set_xlabel("Jam dalam Sehari")
    ax.set_xticks(range(0, 24))
    ax.grid(axis="y", linestyle="--", alpha=0.7)

    st.pyplot(fig)

    # Penjelasan
    with st.expander("📌 Penjelasan", expanded=True):
        st.markdown(f"""
        - Grafik ini menunjukkan **pola penyewaan sepeda setiap jam pada hari {selected_day}**.
        - **Jam sibuk** dapat diidentifikasi dari lonjakan penyewaan yang signifikan.
        - Data ini berguna untuk memahami tren penggunaan sepeda berdasarkan waktu.
        """)
    
    with st.expander("**📌 Rangkuman Grafik**", expanded=True):
        st.markdown(f"""
        - Hari-hari kerja Senin sampai Jumat memiliki pola yang mirip, dimana *peak hour* ada di jam kerja 08.00 AM dan jam pulang kerja 05.00 PM
        - Namun, pada hari *weekend* Sabtu dan Minggu, *peak hour* peminjaman sepeda ada di rentang jam 12.00 AM - 05.00 PM. Hal ini menjadi wajar karena diasumsikan pada *weekend* orang-orang cenderung meminjam sepeda pada siang-sore hari untuk liburan/jalan-jalan.
        """)


    st.markdown("<br>", unsafe_allow_html=True)


    #3. Visualisasi tren penyewaan sepeda 2 tahun terakhir
    st.subheader("📈 Tren Jumlah Pelanggan Selama 2 Tahun Terakhir")

    
    fig, ax = plt.subplots(figsize=(10, 5))

    # Hitung jumlah penyewaan maksimum per bulan
    monthly_counts = df_day['cnt'].groupby(df_day['dteday']).max()

    # Buat line chart maksimum penyewaan per bulan
    ax.scatter(monthly_counts.index, monthly_counts.values, c="#90CAF9", s=10, marker='o')
    ax.plot(monthly_counts.index, monthly_counts.values)

    ax.set_xlabel('Bulan')
    ax.set_ylabel('Jumlah')
    ax.set_title('Tren Jumlah Pelanggan Selama 2 Tahun Terakhir (2011-2013)', fontsize=12)

    st.pyplot(fig)

    with st.expander("**📌 Rangkuman Grafik**", expanded=True):
        st.markdown(f"""
        Jumlah penyewa sepeda cenderung fluktuatif setiap bulannya. Namun, secara keseluruhan, dalam dua tahun terakhir, tren penyewaan sepeda menunjukkan peningkatan, dengan pola kenaikan signifikan pada pertengahan tahun.
        """)


elif st.session_state.menu == "user":

    # 1. Perbandingan Casual dan Registered User
    st.subheader("👥 Perbandingan Casual vs Registered Users")
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    colors = ['#FFAA33', '#3399FF'] 
    edge_color = '#444444'

    with col1:
        fig1, ax1 = plt.subplots(figsize=(6, 6))
        wedges, texts, autotexts = ax1.pie(unique_users_prop.squeeze(), labels=['Casual Users', 'Registered Users'], 
                                        autopct='%1.1f%%', colors=colors, startangle=140, 
                                        wedgeprops={'edgecolor': edge_color, 'linewidth': 1.2})
        ax1.set_title('Perbandingan Jumlah Casual dan Registered Users \n(2011-2012)',fontsize=12, fontweight='bold')
        st.pyplot(fig1)

    with col2:
        fig2, ax2 = plt.subplots(figsize=(6, 6))
        wedges, texts, autotexts = ax2.pie(users_frequency_prop.squeeze(), labels=['Casual Users', 'Registered Users'], 
                                        autopct='%1.1f%%', colors=colors, startangle=140, 
                                        wedgeprops={'edgecolor': edge_color, 'linewidth': 1.2})
        ax2.set_title('Frekuensi Penyewaan Sepeda oleh Casual vs Registered Users \n(2011-2012)', fontsize=12, fontweight='bold')
        st.pyplot(fig2)
    
    with st.expander("📌 **Rangkuman Grafik**", expanded=True):
        st.markdown("""
        Pada tahun 2011-2012, sebanyak 70.7% dari seluruh pengguna penyewaan sepeda berasal dari kategori Registered Users, sementara sisanya merupakan Casual Users (19.7%). Dan selama tahun 2011-2012, sekitar 81.2% dari total aktivitas penyewaan sepeda dilakukan oleh Registered Users.
        """)
    

elif st.session_state.menu == "cuaca":
    st.subheader("☀️ Analisis Korelasi Faktor Cuaca terhadap Penyewaan Sepeda")

    label_mapping = {
    "temp": "Suhu Udara (°C)",
    "atemp": "Suhu yang Dirasakan (°C)",
    "hum": "Kelembaban Udara (%)",
    "windspeed": "Kecepatan Angin (km/jam)"
    }

    # Membuat figure untuk scatter plot
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))  # Atur ukuran figure agar proporsional

    # Looping untuk membuat scatter plot dalam grid 2x2
    for ax, col in zip(axes.flatten(), label_mapping.keys()):
        sns.scatterplot(x=hour_subset[col], y=hour_subset['cnt'], alpha=0.5, ax=ax)
        ax.set_xlabel(label_mapping[col])  # Ganti label dengan nama yang lebih deskriptif
        ax.set_ylabel("Jumlah Penyewaan Sepeda (cnt)")
        ax.set_title(f"Korelasi {label_mapping[col]} vs Penyewaan")

    plt.subplots_adjust(hspace=0.4, wspace=0.3)

    st.pyplot(fig)

    with st.expander("📌 **Rangkuman Grafik**", expanded=True):
        st.markdown("""
        - Dilihat dari sebarannya, korelasi antara jumlah penyewaan sepeda dengan Humidity, Windspeed, Temperature, dan Atemp cenderung berada pada tingkat rendah hingga sedang.
        - Variabel suhu (baik Temp maupun Atemp) berkorelasi positif dengan jumlah penyewaan sepeda. Artinya, semakin tinggi suhu di suatu tempat, maka kecenderungan penyewaan sepeda akan meningkat
        - Sedangkan itu, variabel humidity berkorelasi negatif dengan jumlah penyewaan sepeda, yang berarti semakin rendah humidity/kelembapan di hari itu, maka jumlah penyewaan sepeda akan meningkat.
        - Sedangkan untuk windspeed/kecepatan angin, semakin rendah kecepatan angin di hari itu, maka jumlah penyewaan sepeda akan meningkat.
        """)
    

    st.markdown("<br>", unsafe_allow_html=True)


    # 2. Perbandingan penyewaan sepeda antar musim
    st.subheader("📊 Perbandingan Rata-rata Penyewaan Sepeda dalam Berbagai Musim")

    # Cari kategori musim dengan jumlah penyewaan tertinggi
    avg_rental_per_season = df_day.groupby("season_label")["cnt"].sum()
    max_season = avg_rental_per_season.idxmax()

    # Buat mapping warna berdasarkan musim tertinggi
    color_mapping = {season: "darkblue" if season == max_season else "lightblue" for season in avg_rental_per_season.index}

    # Buat figure
    fig, ax = plt.subplots(figsize=(10, 6))

    # Buat barplot dengan warna yang sudah sesuai urutan di dataset
    sns.barplot(
        data=df_day,
        x="season_label",
        y="cnt",
        estimator=sum,  # Gunakan total penyewaan
        edgecolor="black",
        errorbar=None,
        order=avg_rental_per_season.index,  # Pastikan urutan sesuai dengan yang dihitung
        palette=color_mapping,  # Terapkan warna dengan mapping
        ax=ax
    )

    # Tambahkan label di atas setiap batang
    for p in ax.patches:
        ax.annotate(
            f"{p.get_height():,.0f}",  # Format angka tanpa desimal dengan pemisah ribuan
            (p.get_x() + p.get_width() / 2, p.get_height()),  # Posisi di tengah bar
            ha="center",  # Horizontal align di tengah
            va="bottom",  # Vertical align di atas batang
            fontsize=11,
            fontweight="bold",
            color="black"
        )

    ax.set_xlabel("Musim", fontsize=10, labelpad=15)  # Spasi ekstra untuk label X
    ax.set_title("Sebaran Jumlah Penyewaan Sepeda berdasarkan Musim", fontsize=12, pad=15)

    # Tampilkan plot di Streamlit
    st.pyplot(fig)

    with st.expander("📌 **Rangkuman Grafik**", expanded=True):
        st.markdown("""
        - Dari empat musim dalam 2 tahun terakhir, penyewaan sepeda terbanyak dilakukan pada musim gugur dengan angka yang sangat besar yakni 1,061 juta kali penyewaan. Hal ini berdasar karena kondisi cuaca nya cocok untuk beraktivitas di luar.
        - Sedangkan untuk jumlah penyewaan terkecil ada pada musim semi karena pada musim ini cenderung ada perubahan cuaca yang ekstrem seperti terjadinya hujan lebat sehingga orang-orang lebih memilih untuk tidak banyak beraktivitas di luar.
        """)

    # 3. Perbandingan penyewaan sepeda berdasarkan Suhuh
    st.subheader("📊 [ANALISIS BINNING] Perbandingan Rata-rata Penyewaan Sepeda dalam Berbagai Kelompok Suhu")

    # Hitung jumlah hari dalam setiap kategori suhu
    temp_counts = df_day.set_index("temp_category")["cnt"].sort_index()

    highlight_index = temp_counts.idxmax()  

    # Buat daftar warna: biru biasa, kecuali kategori tertinggi pakai biru tua
    bar_colors = ["lightblue" if category == highlight_index else "darkblue" for category in temp_counts.index]

    # Buat figure
    fig, ax = plt.subplots(figsize=(3, 3), dpi = 50)

    # Plot bar chart
    sns.barplot(x=temp_counts.index, y=temp_counts.values, palette=bar_colors, edgecolor="black", ax=ax, errorbar=None, width=0.4)

    # Tambahkan label
    ax.set_title("Jumlah Hari berdasarkan Kategori Suhu", fontsize=7)
    ax.set_xlabel("", fontsize=5)

    # Streamlit Show
    st.pyplot(fig, use_container_width=False)  # Hindari auto-resize

    with st.expander("ℹ️ Penjelasan Kategori Suhu", expanded = True):
        st.write("""
        Suhu dalam dataset awalnya telah dinormalisasi dalam rentang **0–1** berdasarkan nilai maksimum **40°C**.  
        Untuk mendapatkan kategori suhu, nilai suhu yang telah dinormalisasi dikalikan kembali dengan **40**,  
        kemudian dikelompokkan ke dalam tiga kelas sebagai berikut:

        - **Dingin**: Suhu < **15°C** (`temp_normalized * 40 < 15`)  
        - **Sedang**: Suhu **15°C – 30°C** (`15 ≤ temp_normalized * 40 ≤ 30`)  
        - **Ekstrem**: Suhu > **30°C** (`temp_normalized * 40 > 30`)  

        Setelah dikelompokkan, suhu dinormalisasi kembali untuk menjaga konsistensi dengan rentang awal **0–1** sebelum digunakan dalam analisis.  
        """)


    with st.expander("📌 **Rangkuman Grafik**", expanded=True):
        st.markdown("""
        - Hari dimana para penyewa melakukan penyewaan sepeda ini banyak dilakukan di hari dengan suhu sedang, yang dalam rentang normalisasi berada pada angka 0.366-0.732 atau pada rentang biasa di angka 15-30 derajat
        """)
