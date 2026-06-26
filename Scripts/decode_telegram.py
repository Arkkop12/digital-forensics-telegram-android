import sqlite3
from datetime import datetime, timezone, timedelta
from itertools import groupby
import re

WIB = timezone(timedelta(hours=7))

conn = sqlite3.connect(r'D:\Kuliah\Semester_6\Forensik Digital\UAS\Logical_Acquisition\Telegram\Database\cache4.db')
cursor = conn.cursor()

TARGET_UIDS = [1304847444, 5340529263, 1327557995, 540840483]

cursor.execute("SELECT uid, name FROM users")
user_map = {}
for uid, name in cursor.fetchall():
    nama = name.split(';;;')[0] if ';;;' in name else name
    user_map[uid] = nama

NOISE = {
    'QY', 'jR', 'lb', 'AN', 'AM', 'ez', 'QYlbm', 'c=', 'v',
    'lo', 'Ki', 'ne', 'un', 'vu', 'RA', 'TG'
}

def extract_text(data):
    if not data:
        return "[kosong]"
    raw = bytes(data)
    hex_data = raw.hex().upper()

    try:
        full = raw.decode('utf-8', errors='ignore')
        emoji_inline = re.findall(r'[\U0001F300-\U0001F9FF\u2600-\u27BF\U0001FA00-\U0001FAFF]+', full)
    except:
        full = ''
        emoji_inline = []

    # cek phone call
    if hex_data.startswith('0A') and len(raw) < 100:
        return "[📞 PHONE CALL]"

    # cek media
    if b'video/mp4' in raw:
        return "[🎥 VIDEO]"
    if b'image/' in raw or b'jpg' in raw or b'png' in raw:
        return "[🖼️ FOTO]"
    if b'audio/' in raw or b'ogg' in raw or b'mp3' in raw:
        return "[🎵 AUDIO]"
    if b'application/x-tgsticker' in raw and not emoji_inline:
        return "[🎭 STICKER]"

    try:
        tokens = re.findall(
            r'[a-zA-Z0-9\s\.,!?\'\"()\-_@#%&*+=:;<>/\\]+'
            r'|[\U0001F300-\U0001F9FF]+'
            r'|[\u2600-\u27BF]+'
            r'|[\U0001FA00-\U0001FAFF]+'
            r'|[\U00010000-\U0010FFFF]+',
            full
        )

        bersih = []
        for t in tokens:
            t = t.strip()
            if not t:
                continue
            if t in NOISE:
                continue
            if len(t) <= 3 and not any(ord(c) > 127 for c in t):
                if not re.match(r'^[a-zA-Z]{2,}$', t):
                    continue
                if re.match(r'^[A-Z]{2,3}$', t) and t not in {'OK', 'Hi'}:
                    continue
            if len(t) > 3:
                readable = sum(c.isalpha() or c.isspace() or ord(c) > 127 for c in t)
                if readable / len(t) < 0.5:
                    continue
            if re.match(r"^[a-zA-Z0-9'=\-]{1,4}$", t) and not t.isalpha():
                continue
            bersih.append(t)

        hasil = ' '.join(bersih[:8]).strip()
        if emoji_inline:
            hasil += ' ' + ' '.join(emoji_inline)
        hasil = hasil.strip()

        if hasil:
            return hasil

    except:
        pass

    return "[📎 MEDIA]"

cursor.execute("""
    SELECT mid, uid, date, out, data 
    FROM messages_v2 
    WHERE uid IN ({})
    ORDER BY date ASC
""".format(','.join(str(u) for u in TARGET_UIDS)))

print("=" * 70)
print("REKONSTRUKSI TIMELINE CHAT TELEGRAM")
print("=" * 70)

for row in cursor.fetchall():
    mid, uid, date, out, data = row
    waktu = datetime.fromtimestamp(date, tz=WIB).strftime('%Y-%m-%d %H:%M:%S WIB')
    arah = ">>> KIRIM" if out == 1 else "<<< TERIMA"
    nama = user_map.get(uid, f"UID:{uid}")
    pesan = extract_text(data)

    print(f"[{waktu}] {arah} | {nama} (uid={uid})")
    print(f"  Pesan: {pesan}")
    print()

cursor.execute("""
    SELECT uid, mid FROM messages_v2 
    WHERE uid IN ({})
    ORDER BY uid, mid ASC
""".format(','.join(str(u) for u in TARGET_UIDS)))

rows = cursor.fetchall()

print("=" * 70)
print("DETEKSI PESAN YANG DIHAPUS")
print("=" * 70)

ada_gap = False
for uid, group in groupby(rows, key=lambda x: x[0]):
    mids = [r[1] for r in group]
    nama = user_map.get(uid, f"UID:{uid}")
    gaps = []
    for i in range(len(mids) - 1):
        if mids[i+1] - mids[i] > 1:
            start = mids[i] + 1
            end = mids[i+1] - 1
            jumlah = end - start + 1
            gaps.append((start, end, jumlah))

    if gaps:
        ada_gap = True
        print(f"\n[!] {nama} (uid={uid})")
        for start, end, jumlah in gaps:
            print(f"  ⚠️  mid {start} s/d {end} HILANG ({jumlah} pesan kemungkinan dihapus)")

if not ada_gap:
    print("Tidak ada pesan yang terdeteksi dihapus.")

conn.close()