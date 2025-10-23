
from __future__ import annotations
import os
import time
import re
from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup

BASE_URL = os.environ.get('LUMC_BASE_URL', 'https://sec.lumc.nl/pollenwebextern/')

class PollenNotFound(Exception):
    pass

class LUMCPollenClient:
    """
    Lightweight scraper for the LUMC pollen dashboard.
    Caches results in memory for a short TTL to avoid excessive requests.
    """
    def __init__(self, ttl_seconds: int = 15 * 60, timeout: int = 15):
        self.ttl = ttl_seconds
        self.timeout = timeout
        self._cache: Dict[str, Any] = {}

    # --------------- internal helpers ---------------
    def _get_soup(self) -> BeautifulSoup:
        now = time.time()
        cached = self._cache.get('soup')
        if cached and (now - cached['ts']) < self.ttl:
            return cached['soup']

        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; LUMCPollenBot/1.0; +https://example.local)'
        }
        resp = requests.get(BASE_URL, headers=headers, timeout=self.timeout)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        self._cache['soup'] = {'ts': now, 'soup': soup}
        # invalidate derived caches
        for k in ['rows', 'names', 'graph_links']:
            self._cache.pop(k, None)
        return soup

    def _parse_rows(self) -> List[Dict[str, Any]]:
        cached = self._cache.get('rows')
        if cached:
            return cached

        soup = self._get_soup()
        table = soup.find('table', attrs={'id': 'PollenTabel'})
        if not table:
            return []
        body = table.find('tbody') or table
        rows = []
        for tr in body.find_all('tr'):
            tds = [td.get_text(strip=True) for td in tr.find_all('td')]
            if not tds:
                continue
            # Assume: first cell is pollen name, last cell is total
            name = tds[1]
            total_raw = tds[-1] if tds else ''
            try:
                total = int(total_raw) if total_raw else 0
            except ValueError:
                # remove non-digits, then cast
                total = int(re.sub(r'\D', '', total_raw) or 0)
            rows.append({'name': name, 'columns': tds, 'total': total})
        self._cache['rows'] = rows
        # also cache names for lookup convenience
        self._cache['names'] = [r['name'] for r in rows]
        return rows

    def _graph_links(self) -> List[str]:
        cached = self._cache.get('graph_links')
        if cached:
            return cached
        soup = self._get_soup()
        links = [a['href'] for a in soup.find_all('a', href=True)]
        # Heuristic: keep only graph pages (PollenGrafiek*.html)
        links = [h for h in links if 'PollenGrafiek' in h and h.endswith('.html')]
        self._cache['graph_links'] = links
        return links

    def _find_name_index(self, name: str) -> int:
        names = [n.lower() for n in self._cache.get('names') or [r['name'] for r in self._parse_rows()]]
        try:
            return names.index(name.lower())
        except ValueError:
            raise PollenNotFound(name)

    # --------------- public API ---------------
    def list_names(self) -> List[str]:
        return [r['name'] for r in self._parse_rows()]

    def get_table(self) -> List[Dict[str, Any]]:
        return self._parse_rows()

    def get_total(self, pollen_name: str) -> int:
        idx = self._find_name_index(pollen_name)
        return self._parse_rows()[idx]['total']

    def get_history_graph_url(self, pollen_name: str) -> str:
        idx = self._find_name_index(pollen_name)
        links = self._graph_links()
        if idx >= len(links):
            raise PollenNotFound(pollen_name)
        url = BASE_URL + links[idx]
        url_png = url.replace('.html', '.png').replace('PollenGrafiek', 'PollenGrafiekImg')
        return url_png

    def get_history_graph_png(self, pollen_name: str) -> bytes:
        url = self.get_history_graph_url(pollen_name)
        resp = requests.get(url, timeout=self.timeout)
        resp.raise_for_status()
        return resp.content
