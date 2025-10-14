"""MU88 API Client"""

import httpx
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class MU88APIClient:
    """Client for MU88 Lottery API"""

    BASE_URL = "https://mu88.live/api/front/open/lottery/history/list/game"

    # Map our province codes to MU88 game codes
    PROVINCE_MAP = {
        # Miền Bắc
        "MB": "miba",
        # Miền Nam
        "TPHCM": "tphc",
        "BALI": "bali",
        "BETR": "betr",
        "ANGI": "angi",
        "BIDU": "bidu",
        "BIPH": "biph",
        "BITH": "bith",
        "CAMA": "cama",
        "CATH": "cath",
        "DALAT": "dalat",
        "DONA": "dona",
        "DOTH": "doth",
        "HAGI": "hagi",
        "KIGI": "kigi",
        "LOAN": "loan",
        "SOTR": "sotr",
        "TANI": "tani",
        "TIGI": "tigi",
        "TRVI": "trvi",
        "VILO": "vilo",
        "VUTA": "vuta",
        # Miền Trung
        "DANA": "dana",
        "BIDI": "bidi",
        "DALAK": "dalak",
        "DANO": "dano",
        "GILA": "gila",
        "KHHO": "khho",
        "KOTU": "kotu",
        "NITH": "nith",
        "PHYE": "phye",
        "QUBI": "qubi",
        "QUNA": "quna",
        "QUNG": "qung",
        "QUTR": "qutr",
        "THTH": "thth",
    }

    def __init__(self, timeout: float = 30.0):
        self.timeout = timeout

    async def fetch_results(self, province_code: str, limit: int = 60) -> Optional[Dict]:
        """
        Fetch lottery results from MU88 API

        Args:
            province_code: Province code (MB, TPHCM, GILA, etc.)
            limit: Number of results to fetch (default 60)

        Returns:
            Raw API response or None if error
        """
        try:
            # Convert province code to game code
            game_code = self.PROVINCE_MAP.get(province_code.upper(), province_code.lower())

            params = {"limitNum": limit, "gameCode": game_code}

            logger.info(f"📡 Fetching {province_code} ({game_code}) - limit {limit}")

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(self.BASE_URL, params=params)
                response.raise_for_status()

                data = response.json()

                # Check if API request was successful
                if not data.get("success"):
                    logger.error(f"❌ API returned error: {data.get('msg')}")
                    return None

                logger.info(f"✅ Fetched {province_code} successfully")
                return data

        except httpx.HTTPError as e:
            logger.error(f"❌ HTTP Error fetching {province_code}: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Error fetching {province_code}: {e}")
            return None
