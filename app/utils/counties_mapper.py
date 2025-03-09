from typing import Dict, List, Optional
from difflib import get_close_matches

COUNTY_DATA = [
    {"id": 1, "name": "臺北市"},
    {"id": 2, "name": "基隆市"},
    {"id": 3, "name": "新北市"},
    {"id": 4, "name": "宜蘭縣"},
    {"id": 5, "name": "桃園市"},
    {"id": 6, "name": "新竹市"},
    {"id": 7, "name": "新竹縣"},
    {"id": 8, "name": "苗栗縣"},
    {"id": 9, "name": "臺中市"},
    {"id": 10, "name": "彰化縣"},
    {"id": 11, "name": "南投縣"},
    {"id": 12, "name": "雲林縣"},
    {"id": 13, "name": "嘉義市"},
    {"id": 14, "name": "嘉義縣"},
    {"id": 15, "name": "臺南市"},
    {"id": 16, "name": "高雄市"},
    {"id": 17, "name": "澎湖縣"},
    {"id": 18, "name": "屏東縣"},
    {"id": 19, "name": "臺東縣"},
    {"id": 20, "name": "花蓮縣"},
    {"id": 21, "name": "金門縣"},
    {"id": 22, "name": "連江縣"},
    {"id": 23, "name": "南海諸島"},
    {"id": 24, "name": "金邊"},
    {"id": 25, "name": "大阪市"}
]

class CountyMapper:
    def __init__(self):
        self.county_map = {county["name"]: county["id"] for county in COUNTY_DATA}
        # Create alternative mappings for common variations
        self.alternative_names = {
            "台北市": "臺北市",
            "台中市": "臺中市",
            "台南市": "臺南市",
            "台東縣": "臺東縣"
        }
        
    def get_county_id(self, location: str) -> Optional[int]:
        """
        Get county ID from location string using fuzzy matching.
        
        Args:
            location (str): Location string that might contain county name
            
        Returns:
            Optional[int]: County ID if found, None otherwise
        """
        # Clean up the location string
        location = location.strip()
        
        # First, try direct mapping
        for county_name in self.county_map:
            if county_name in location:
                return self.county_map[county_name]
        
        # Try alternative names
        for alt_name, std_name in self.alternative_names.items():
            if alt_name in location:
                return self.county_map[std_name]
        
        # Extract the first part of the location (usually the county)
        county_part = location.split('區')[0].split('市')[0].split('縣')[0]
        if county_part:
            # Try fuzzy matching
            county_names = list(self.county_map.keys())
            matches = get_close_matches(county_part, county_names, n=1, cutoff=0.6)
            if matches:
                return self.county_map[matches[0]]
        
        return None

    def get_county_name(self, county_id: int) -> Optional[str]:
        """Get county name from ID."""
        for county in COUNTY_DATA:
            if county["id"] == county_id:
                return county["name"]
        return None