# Event Schema and Taxonomy

## Core event schema

| Field | Type | Description | Required | Example |
| --- | --- | --- | --- | --- |
| timestamp | string (ISO 8601 with UTC offset) | Event time in UTC with offset (e.g., `2025-01-15T13:45:30+00:00`). | Yes | `2025-01-15T13:45:30+00:00` |
| source | string | System or subsystem that emitted the event. | Yes | `auth-service` |
| event_type | string | Event type from the taxonomy below. | Yes | `login` |
| device | object | Device descriptor (may contain `device_id`, `type`, `os`, `user_agent`). | Conditional | `{ "device_id": "dev-123", "type": "mobile" }` |
| ip | string | IP address (IPv4/IPv6). | Conditional | `203.0.113.42` |
| location | object | Geolocation info (may contain `country`, `region`, `city`, `lat`, `lon`). | Conditional | `{ "country": "US", "region": "CA", "city": "San Francisco" }` |
| confidence | number (0.0–1.0) | Confidence score for derived fields (location/device inference). | Conditional | `0.82` |
| raw_reference | string | Pointer to raw source record (log ID, blob URL, etc.). | Yes | `log:auth/2025-01-15/abc123` |

## Event type taxonomy

- `login`
- `logout`
- `device_register`
- `device_update`
- `location_ping`
- `message_metadata`
- `message_send`
- `message_receive`
- `session_start`
- `session_end`
- `api_request`
- `api_response`
- `permission_change`
- `account_recovery`
- `mfa_challenge`
- `mfa_result`

## Minimum required fields per event type

| Event type | Minimum required fields |
| --- | --- |
| login | `timestamp`, `source`, `event_type`, `device.device_id` **or** `ip`, `raw_reference` |
| logout | `timestamp`, `source`, `event_type`, `raw_reference` |
| device_register | `timestamp`, `source`, `event_type`, `device.device_id`, `raw_reference` |
| device_update | `timestamp`, `source`, `event_type`, `device.device_id`, `raw_reference` |
| location_ping | `timestamp`, `source`, `event_type`, `location` **or** `ip`, `raw_reference` |
| message_metadata | `timestamp`, `source`, `event_type`, `raw_reference` |
| message_send | `timestamp`, `source`, `event_type`, `raw_reference` |
| message_receive | `timestamp`, `source`, `event_type`, `raw_reference` |
| session_start | `timestamp`, `source`, `event_type`, `raw_reference` |
| session_end | `timestamp`, `source`, `event_type`, `raw_reference` |
| api_request | `timestamp`, `source`, `event_type`, `raw_reference` |
| api_response | `timestamp`, `source`, `event_type`, `raw_reference` |
| permission_change | `timestamp`, `source`, `event_type`, `raw_reference` |
| account_recovery | `timestamp`, `source`, `event_type`, `raw_reference` |
| mfa_challenge | `timestamp`, `source`, `event_type`, `raw_reference` |
| mfa_result | `timestamp`, `source`, `event_type`, `raw_reference` |

## Missing fields handling

- **Unknown vs. missing**: If a field is not available, omit it entirely. Do not use empty strings or sentinel values. Use `null` only when the field is explicitly present but unknown (e.g., a device is known but the `os` is not).
- **Conditionally required fields**: Some event types allow either `device.device_id` or `ip` to satisfy device presence (e.g., `login`). If neither is available, the event should be rejected or placed into a quarantine queue for enrichment.
- **Derived fields**: Fields like `location` may be derived from `ip` or device telemetry. If derivation fails, omit the derived field and set `confidence` to `0.0` only when a derived field is included but is highly uncertain. If no derived fields are present, omit `confidence`.
- **Raw reference**: Always required. If no stable reference exists, create one at ingestion (e.g., UUID) and store the raw payload in a retrievable location keyed by that reference.

## Confidence assignment

Confidence applies to derived or inferred fields (e.g., `location`, `device` details inferred from user agent):

- **1.00**: Verified by authoritative source (e.g., device enrollment record, GPS).
- **0.80–0.99**: High-confidence inference (e.g., IP-to-geo match with recent ASN validation).
- **0.50–0.79**: Moderate inference (e.g., user-agent parsing without device enrollment match).
- **0.01–0.49**: Weak inference (e.g., IP-to-geo without ASN consistency).
- **0.00**: Included only when an inferred field is present but effectively unreliable.

When multiple inferred fields are present, set `confidence` to the lowest confidence among them to avoid overstating certainty.
