<div align="center">
  <img src="assets/banner.jpg" alt="GTA Auto Clipper Logo" width="360" style="border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.3);" />

  # 🎬 LocalClip GTA VI · Auto Clipper
  
  **Generator Video Pendek Vertikal Otomatis (YouTube Shorts, TikTok, Instagram Reels) Berbasis AI & Render Lokal.**

  [![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
  [![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-brightgreen.svg)](https://github.com/TSABIT1312/localclip-gtavi)
  [![FastAPI](https://img.shields.io/badge/Backend-FastAPI%20%2B%20Uvicorn-009688.svg)](https://fastapi.tiangolo.com/)
  [![FFmpeg](https://img.shields.io/badge/Render-FFmpeg%20Lokal-green.svg)](https://ffmpeg.org/)
  [![AI](https://img.shields.io/badge/AI-Anthropic%20%7C%209Router-purple.svg)](https://anthropic.com)
  [![TTS](https://img.shields.io/badge/TTS-Edge--TTS%20%7C%20SAPI%20%7C%20Say-orange.svg)](https://github.com/rany2/edge-tts)

</div>

---

## 📌 Tentang Project

**LocalClip GTA VI (Auto Clipper)** adalah aplikasi web lokal untuk memotong dan mengonversi video panjang (seperti gameplay GTA, live streaming YouTube, podcast, atau rekaman MP4 lokal) menjadi klip vertikal pendek (9:16) yang siap diposting ke Shorts, TikTok, dan Reels.

Aplikasi ini menggunakan model AI (Claude / 9Router) untuk menganalisis transkrip dialog, menemukan momen-momen paling seru, mendeteksi wajah streamer, dan merender video vertikal menggunakan **FFmpeg** serta suara narator (Microsoft Neural, macOS Speech, atau Windows SAPI) tanpa perlu upload video ke cloud eksternal.

---

## ✨ Fitur Utama

- 🌍 **Full Cross-Platform (Windows, Linux, macOS)**:
  - Berjalan mulus di sistem operasi apa pun. Dilengkapi launcher sekali klik untuk Windows (`start.bat`), macOS (`start.command`), dan Linux (`start.sh`).
- 🎮 **Layout Streamer Split Screen**:
  - **Atas**: Wajah streamer hasil crop rapi (0–460 px).
  - **Tengah**: Banner pembatas gelap bergaris kuning (`#ffd24a`) yang menampilkan nama *CREATOR / JUDUL KLIP*.
  - **Bawah**: Video aksi gameplay dinamis (520–1280 px) dilengkapi subtitle teks tebal yang mudah dibaca.
- ✂️ **Interactive Visual Cropper**:
  - Pangkas wajah streamer langsung di browser dengan menggeser dan menarik kotak kuning di atas gambar frame video.
  - Tersedia tombol preset instan: **Kiri Bawah**, **Kiri Atas**, **Kanan Atas**, **Kanan Bawah**, dan **Reset AI**.
- 🌐 **Dukungan 9Router & Anthropic API**:
  - Mendukung koneksi langsung ke Anthropic API maupun melalui AI proxy/gateway lokal seperti **9Router** (`http://127.0.0.1:20128`).
  - Mendukung custom model (misal `gacorr`, `claude-3-5-sonnet`, dll).
- 🗣️ **Suara Narator Alami Multi-Bahasa**:
  - 🇮🇩 **Bahasa Indonesia**: Narasi jernih dan natural dengan subtitle bahasa Indonesia.
  - 🇺🇸 **English**: Narasi aksen Inggris dengan subtitle bahasa Inggris.
  - Didukung oleh **Edge-TTS** lintas platform dengan fallback cerdas ke TTS sistem lokal (macOS `say` / Windows PowerShell SAPI / Linux `espeak`).
- ⏱️ **Auto-Clamping Durasi Cerdas**:
  - Klip otomatis dijaga dalam rentang aman 10–55 detik (maksimal 60 detik) sehingga tidak pernah melebihi batas durasi Shorts/Reels.
- 🔒 **100% Privat & Lokal**:
  - API key hanya disimpan di memori proses (tidak ditulis ke disk/database).
  - Video dan subtitle dirender langsung di komputer Anda.

---

## 📋 Prasyarat Sistem

1. **Sistem Operasi**: Windows 10/11, macOS, atau Linux (Ubuntu, Debian, Fedora, Arch, dll).
2. **Python**: Versi `3.10` atau lebih baru.
3. **FFmpeg & ffprobe**:
   - **Windows**: Jalankan di PowerShell: `winget install Gyan.FFmpeg` (atau download dari [gyan.dev/ffmpeg](https://www.gyan.dev/ffmpeg/builds/) lalu tambahkan folder `bin` ke System PATH).
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt update && sudo apt install ffmpeg`
4. **Koneksi Internet**: Untuk download video YouTube, API AI, dan suara narator.

---

## 🚀 Tutorial Instalasi & Menjalankan

### 1. Clone Repository
```bash
git clone https://github.com/TSABIT1312/localclip-gtavi.git
cd localclip-gtavi
```

### 2. Buat Virtual Environment & Install Dependencies

#### Di Windows:
Buka Command Prompt atau PowerShell di folder project:
```cmd
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

#### Di macOS & Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

### 3. Jalankan Aplikasi Web

Pilih cara tercepat sesuai sistem operasi Anda:

- **Windows**: Cukup klik dua kali file **`start.bat`** (atau ketik `start.bat` di CMD).
- **macOS**: Klik dua kali file **`start.command`**.
- **Linux**: Buka terminal dan jalankan `./start.sh` (atau `bash start.sh`).

*Atau secara manual lewat terminal di OS apa pun:*
```bash
python -m uvicorn app:app --host 127.0.0.1 --port 8765
```

### 4. Buka di Browser
Setelah server menyala, buka:
👉 **[http://127.0.0.1:8765](http://127.0.0.1:8765)**

---

## 📖 Panduan Penggunaan Web App

```
 [Input Video/YouTube] ──> [Analisis AI] ──> [Visual Crop & Edit] ──> [Render FFmpeg] ──> [Download MP4/ZIP]
```

### Langkah 1: Atur API Key & Provider AI
1. Di pojok kanan atas dashboard, klik tombol **"Pengaturan AI"**.
2. Masukkan konfigurasi Anda:
   - **Jika menggunakan 9Router**:
     - *Base URL*: `http://127.0.0.1:20128` (atau alamat port 9Router Anda)
     - *API Key*: Masukkan API key 9Router Anda
     - *Model*: Ketik nama model Anda (misalnya `gacorr` atau `anthropic/claude-3-5-sonnet`)
   - **Jika menggunakan Anthropic Resmi**:
     - *Base URL*: Kosongkan
     - *API Key*: Masukkan `sk-ant-...`
     - *Model*: Pilih atau isi `claude-3-5-sonnet-20241022`
3. Klik **Simpan Pengaturan**.

---

### Langkah 2: Buat Batch Klip Baru
1. Pada form **"Bikin batch baru"**:
   - **Link YouTube**: Masukkan link video YouTube (misalnya video stream Kai Cenat atau gameplay GTA VI).
   - *Atau upload file*: Anda juga bisa mengunggah file `.mp4` sendiri beserta file `.srt`.
2. **Jumlah Klip**: Pilih berapa klip yang ingin diekstrak (1 s/d 5 klip).
3. **Bahasa Subtitle & Narasi**: Pilih 🇮🇩 **Bahasa Indonesia** atau 🇺🇸 **English**.
4. **Nama Channel / Creator**: Nama yang akan ditampilkan pada banner kuning pemisah (misal: `Kai Cenat`).
5. Centang persetujuan pengiriman transkrip ke AI, lalu klik **Proses**.

---

### Langkah 3: Koreksi & Pangkas Wajah Streamer (Visual Cropper)
Setelah AI selesai menganalisis video dan menyiapkan kandidat:
1. Klik tombol **"Koreksi & crop"** pada kartu klip yang ingin disesuaikan.
2. Anda akan melihat gambar cuplikan video dengan **kotak pembatas kuning**:
   - **Geser kotak** ke posisi wajah streamer.
   - **Tarik sudut kotak** untuk memperbesar/memperkecil area pangkasan.
   - Atau gunakan tombol preset cepat: `📍 Kiri Bawah`, `📍 Kiri Atas`, `📍 Kanan Atas`, `📍 Kanan Bawah`.
3. Pilih **Gaya Layout Short**:
   - **Split Screen**: Wajah di atas, Banner pemisah kuning di tengah, Gameplay di bawah *(Rekomendasi)*.
   - **Contained 16:9**: Video full frame proporsional di tengah.
   - **No Facecam**: Fokus gameplay tanpa crop wajah.
4. Anda juga bisa mengedit judul klip, teks pembuka (hook), atau transkrip subtitle di panel ini.
5. Klik **Simpan & Render Ulang**.

---

### Langkah 4: Download Hasil Video
- Tonton preview video langsung di browser.
- Klik **Download MP4** untuk mengunduh video per klip.
- Atau klik tombol **Download ZIP** di bagian atas batch untuk mengunduh seluruh klip sekaligus dalam satu arsip zip.

---

## 🛠️ Perintah Berguna & Pengujian

Untuk menjalankan unit test otomatis guna memastikan seluruh fungsi validasi dan parsing berjalan normal:
```bash
.venv/bin/python -m unittest -v test_app.py
```

Untuk menjalankan smoke test pipeline rendering:
```bash
.venv/bin/python smoke_test.py
```

---

## 📁 Struktur Direktori

```text
localclip-gtavi/
├── assets/
│   └── banner.jpg          # Logo & banner header project
├── app.py                  # Server FastAPI, API endpoint, & background worker
├── render.py               # Engine render video FFmpeg, layout, & TTS macOS
├── index.html              # Frontend UI interaktif & visual image cropper
├── start.command           # Launcher one-click untuk macOS
├── requirements.txt        # Dependensi Python (FastAPI, Uvicorn, Pillow, yt-dlp, dll)
├── test_app.py             # Unit tests
├── smoke_test.py           # Smoke test script
├── .gitignore              # Proteksi data video, venv, cache, dan secret
└── README.md               # Dokumentasi panduan lengkap
```

---

## 📄 Lisensi & Disclaimer

- Project ini dibuat untuk penggunaan lokal dan personal.
- Pastikan Anda memiliki hak cipta atau izin untuk memproses dan mempublikasikan ulang video yang diunduh dari YouTube.
- AI menghasilkan rekomendasi berdasarkan transkrip; selalu tinjau ulang hasil klip sebelum mempublikasikannya ke media sosial.

---

<div align="center">
  Dibuat dengan ❤️ untuk para kreator konten dan clipper GTA VI / Gaming.
</div>
