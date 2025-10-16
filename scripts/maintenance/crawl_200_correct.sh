#!/bin/bash

echo "🚀 CRAWLING 200 DRAWS FOR ALL PROVINCES (CORRECT CODES)"
echo "=" | head -c 70 | tr '\n' '='
echo ""

# Miền Bắc (200 kỳ)
echo "📥 Miền Bắc..."
PYTHONPATH=$(pwd) python scripts/load_historical_data.py \
  --province MB --days 200 --delay 1.0

# Miền Nam (ALL use 200 limit - API maximum)
echo ""
echo "📥 Miền Nam..."

# Note: API chỉ cho phép MAX 200 kỳ
# Các tỉnh 1 draw/week: 200 kỳ = ~1400 days, nhưng API limit = 200
# Các tỉnh 2 draws/week: 200 kỳ = ~700 days, nhưng API limit = 200

for province in TPHCM DOTH CAMA BETR VUTA BALI DONA CATH SOTR ANGI TANI BITH VILO BIDU TRVI LOAN TIGI KIGI DALAT
do
  echo "  → $province (200 kỳ max)"
  PYTHONPATH=$(pwd) python scripts/load_historical_data.py \
    --province $province --days 200 --delay 1.0
done

# Miền Trung
echo ""
echo "📥 Miền Trung..."

for province in THTH PHYE DALAK QUNA KHHO DANA BIDI QUTR QUBI GILA NITH QUNG DANO KOTU
do
  echo "  → $province (200 kỳ max)"
  PYTHONPATH=$(pwd) python scripts/load_historical_data.py \
    --province $province --days 200 --delay 1.0
done

echo ""
echo "=" | head -c 70 | tr '\n' '='
echo ""
echo "✅ CRAWLING COMPLETE!"
echo ""
echo "📊 Summary:"
python3 << 'EOPYTHON'
import sqlite3

db = sqlite3.connect('xoso.db')
cursor = db.cursor()

cursor.execute("""
    SELECT province_code, COUNT(DISTINCT draw_date) as draws
    FROM lo_2_so_history
    GROUP BY province_code
    ORDER BY province_code
""")

print("\nProvinces with data:")
for row in cursor.fetchall():
    status = "✅" if row[1] >= 180 else "⚠️"
    print(f"  {status} {row[0]:10s} {row[1]:3d} kỳ")

db.close()
EOPYTHON

echo ""
echo "🎯 Ready to test Lô Gan!"
