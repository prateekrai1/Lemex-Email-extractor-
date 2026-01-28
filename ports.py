import json
from typing import Optional


class PortResolver:
    def __init__(self, path: str):
        with open(path, "r") as f:
            ports = json.load(f)

        # Build lookup tables
        self.name_to_code = {}
        self.code_to_name = {}

        for entry in ports:
            code = entry["code"]
            name = entry["name"]

            # normalize
            name_key = name.strip().lower()

            self.name_to_code[name_key] = code

            # prefer first-seen canonical name per code
            if code not in self.code_to_name:
                self.code_to_name[code] = name

    def resolve(self, raw_name: Optional[str]) -> Optional[str]:
        """
        Resolve raw port name → UN/LOCODE
        """
        if not raw_name:
            return None

        key = raw_name.strip().lower()
        return self.name_to_code.get(key)

    def get_name(self, code: Optional[str]) -> Optional[str]:
        """
        Resolve UN/LOCODE → canonical port name
        """
        if not code:
            return None

        return self.code_to_name.get(code)
