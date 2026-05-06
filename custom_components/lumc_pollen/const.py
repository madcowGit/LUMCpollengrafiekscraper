"""Constants for the LUMC Pollen Grafiek integration."""

DOMAIN = "lumc_pollen"
DEFAULT_BASE_URL = "https://sec.lumc.nl/pollenwebextern/"
DEFAULT_TTL = 15 * 60  # 15 minutes
DEFAULT_SCAN_INTERVAL = 30 * 60  # 30 minutes

CONF_BASE_URL = "base_url"
CONF_POLLEN_TYPE = "pollen_type"
CONF_TTL = "ttl"
