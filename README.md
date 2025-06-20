# x-agentic-ai

A tool for monitoring F5 BIG-IP devices and other security devices using OpenTelemetry, Prometheus, and a custom React dashboard.

## Setup

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd x-agentic-ai
   ```

2. Copy and edit environment variables:
   ```bash
   cp config/.env.device-secrets-example config/.env.device-secrets
   vi config/.env.device-secrets
   ```

3. Generate configurations:
   ```bash
   docker run --rm -it -w /app -v ${PWD}:/app --entrypoint /app/otel-collector/bin/init_entrypoint.sh python:3.12.6-slim-bookworm --generate-config
   ```

4. Start the services:
   ```bash
   docker compose up --build
   ```

5. Access the dashboard at `http://localhost:3000`.

## Syslog Configuration

- Configure devices to send Syslog to the collector (TCP port 54527).
- Example for BIG-IP:
  ```bash
  tmsh modify sys syslog remote-servers add { otel-collector { host <collector-ip> remote-port 54527 } }
  ```

## Customization

- Extend the dashboard in `src/dashboard/src/App.jsx` and `src/dashboard/src/components/`.
- Modify Syslog settings in `config/syslog/syslog_config.yaml`.
- Add remediation scripts in `otel-collector/bin/` or a separate service.
- Optional: Enable F5 Datafabric by uncommenting the exporter in `otel-collector/x-agentic-ai-scraper-config.yaml` and setting `SENSOR_ID` and `SENSOR_SECRET_TOKEN`.