# 🔍 Digital Forensik Mobile — Akuisisi & Analisis Artefak Telegram di Android Emulator

> **UAS Forensik Digital | Universitas Telkom Surabaya | 2026**  
> Kelas IF-03-02

---

## 📌 Deskripsi Proyek

Proyek ini merupakan investigasi forensik digital terhadap aplikasi **Telegram** yang berjalan di Android Emulator. Tujuan utama adalah mensimulasikan aktivitas pengguna, mengakuisisi barang bukti digital, dan menganalisis artefak yang tersimpan pada perangkat Android menggunakan metode **Logical Acquisition** dan **Physical Acquisition**.

Investigasi dilakukan sepenuhnya menggunakan tools open-source dan command-line, mulai dari koneksi ADB hingga decoding BLOB database SQLite dengan Python.

---

## 🎯 Tujuan Investigasi

- Mensimulasikan aktivitas pengguna nyata (SMS, panggilan telepon, chat Telegram)
- Mengakuisisi artefak digital dari perangkat Android secara forensik
- Menganalisis database Telegram (`cache4.db`) untuk merekonstruksi komunikasi
- Mendeteksi kemungkinan pesan yang telah dihapus
- Menjaga integritas barang bukti menggunakan hashing SHA-256

---

## 🧪 Lingkungan & Spesifikasi Perangkat

| Parameter | Nilai |
|---|---|
| Jenis Perangkat | Android Emulator (Android Studio) |
| Model | Android SDK built for x86 |
| Sistem Operasi | Android 10 |
| Aplikasi Target | Telegram |
| Package Name | `org.telegram.messenger.web` |
| Metode Akses | ADB Root (`adbd running as root`) |

---

## ⚙️ Tools yang Digunakan

| Tool | Fungsi |
|---|---|
| **Android Debug Bridge (ADB)** | Koneksi ke emulator, akuisisi data, pull file |
| **DB Browser for SQLite** | Inspeksi visual struktur database Telegram |
| **Python 3** (`sqlite3`, `datetime`, `itertools`) | Decoding artefak BLOB, rekonstruksi timeline |
| **PowerShell** | Hashing SHA-256 (`Get-FileHash`) |
| **Android Emulator (AVD)** | Simulasi perangkat Android |

---

## 🗂️ Struktur Investigasi

```
📁 Digital-Forensik-Telegram/
├── 📄 README.md
├── 📄 LAPORAN_FINAL.pdf          ← Laporan lengkap
│
│
├── 📁 ADB                        ← Tools untuk melakukan Akuisisi
│
├── 📁 Autopsy                    ← Tools untuk melakukan Analisis 
│
│
├── 📁 Logical_Acquisition/
│   ├── 📁 Device_Info/
│   │   ├── getprop.txt           ← Properti sistem Android
│   │   └── packages.txt          ← Daftar aplikasi terinstal
│   ├── 📁 Screenshots/
│   │   ├── homescreen.png        ← Kondisi perangkat saat akuisisi
│   │   ├── sms.png
│   │   └── calllog.png
│   ├── 📁 SMS/
│   │   └── sms_content.txt       ← Data SMS (nomor, isi, timestamp)
│   ├── 📁 CallLogs/
│   │   └── calllog_content.txt   ← Riwayat panggilan telepon
│   └── 📁 Telegram/
│       └── 📁 Database/
│           ├── cache4.db         ← Database utama Telegram ⭐
│           ├── cache4.db-wal     ← SQLite Write-Ahead Log
│           ├── cache4.db-shm     ← SQLite Shared Memory
│           └── tgnet.dat         ← Konfigurasi jaringan Telegram
│
├── 📁 Physical_Acquisition/
│   ├── userdata-qemu.img         ← Image penyimpanan virtual (1 GB)
│   ├── userdata-qemu.img.qcow2   ← Image diferensial (berisi perubahan)
│   └── 📁 hash/
│       ├── cache4hash.txt
│       ├── userdata-qemu.img.sha256.txt
│       └── userdata-qemu.img.qcow2.sha256.txt
│
│
└── 📁 Scripts/
    └── decode_telegram.py       ← Script Python decoding BLOB
```

---

## 🔬 Metodologi

### 1. Simulasi Aktivitas Pengguna
Aktivitas disimulasikan pada emulator Android menggunakan **Android Extended Controls** untuk SMS dan panggilan telepon, serta akun Telegram asli untuk skenario chat.

**Skenario aktivitas mencakup:**
- Login Telegram dan pengiriman pesan ke 3 user (Haidar, Meraa, Ryan)
- Pengiriman emoji, foto, dan video
- Pengeditan dan penghapusan pesan
- Voice call (berhasil & gagal)
- Pembuatan grup "forensic grub"
- Simulasi 3 SMS masuk + penghapusan 1 SMS
- Simulasi panggilan masuk, missed call, dan panggilan kedua

### 2. Identifikasi & Verifikasi Akses
```bash
# Verifikasi koneksi emulator
./adb devices

# Identifikasi model & versi Android
./adb shell getprop ro.product.model
./adb shell getprop ro.build.version.release

# Verifikasi akses root
./adb root
./adb shell whoami  # → root
```

### 3. Logical Acquisition
```bash
# Akuisisi informasi sistem
./adb shell getprop > Device_Info/getprop.txt

# Akuisisi daftar aplikasi
./adb shell pm list packages > Device_Info/packages.txt

# Akuisisi SMS
./adb shell content query --uri content://sms > SMS/sms_content.txt

# Akuisisi Call Log
./adb shell content query --uri content://call_log/calls > CallLogs/calllog_content.txt

# Discovery lokasi database Telegram
./adb shell ls -la /data/data/ | grep telegram
# → /data/data/org.telegram.messenger.web

# Pull database Telegram
./adb pull /data/data/org.telegram.messenger.web/files/cache4.db
./adb pull /data/data/org.telegram.messenger.web/files/cache4.db-wal
./adb pull /data/data/org.telegram.messenger.web/files/cache4.db-shm
./adb pull /data/data/org.telegram.messenger.web/files/tgnet.dat
```

### 4. Physical Acquisition
Image file AVD (`userdata-qemu.img.qcow2`) disalin dan di-hash sebagai low-level evidence.

### 5. Analisis Database & Decoding Python
Database `cache4.db` dibuka menggunakan DB Browser for SQLite. Karena Telegram menyimpan pesan dalam format **BLOB (Binary Large Object)**, dilakukan decoding menggunakan Python.

```python
import sqlite3
from datetime import datetime, timezone, timedelta
from itertools import groupby
import re

WIB = timezone(timedelta(hours=7))

conn = sqlite3.connect('cache4.db')
cursor = conn.cursor()

# Target UID yang terlibat dalam skenario
TARGET_UIDS = [1304847444, 5340529263, 1327557995, 540840483]
```

---

## 📊 Temuan Utama

### ✅ Artefak yang Berhasil Direkonstruksi

| No | Artefak | Status | Detail |
|---|---|---|---|
| 1 | Pesan terkirim & diterima | ✅ Berhasil | Timeline lengkap dengan timestamp WIB |
| 2 | Emoji, foto, video | ✅ Berhasil | Teridentifikasi sebagai `[FOTO]` / `[VIDEO]` |
| 3 | Voice call | ✅ Berhasil | Incoming & outgoing call terdeteksi |
| 4 | Pesan yang diedit | ✅ Berhasil | Versi terbaru berhasil ditemukan |
| 5 | Metadata grup | ✅ Berhasil | Nama & UID grup "forensic grub" ditemukan |
| 6 | Data SMS | ✅ Berhasil | Nomor pengirim, isi, timestamp |
| 7 | Call log | ✅ Berhasil | Nomor, durasi, jenis panggilan |

### ⚠️ Temuan Khusus

**Pesan Terhapus — Suspected Deleted Messages**

Deteksi dilakukan dengan menganalisis gap pada urutan Message ID (MID) di tabel `messages_v2`:

```
[!] ryan. (uid=1304847444)
  ▲ mid 120 s/d 121 HILANG  (2 pesan kemungkinan dihapus)
  ▲ mid 123 s/d 123 HILANG  (1 pesan kemungkinan dihapus)
  ▲ mid 126 s/d 131 HILANG  (6 pesan kemungkinan dihapus)
  ▲ mid 133 s/d 139 HILANG  (7 pesan kemungkinan dihapus)

[!] haidar (uid=5340529263)
  ▲ mid 119 s/d 119 HILANG  (1 pesan kemungkinan dihapus)
  ▲ mid 122 s/d 122 HILANG  (1 pesan kemungkinan dihapus)
  ▲ mid 124 s/d 125 HILANG  (2 pesan kemungkinan dihapus)
  ▲ mid 132 s/d 132 HILANG  (1 pesan kemungkinan dihapus)
```

**Pesan Dihapus** — Isi pesan dari User A ke Meraa yang dihapus tidak dapat direkonstruksi, membuktikan bahwa Telegram menghapus record dari database secara permanen.

**Edit Pesan** — Telegram hanya menyimpan versi terbaru pesan; versi sebelum edit tidak dipertahankan dalam artefak yang berhasil diekstraksi.

**Pesan Grup** — Meskipun metadata grup berhasil ditemukan di tabel `chats`, isi komunikasi grup tidak berhasil direkonstruksi, kemungkinan karena perbedaan mekanisme penyimpanan pesan grup vs. private chat.

---

## 🔐 Integritas Barang Bukti (Hash SHA-256)

| File | SHA-256 |
|---|---|
| `cache4.db` | `C05CFB871D824EE7009544D49FA43C2F2B1CF21280EC655A1A37C28E36BA1F23` |
| `userdata-qemu.img` | `CC7FD069EA122B7C93689F8302C1EF886E852DC673D666F8BB809CA64E2D7DB3` |
| `userdata-qemu.img.qcow2` | `4B24BB7C1FF876D79F924572FD4B35536868D8D84D67015E3BEB0CC13ED6C5DF` |

---

## 📚 Tabel Artefak Digital yang Dikumpulkan

| No | File | Deskripsi | Metode |
|---|---|---|---|
| 1 | `getprop.txt` | Properti sistem Android | Logical — ADB |
| 2 | `packages.txt` | Daftar aplikasi terinstal | Logical — ADB |
| 3 | `homescreen.png` | Screenshot kondisi perangkat | Logical — ADB |
| 4 | `sms_content.txt` | Data SMS lengkap | Logical — Content Provider |
| 5 | `calllog_content.txt` | Riwayat panggilan telepon | Logical — Content Provider |
| 6 | `cache4.db` | Database utama Telegram | Logical — ADB Pull |
| 7 | `cache4.db-wal` | SQLite Write-Ahead Log | Logical — ADB Pull |
| 8 | `cache4.db-shm` | SQLite Shared Memory | Logical — ADB Pull |
| 9 | `tgnet.dat` | Konfigurasi jaringan | Logical — ADB Pull |
| 10 | `userdata-qemu.img.qcow2` | Physical image emulator | Physical — File Copy |

---

## 📝 Kesimpulan

Investigasi forensik digital ini berhasil mendemonstrasikan seluruh tahapan proses forensik mobile, mulai dari **persiapan lingkungan**, **simulasi aktivitas**, **identifikasi perangkat**, **akuisisi data**, hingga **analisis & rekonstruksi timeline**.

Temuan kunci:
- Telegram menyimpan database utamanya di `/data/data/org.telegram.messenger.web/files/cache4.db`, bukan di direktori `databases/` standar Android
- Pesan disimpan dalam format BLOB yang memerlukan decoding khusus
- Pesan yang dihapus **tidak dapat direcovery** dari database, namun keberadaannya dapat dideteksi melalui gap MID
- Pesan yang diedit hanya menyimpan versi terbaru; riwayat edit tidak tersedia

---

## 👥 Tim

| Nama | NIM |
|---|---|
| Arka Dwi Indrastata | 1203230017 |

**Program Studi:** Informatika | **Fakultas:** Informatika  
**Universitas Telkom Surabaya** | 2026

---

## 🔗 Proyek Terkait

> 🚧 **[Dalam Pengerjaan]** — [Building a Secure Linux Mint Workstation for Blue Team Operations](#)  
> Proyek selanjutnya berfokus pada hardening sistem Linux untuk keperluan operasi blue team / defensive security.

---

*Laporan ini dibuat untuk keperluan akademik dan portofolio. Seluruh simulasi dilakukan pada lingkungan terkontrol (emulator).*
