Here’s a clean, polished **English README** for your integration — written to meet HACS expectations and to clearly explain how your scraper‑based integration works. It reflects all your latest requirements:

- Integration name: **LUMC pollentelling**
- One sensor per pollen type
- Names extracted from the **second column**
- Values extracted from **Totaal**
- No selection during setup
- Heuristic HTML scraper

---

# 📘 LUMC pollentelling

## 🌿 Overview  
**LUMC pollentelling** is a Home Assistant integration that retrieves daily pollen counts from the Leiden University Medical Center (LUMC).  
The integration scrapes the public page:

```
https://sec.lumc.nl/pollenwebextern/
```

It automatically detects all pollen types listed in the **second column** of the table (e.g., *Hazelaar*, *Els*, *Berk*, *Gras*) and creates **one sensor per pollen type**.  
The pollen count is extracted from the **“Totaal”** column and interpreted as an integer.

This integration does **not** rely on an API — it uses a robust HTML scraper designed to handle minor layout changes.

---

## ✨ Features

- 🔍 **Automatic pollen type detection**  
  The integration scans the table and creates sensors for all pollen types found in the second column.

- 🌡 **Accurate value extraction**  
  Values are parsed from the “Totaal” column and converted to integers.

- 🏷 **Clean sensor names**  
  Sensors are named exactly after the pollen type:  
  - `sensor.hazelaar`  
  - `sensor.els`  
  - `sensor.berk`  
  - `sensor.gras`

- 🔁 **Configurable update interval**  
  Cache TTL can be set during installation.

- 🧠 **Heuristic HTML parsing**  
  The scraper identifies the correct table, extracts the second column as the pollen name, and the “Totaal” column as the value.

---

## 📦 Installation via HACS (Custom Repository)

1. Open **HACS → Integrations**
2. Click **⋮ → Custom repositories**
3. Add your repository URL:
   ```
   https://github.com/<your-username>/<your-repo>
   ```
4. Select category **Integration**
5. Install **LUMC pollentelling**
6. Go to **Settings → Devices & Services → Add Integration**
7. Search for **LUMC pollentelling**
8. Set the cache TTL (default: 3600 seconds)

---

## 🛠 Requirements

The integration uses:

- `requests`
- `beautifulsoup4`

These are installed automatically by Home Assistant based on `manifest.json`.

---

## 📁 Directory Structure

```
custom_components/lumc_pollen/
│
├── __init__.py
├── manifest.json
├── config_flow.py
├── sensor.py
├── html_scraper.py
└── const.py
```

---

## 🧪 Debug Logging

To enable debug logs:

```yaml
logger:
  default: info
  logs:
    custom_components.lumc_pollen: debug
```

---

## ⚖️ License

MIT License  
© Yoeng Sin Khoe, 2026

---

## 🤝 Contributing

Issues, improvements, and pull requests are welcome.

