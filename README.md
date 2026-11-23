# Clip Local

Web pribadi di Mac untuk memilih momen dari YouTube atau upload video + SRT, analisis melalui Claude API, render short vertikal lokal.

## Jalankan

Klik dua kali `start.command`, lalu buka http://127.0.0.1:8765. Atau:

```sh
.venv/bin/python -m uvicorn app:app --host 127.0.0.1 --port 8765
```

Masukkan API key melalui Pengaturan AI (mendukung Anthropic API langsung maupun gateway seperti 9Router). Untuk 9Router, masukkan Base URL (misalnya `http://localhost:20128`). Key hanya berada di memori proses (atau `ANTHROPIC_API_KEY` dan `ANTHROPIC_BASE_URL` saat start), tidak tersimpan dalam browser maupun file job. Model default `claude-fable-5-2`; dapat diganti dengan ID model yang tersedia di akun/gateway Anda. Jangan masukkan key melalui chat.

## Alur

1. Link HTTPS YouTube publik, atau file video maksimal 1 GB + SRT. Rekaman maksimal 4 jam; live aktif tidak didukung.
2. Pilih 1–5 klip, nama CTA opsional (default nama channel), setujui pengiriman transkrip/gambar ke API.
3. AI membaca seluruh transkrip dalam bagian 30 menit; memilih kandidat; mengurutkan kandidat. Untuk setiap kandidat dipilih, tiga frame + caption diperiksa untuk crop facecam dan subtitle Inggris.
4. Render memakai FFmpeg + Pillow, narasi lokal macOS Samantha; 720×1280 30 fps, facecam di atas, subtitle di bawah, zoom, intro, CTA.
5. Koreksi caption/crop/teks lalu render ulang tanpa biaya AI tambahan. Download per MP4 atau ZIP. File di `data/<job-id>/` tetap lokal; versi lama tidak dihapus otomatis.

## Batas yang sengaja dipilih

- Ranking editorial, bukan prediksi/jaminan viral. Pencarian transkrip bisa melewatkan kejadian tanpa dialog. Tiga frame bukan penilaian seluruh gerakan atau suara; audio tidak dikirim ke AI.
- File tanpa subtitle membutuhkan SRT; belum ada speech-to-text otomatis. Subtitle auto/terjemahan AI dapat salah, preview sebelum publikasi.
- Crop facecam statis per klip; jika posisi berubah, koreksi di editor atau gunakan mode gameplay utuh.
- Satu job pada satu waktu; proses panjang berjalan di thread lokal. Restart menandai job belum selesai sebagai terhenti, tidak melanjutkannya otomatis.
- API berbayar: sampai satu panggilan per bagian transkrip 30 menit, satu ranking, dan satu pemeriksaan per klip. Tidak ada estimasi harga palsu. Model default mungkin tidak tersedia pada semua akun.
- YouTube dapat menolak download/subtitle; upload lokal adalah alternatif. Pengguna harus memiliki hak pemrosesan/publikasi.
- API key hanya dikirim ke `https://api.anthropic.com`. Nama channel, transkrip, serta tiga frame terpilih per klip dikirim setelah persetujuan. Jangan unggah materi sensitif yang tidak ingin dikirim.
- Bind hanya 127.0.0.1. Ada validasi Host, Origin, token mutasi per sesi, whitelist file media. Jangan expose lewat tunnel/LAN; bukan aplikasi multi-user.
- Tidak memakai cloud storage, akun pengguna, database eksternal, auto-publish, atau cloning suara.

## Verifikasi

```sh
.venv/bin/python -m unittest -v test_app.py
```

Tes API live memerlukan key dan kredit. Tes render lokal tidak memerlukan key. Dependensi sistem: `ffmpeg`, `ffprobe`, macOS `say`; Python dependencies di `requirements.txt`. Lingkungan `.venv` terisolasi.
