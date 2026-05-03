# LUMC Pollen Grafiek - Home Assistant Integration

This integration brings LUMC pollen data directly into Home Assistant without needing a separate Docker container or webserver.

## Features

- **Memory-cached scraper**: Efficient, lightweight scraping with configurable TTL cache
- **Configurable UI**: Easy setup through Home Assistant UI
- **Multiple data points**: Get pollen total count, graph URL, and graph image
- **Base64 encoded images**: Graph images stored as base64 for easy display in automations/templates
- **No Docker required**: Runs as a native Home Assistant integration
- **Native entities**: Access data through standard Home Assistant sensors

## Installation

1. Copy the `custom_components/lumc_pollen` directory to your Home Assistant `custom_components` folder:
   ```bash
   ~/.homeassistant/custom_components/lumc_pollen/
   ```

2. Restart Home Assistant

3. Go to **Settings → Devices & Services** and click **Create Integration**

4. Search for and select "LUMC Pollen Grafiek"

## Configuration

After adding the integration via the UI, you'll be prompted to configure:

- **Base URL**: The LUMC website URL (default: `https://sec.lumc.nl/pollenwebextern/`)
- **Pollen Type**: The pollen type to monitor (e.g., "Gramineeën", "Betulapollen", "Berkenpollen")
- **Cache TTL**: How long to keep data cached in memory (default: 900 seconds = 15 minutes)

## Sensors

The integration creates three sensors per pollen type:

### 1. Total Count Sensor
- **Entity ID**: `sensor.lumc_[pollen_type]_total`
- **State**: The pollen count in µg/m³
- **Unit**: µg/m³
- **State Class**: measurement
- **Attributes**:
  - `graph_url`: Direct URL to the graph image on LUMC website
  - `graph_image`: Base64-encoded PNG image as data URL

### 2. Graph URL Sensor
- **Entity ID**: `sensor.lumc_[pollen_type]_graph_url`
- **State**: Direct link to the graph image PNG

### 3. Graph Image Sensor
- **Entity ID**: `sensor.lumc_[pollen_type]_graph_image`
- **State**: Base64-encoded data URL of the graph image (can be used in picture entities)
- **Icon**: mdi:image

## Usage Examples

### Display the current pollen count as a gauge
```yaml
type: gauge
entity: sensor.lumc_gramineeën_total
min: 0
max: 200
```

### Display the graph image in a dashboard
```yaml
type: custom:picture-entity
entity: sensor.lumc_gramineeën_graph_image
show_name: false
show_state: false
```

### Create an automation based on pollen count
```yaml
automation:
  - alias: High Pollen Alert
    trigger:
      platform: numeric_state
      entity_id: sensor.lumc_gramineeën_total
      above: 80
    action:
      - service: persistent_notification.create
        data:
          message: "High pollen levels detected! Current: {{ states('sensor.lumc_gramineeën_total') }} µg/m³"
          title: "Pollen Alert"
```

### Get pollen data in templates
```jinja2
Current pollen count: {{ states('sensor.lumc_gramineeën_total') }} µg/m³
Graph URL: {{ state_attr('sensor.lumc_gramineeën_total', 'graph_url') }}
```

### Create a template sensor for pollen category
```yaml
template:
  - sensor:
      - name: "Pollen Level Category"
        unique_id: pollen_category
        state: >
          {% set pollen = states('sensor.lumc_gramineeën_total') | int(0) %}
          {% if pollen < 20 %}Low
          {% elif pollen < 50 %}Medium
          {% elif pollen < 100 %}High
          {% else %}Very High
          {% endif %}
```

## Architecture

- **`__init__.py`**: Integration entry point and setup
- **`config_flow.py`**: UI configuration flow with pollen type validation
- **`const.py`**: Configuration constants and defaults
- **`lumc_client.py`**: Core scraper logic (ported from original `lumc.py`)
- **`sensor.py`**: Home Assistant sensor entities and data coordinator
- **`manifest.json`**: Integration metadata
- **`strings.json`**: UI localization strings

## Memory Cache

The integration uses an in-memory cache with configurable TTL to minimize requests to the LUMC website:

- Cache is stored per integration instance in the `LUMCPollenClient`
- Configurable TTL (default: 15 minutes)
- Automatic cache invalidation when new data is fetched
- Separate caches for:
  - HTML page content (soup)
  - Parsed table rows and pollen names
  - Graph links

## Update Coordinator

The integration uses Home Assistant's `DataUpdateCoordinator` for efficient updates:

- Default scan interval: 30 minutes
- Configurable via options flow
- Automatic retry on failures
- Coordinator state tracking

## Requirements

- Home Assistant 2023.12 or later
- `requests>=2.32.3` library
- `beautifulsoup4>=4.12.3` library

## Differences from Original Docker Setup

| Aspect | Original (Docker) | HA Integration |
|--------|-------------------|-----------------|
| Deployment | Docker container | Native HA custom component |
| Web Server | Flask + Gunicorn | DataUpdateCoordinator |
| HTTP API | Yes (port 8000) | No (direct sensor data) |
| Configuration | Environment variables | HA UI config flow |
| Cache | In-memory | In-memory |
| Data Access | REST endpoints | Native Home Assistant entities |
| Caching Layer | Flask app level | Client level |

## Troubleshooting

### "Pollen type not found" during setup
Make sure the pollen type name matches exactly what's on the LUMC website. The integration should auto-detect available types during setup.

### Data not updating
- Check the scan interval in the integration options
- Verify Home Assistant has internet access to the LUMC website
- Monitor the Home Assistant logs for errors

### Graph image not displaying
- Ensure the `graph_image` sensor state contains a valid base64-encoded data URL
- Check if your display entity supports base64 image data URLs
- Verify the LUMC website is accessible and serving images

### Integration fails to load
- Check Home Assistant logs for specific error messages
- Ensure `requests` and `beautifulsoup4` are installed
- Verify the LUMC base URL is correct

## Contributing

Feel free to submit issues or pull requests to improve this integration.

## License

Same as the original repository.
