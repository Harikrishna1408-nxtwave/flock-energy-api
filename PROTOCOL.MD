# Urja Meter Operations Portal — Protocol Notes

## 1. Overview

The Flock Energy Meter API communicates with the legacy Urja Meter Operations portal:

`https://urja-ops.flockenergy.tech`

The upstream service provides meter-search, transformer, and energy-consumption data. Authentication is session-based.

These notes distinguish observed behavior from implementation assumptions.

## 2. Authentication

### Login endpoint

- Method: `POST`
- Path: `/login`
- Content type: `application/x-www-form-urlencoded`

### Form fields

| Field      | Description           |
| ---------- | --------------------- |
| `email`    | Portal username/email |
| `password` | Portal password       |

### Relevant request headers

The browser's successful login request included:

- `Accept: application/json`
- `Origin: https://urja-ops.flockenergy.tech`
- `Referer: https://urja-ops.flockenergy.tech/login`
- `X-Sveltekit-Action: true`

The Python implementation uses these headers when submitting the login form.

### Observed response

A successful browser login returned:

- HTTP status: `200 OK`
- Content type: `application/json`
- A `Set-Cookie` response header
- A JSON redirect instruction indicating status `303`

The session cookie was stored and reused by the HTTP client. A subsequent meter-search request returned `200 OK`.

**Security:** Cookie values and credentials must not be included in source code, logs, documentation, or version control.

## 3. Meter Search

### Endpoint

`GET /portal/meters/search`

### Query parameters

| Parameter | Observed purpose |
| --------- | ---------------- |
| `q`       | Search query     |
| `page`    | Page number      |

### Observed response structure

```json
{
  "data": [
    {
      "meterId": "J100000",
      "serialNo": "SE33962",
      "make": "HPL",
      "phaseType": "single",
      "installStatus": "Decommissioned",
      "dtCode": "DT-001"
    }
  ],
  "total": 403,
  "page": 1,
  "pageSize": 20
}
```

The example is based on an observed response. The total number of records may change.

### Meter fields

| Field           | Meaning                                  |
| --------------- | ---------------------------------------- |
| `meterId`       | Meter identifier                         |
| `serialNo`      | Serial number                            |
| `make`          | Manufacturer                             |
| `phaseType`     | Electrical phase type                    |
| `installStatus` | Installation status                      |
| `dtCode`        | Associated distribution-transformer code |

## 4. Transformer Data

### Endpoint

`GET /portal/dts?page=1`

The observed response contained transformer records with fields including:

- `code`
- `name`
- `feederCode`
- `capacityKva`

The observed first page contained 20 records, with 40 records reported in total at the time of inspection.

Meter `dtCode` values corresponded to transformer `code` values in the observed sample.

## 5. Meter Details

A meter detail page request was observed at:

`GET /meters/{meter_id}/__data.json?x-sveltekit-invalidated=001`

The response used SvelteKit's serialized page-data format rather than a straightforward meter JSON object.

The page data included meter attributes and hierarchy information such as zone, circle, division, subdivision, substation, feeder, and transformer.

Parsing this serialized page-data format is more brittle than consuming a documented JSON API. The wrapper currently retrieves individual meter details using the meter-search endpoint instead.

## 6. Energy Consumption

### Endpoint

`GET /portal/meters/{meter_id}/energy`

### Observed response fields

| Field       | Description                    |
| ----------- | ------------------------------ |
| `timestamp` | Reading timestamp              |
| `kwh`       | Energy reading in kWh          |
| `kvah`      | Energy reading in kVAh         |
| `voltR`     | Observed R-phase voltage field |

The timestamp format observed was:

`DD/MM/YYYY HH:mm`

Numeric readings were represented as strings in the observed response.

The timestamp did not include a timezone. The wrapper should not silently interpret it as UTC.

The readings have not been independently verified as interval consumption rather than cumulative readings. Therefore, the wrapper preserves the upstream reading semantics and does not calculate interval consumption.

## 7. Error Handling

Observed behavior:

- Requests without a valid session can return `401 Unauthorized`.
- A successful login followed by a protected meter-search request returned `200 OK`.
- The upstream service may reject requests that do not follow its expected login request format.

The wrapper converts upstream communication and authentication failures into application-level errors.

## 8. Limitations and Assumptions

- Authentication relies on session cookies.
- The login behavior is based on observed requests rather than a published upstream authentication specification.
- Session expiration and reauthentication should be tested more thoroughly.
- Meter lookup depends on the upstream search endpoint's behavior and pagination.
- The serialized meter-detail page format is not currently parsed.
- Consumption timestamps have no verified timezone.
- Numeric fields and response structures may change upstream.

## 9. Recommended Future Improvements

- Add mocked tests for upstream responses and authentication failures.
- Test session expiration and reauthentication.
- Verify meter search semantics and exact-match behavior.
- Add retries for appropriate transient failures.
- Add structured logging with secrets redacted.
- Validate upstream response schemas and document schema changes.
- Investigate whether the portal exposes a stable meter-detail JSON endpoint.
