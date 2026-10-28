# Skill Lab presentation requirements: implementation map

This note maps the submitted `Skill_Lab_ppt.pptx` requirements to the ReliefSync project. It distinguishes implemented functions from integrations that need external credentials and roadmap items.

## Included in this project

| Presentation requirement | Project implementation | Status / limitation |
|---|---|---|
| Responsive full-stack application | React/Vite frontend and FastAPI backend | Implemented; use the Windows launcher or the documented local commands.
| Interactive disaster dashboard and map | Operational dashboard, Leaflet map, filters, markers and region-based density/heat layers | Implemented; map/data availability depends on coordinates and source APIs.
| Login and security | Individual registration/login, hashed passwords, signed expiring bearer tokens, operator route authorization, validation and audit logging | Implemented; configure `AUTH_SECRET`, production settings and registration policy before sharing/deployment.
| Volunteers, shelters, inventory and resource allocation | CRUD workflows, availability/capacity/stock bounds, allocation recommendations and lifecycle | Implemented.
| Incident priority and recommendations | Explainable rule-based score and resource suggestions | Implemented as decision support, not a validated impact model.
| Worldwide disaster observations | USGS, GDACS, NASA EONET, optional NASA FIRMS; external observations stay separate from operational incidents | Implemented; FIRMS requires a free MAP_KEY and configured area. Sources can rate-limit or be temporarily unavailable.
| Weather and space-derived/environmental information | Open-Meteo forecasts, NASA EONET metadata, NASA FIRMS thermal-anomaly data | Implemented with source labels; not an official warning. ISRO/MOSDAC has no direct integration in this project because no supported public API and credentials were configured.
| MongoDB | MongoDB archive for collected external observations, with status and connection configuration | Implemented as a separate archive; operational workflows continue to use SQLAlchemy SQLite by default. Local MongoDB or Atlas must be running/configured.
| LLM incident summaries and operational Q&A | Local Ollama for priority explanations and new operator-only Q&A from a bounded snapshot that excludes contacts | Implemented; install/start Ollama and pull the configured model for generated answers. Without it, Q&A explicitly falls back to recorded totals. It does not issue actions.
| Demand forecast | New 7/14/30-day projection using the prior 28 days of delivered allocation history | Implemented as a transparent planning estimate. Sparse/seeded history affects quality; it is not an ML-validated forecast or an order.
| Gmail API campaign messages | Gmail API OAuth refresh-token sender added alongside SMTP, behind the existing operator preview/approval, consent and audit workflow | Code included; requires a Google Cloud OAuth client, Gmail send scope, refresh token, sender configuration and `NOTIFICATIONS_MODE=live`. By default delivery remains simulated. Provider acceptance is not confirmed delivery.
| Email/SMS regional alerts | Area-filtered opt-in/consented campaign workflow, preview, human approval, idempotency and delivery status | SMS requires Twilio; email requires Gmail OAuth or SMTP. ReliefSync is not a government cell-broadcast/emergency alert system.
| Data management | SQL operational store, external observation archive, duplicate handling, backups/migrations, source labels and audit logs | Implemented as described in README and setup docs.

## Roadmap items from the presentation

Mobile offline access/synchronization, multilingual UI, direct government-data integrations, validated forecasting, optimized logistics routing, and a formal accessibility/low-bandwidth program remain future work. Existing responsive layout, routing suggestions and accessible labels are partial foundations, not a claim that those roadmap items are complete.

## Startup database-path fix

When `DATABASE_URL=sqlite:///./data/reliefsync.db` is explicitly set, SQLAlchemy resolves that relative location from the backend process working directory. SQLite does not create missing parent directories. `backend/app/database.py` now parses file-backed SQLite URLs and creates the parent folder before creating the engine. This addresses the pasted `sqlite3.OperationalError: unable to open database file` during FastAPI startup without deleting or replacing an existing database.

## Setup references

- Local app and feature guide: `README.md`
- External APIs, MongoDB and notification configuration: `FREE-API-SETUP.md`
- Dataset date range and source limits: `docs/REGIONAL-DATA.md`
- Test commands and current verification: `TESTING.md`
