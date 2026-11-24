# Editor video sebelumnya

## Intent
Rapikan ruang kerja Clip Local dan tambahkan pemilihan waktu pada video yang sudah tersedia, tanpa upload ulang. Pengguna menyetujui penggunaan video sebelumnya setelah usulan preview besar, timeline, serta panel crop/teks/gaya.

## Approach
Gunakan HTML/CSS/JavaScript dan FastAPI yang ada. Sumber upload lengkap dipakai bila tersimpan; klip YouTube lama memakai potongan lokal yang tersedia. Download ulang seluruh YouTube tidak dipilih: bukan permintaan pengguna dan menambah jaringan/disk. Editor multitrack penuh tidak diperlukan.

## Design
Ruang kerja gelap slate dengan aksen kuning penanda waktu, sidebar impor ringkas, kartu klip, editor lebar: preview sumber dan timeline di kiri, pengaturan dalam kelompok di kanan. Font sistem untuk teks, monospace untuk timecode. Preview sumber bukan simulasi output final; label menjelaskan hal ini. Input menit:detik dan slider mulai/akhir menyediakan akses keyboard dan pointer. Crop dilakukan pada video yang sama, bukan gambar dengan rasio berbeda. Mobile menjadi satu kolom.

## Behavior and constraints
- Gunakan video sebelumnya, tanpa mengubah atau menghapus sumber maupun render lama.
- Waktu start/end menggunakan detik absolut pada video asli; UI menampilkan timecode. Rentang potongan 1–60 detik, mengikuti renderer saat ini. Intro/CTA ditambahkan di luar durasi potongan.
- API menyediakan sumber editor dan batasnya. Jika hanya potongan lokal tersedia, batas ditampilkan, tidak mengesankan seluruh video tersedia.
- Subtitle dan zoom digeser/dibatasi saat trim berubah. Bagian di luar subtitle yang ada tidak diterjemahkan otomatis; beri penjelasan.
- Validasi rentang, angka finite, batas media, dan token tetap berlaku. Render gagal tidak mengganti sumber, metadata edit, atau output sebelumnya.
- Tidak ada dependency baru, AI berbayar, multitrack, transisi, atau download sumber tambahan.

## Verification
Unit test rentang dan kompatibilitas, perubahan timing, rollback render gagal, media whitelist. Browser desktop/mobile dan uji render lokal memakai media sintetis tanpa panggilan AI/TTS eksternal.
