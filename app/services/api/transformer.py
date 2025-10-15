"""Transform MU88 API data to standard format"""

import json
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class DataTransformer:
    """Transform MU88 API data to bot's standard format"""

    # Prize mapping for different regions
    MB_PRIZES = ["DB", "G1", "G2", "G3", "G4", "G5", "G6", "G7"]
    MN_MT_PRIZES = ["DB", "G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8"]

    @staticmethod
    def transform_single_result(issue: Dict, province_name: str, region: str) -> Dict:
        """
        Transform single issue to standard format

        Args:
            issue: Single issue from API's issueList
            province_name: Province name (e.g., "Miền Bắc", "TP. HCM")
            region: Region code (MB, MN, MT)

        Returns:
            Standardized result dict
        """
        try:
            # Parse the detail JSON string
            detail_str = issue.get("detail", "[]")
            detail_list = json.loads(detail_str)

            # Select prize mapping based on region
            prize_names = (
                DataTransformer.MB_PRIZES
                if region == "MB"
                else DataTransformer.MN_MT_PRIZES
            )

            # Build result dict
            result = {"date": issue.get("turnNum"), "province": province_name}

            # Map prizes (reverse order for MN/MT to match structure)
            if region == "MB":
                # MB: [DB, G1, G2, G3, G4, G5, G6, G7]
                for i, prize_name in enumerate(prize_names):
                    if i < len(detail_list):
                        numbers = detail_list[i].split(",")
                        result[prize_name] = numbers
            else:
                # MN/MT: [DB, G1, G2, G3, G4, G5, G6, G7, G8]
                # Detail order: [DB, G1, G2, G3, G4, G5, G6, G7, G8]
                for i, prize_name in enumerate(prize_names):
                    if i < len(detail_list):
                        numbers = detail_list[i].split(",")
                        result[prize_name] = numbers

            return result

        except Exception as e:
            logger.error(f"❌ Error transforming result: {e}")
            logger.error(f"Issue data: {issue}")
            return {}

    @staticmethod
    def transform_results(api_response: Dict) -> List[Dict]:
        """
        Transform full API response to list of standardized results

        Args:
            api_response: Full API response from MU88

        Returns:
            List of standardized result dicts
        """
        try:
            t_data = api_response.get("t", {})
            issue_list = t_data.get("issueList", [])
            province_name = t_data.get("name", "Unknown")
            nav_cate = t_data.get("navCate", "").upper()

            # Determine region
            if nav_cate == "MB":
                region = "MB"
            elif nav_cate == "MN":
                region = "MN"
            elif nav_cate == "MT":
                region = "MT"
            else:
                region = "MN"  # Default

            results = []
            for issue in issue_list:
                result = DataTransformer.transform_single_result(
                    issue, province_name, region
                )
                if result:
                    results.append(result)

            logger.info(f"✅ Transformed {len(results)} results for {province_name}")
            return results

        except Exception as e:
            logger.error(f"❌ Error transforming response: {e}")
            return []
