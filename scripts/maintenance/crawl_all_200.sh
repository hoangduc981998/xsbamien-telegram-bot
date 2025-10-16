#!/bin/bash

echo "🚀 CRAWLING 200 DRAWS FOR ALL PROVINCES"
echo "=" | head -c 70 | tr '\n' '='
echo ""

# Miền Bắc (200 days = 200 draws)
echo "📥 Miền Bắc..."
PYTHONPATH=$(pwd) python scripts/load_historical_data.py \
  --province MB --days 200 --delay 1.0

# Miền Nam (1407 days ≈ 200 draws for 1/week, 707 days for 2/week)
echo ""
echo "📥 Miền Nam..."

# TP.HCM (2 draws/week)
PYTHONPATH=$(pwd) python scripts/load_historical_data.py \
  --province TPHCM --days 707 --delay 1.0

# 1 draw/week provinces (1407 days)
for province in DONGTHAP CAMAU BENTRE VUNGTAU BACLIEU DONGNAI CANTHO SOCTRANG ANGI TAYNINH BINHTHUAN VINHLONG BINHDUONG TRAVINH LONGAN TIENGIANG KIENGIANG DALAT
do
  echo "  → $province"
  PYTHONPATH=$(pwd) python scripts/load_historical_data.py \
    --province $province --days 1407 --delay 1.0
done

# Miền Trung (1407 days ≈ 200 draws for 1/week)
echo ""
echo "📥 Miền Trung..."

for province in THUATHIENHUE PHUYEN DAKLAK QUANGNAM KHANHHOA DANANG BINHDINH QUANGTRI QUANGBINH GIALAI NINHTHUAN QUANGNGAI DAKNONG KONTUM
do
  echo "  → $province"
  PYTHONPATH=$(pwd) python scripts/load_historical_data.py \
    --province $province --days 1407 --delay 1.0
done

echo ""
echo "=" | head -c 70 | tr '\n' '='
echo ""
echo "✅ CRAWLING COMPLETE!"
echo ""
echo "📊 Summary:"
python3 << 'EOPYTHON'
import sqlite3
from collections import defaultdict

db = sqlite3.connect('xoso.db')
cursor = db.cursor()

# Get counts by province
cursor.execute("""
    SELECT province_code, COUNT(DISTINCT draw_date) as draws
    FROM lo_2_so_history
    GROUP BY province_code
    ORDER BY province_code
""")

regions = defaultdict(list)
for row in cursor.fetchall():
    province = row[0]
    draws = row[1]
    
    # Determine region
    if province == 'MB':
        region = 'Miền Bắc'
    elif province in ['THUATHIENHUE', 'PHUYEN', 'DAKLAK', 'QUANGNAM', 'KHANHHOA', 
                      'DANANG', 'BINHDINH', 'QUANGTRI', 'QUANGBINH', 'GIALAI', 
                      'NINHTHUAN', 'QUANGNGAI', 'DAKNONG', 'KONTUM']:
        region = 'Miền Trung'
    else:
        region = 'Miền Nam'
    
    regions[region].append((province, draws))

for region, provinces in sorted(regions.items()):
    print(f"\n{region}:")
    for province, draws in provinces:
        status = "✅" if draws >= 180 else "⚠️"
        print(f"  {status} {province:15s} {draws:3d} kỳ")

db.close()
EOPYTHON

echo ""
echo "🎯 Ready to test Lô Gan for all provinces!"
