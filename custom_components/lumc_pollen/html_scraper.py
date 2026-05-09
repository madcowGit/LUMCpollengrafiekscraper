import logging
import re
from typing import Dict

import requests
from bs4 import BeautifulSoup

_LOGGER = logging.getLogger(__name__)

URL = "https://sec.lumc.nl/pollenwebextern/"


def fetch_html() -> str | None:
    try:
        resp = requests.get(URL, timeout=10)
        resp.raise_for_status()
        return resp.text
    except Exception as err:
        _LOGGER.error("Error fetching LUMC HTML: %s", err)
        return None


def extract_pollen_values(html: str) -> Dict[str, int]:
    """Extract pollen values using the 2nd column as name and 'Totaal' as value."""
    soup = BeautifulSoup(html, "html.parser")
    tables = soup.find_all("table")
    results: Dict[str, int] = {}

    for table in tables:
        rows = table.find_all("tr")
        if not rows:
            continue

        # Convert table to matrix
        matrix = [
            [cell.get_text(strip=True) for cell in row.find_all(["td", "th"])]
            for row in rows
        ]

        header = matrix[0]
        if not header:
            continue

        # Find Totaal column
        try:
            totaal_idx = next(i for i, h in enumerate(header) if "totaal" in h.lower())
        except StopIteration:
            continue

        name_idx = 1  # ALWAYS use second column

        _LOGGER.debug("Using name column index: %s, totaal index: %s", name_idx, totaal_idx)

        # Extract rows
        for row in matrix[1:]:
            if len(row) <= max(name_idx, totaal_idx):
                continue

            name = row[name_idx]
            totaal_text = row[totaal_idx]

            if not name:
                continue

            match = re.search(r"(-?\d+)", totaal_text.replace(".", "").replace(",", ""))
            if not match:
                continue

            value = int(match.group(1))
            results[name] = value
            _LOGGER.debug("Extracted %s -> %s", name, value)

        if results:
            break

    if not results:
        _LOGGER.warning("No pollen values found in any table with 2nd-column names")

    return results
