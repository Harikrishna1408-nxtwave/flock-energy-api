# Flock Energy Meter API

A REST API wrapper around the legacy Urja Meter Operations portal. The application uses FastAPI and HTTPX to authenticate with the upstream portal, maintain a session, and expose meter information through documented API endpoints.

## Features

- Authentication with the Urja portal.
- Persistent session cookies using an HTTPX client.
- Meter listing and search.
- Individual meter lookup.
- Meter energy-consumption retrieval.
- Request validation and structured responses using Pydantic.
- Interactive Swagger documentation.
- Automated tests.

## Technology Stack

- Python 3.11
- FastAPI
- HTTPX
- Pydantic
- pydantic-settings
- pytest

## Project Structure

```text
flock-energy-api/
├── app/
│   ├── __init__.py
│   ├── client.py
│   ├── config.py
│   ├── main.py
│   └── models.py
├── tests/
│   └── test_api.py
├── .env.example
├── .gitignore
├── openapi.json
├── PROTOCOL.MD
├── README.md
├── REFLECTION.md
└── requirements.txt
```

## Prerequisites

- Python 3.11 or a compatible Python 3.10+ release.
- Access to the Urja Meter Operations portal.
- Valid portal credentials provided for the assignment.

## Setup

Clone the repository and navigate to its directory:

```bash
git clone <YOUR_PUBLIC_GITHUB_REPOSITORY_URL>
cd flock-energy-api
```

Create and activate a virtual environment.

Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Create a local `.env` file using `.env.example` as a template.

Configure these variables:

```dotenv
URJA_BASE_URL=https://urja-ops.flockenergy.tech
URJA_USERNAME=your-assignment-username
URJA_PASSWORD=your-assignment-password
REQUEST_TIMEOUT=15
```

Use the actual credentials supplied for the assignment. Never commit `.env` or credentials to Git.

## Running the Application

Start the development server:

```powershell
uvicorn app.main:app --reload
```

The default local address is:

`http://127.0.0.1:8000`

Interactive API documentation:

`http://127.0.0.1:8000/docs`

OpenAPI specification:

`http://127.0.0.1:8000/openapi.json`

## API Endpoints

| Method | Endpoint                                | Description              |
| ------ | --------------------------------------- | ------------------------ |
| GET    | `/api/v1/health`                        | Check API health         |
| GET    | `/api/v1/meters`                        | List meters              |
| GET    | `/api/v1/meters?q=J100001&page=1`       | Search meters            |
| GET    | `/api/v1/meters/{meter_id}`             | Retrieve a meter         |
| GET    | `/api/v1/meters/{meter_id}/consumption` | Retrieve energy readings |

### Example Requests

Health check:

```bash
curl http://127.0.0.1:8000/api/v1/health
```

List meters:

```bash
curl "http://127.0.0.1:8000/api/v1/meters?page=1"
```

Search meters:

```bash
curl "http://127.0.0.1:8000/api/v1/meters?q=J100001&page=1"
```

Retrieve a meter:

```bash
curl http://127.0.0.1:8000/api/v1/meters/J100001
```

Retrieve consumption:

```bash
curl http://127.0.0.1:8000/api/v1/meters/J100001/consumption
```

## Testing

Run the automated tests:

```powershell
python -m pytest -v
```

The initial automated test suite checks the health endpoint and unknown-route handling.

## Design Decisions and Limitations

- The application maintains a reusable HTTPX client so authenticated cookies can be reused across requests.
- Credentials are loaded from environment variables.
- Pydantic models validate the API response structures.
- The meter details implementation currently uses the upstream meter-search endpoint.
- Meter lookup behavior depends on how the upstream portal handles its search query and pagination.
- Upstream authentication and data availability are required for meter operations.
- Consumption timestamps and numeric fields depend on the format returned by the upstream portal.
- The API does not currently implement application-level caching or rate limiting.

## Security

- Keep credentials in `.env`.
- Exclude `.env` and `.venv/` from version control.
- Do not log passwords, session cookies, or authentication tokens.
- Use HTTPS when communicating with the upstream portal.

## Future Improvements

- Add mocked tests for upstream API responses.
- Improve session-expiration and reauthentication handling.
- Verify exact-match meter lookup across all relevant pages.
- Add stronger error classification and structured logging.
- Add response caching where appropriate.
- Add request-level rate limiting.
- Expand automated coverage for meter and consumption endpoints.

## Additional Documentation

- [PROTOCOL.md](PROTOCOL.MD): Upstream protocol observations.
- [REFLECTION.md](REFLECTION.md): Design decisions, trade-offs, and future improvements.
- [openapi.json](openapi.json): Generated OpenAPI specification.
