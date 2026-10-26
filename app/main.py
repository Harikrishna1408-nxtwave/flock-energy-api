from contextlib import asynccontextmanager
from typing import Annotated

from fastapi.responses import HTMLResponse
from fastapi import FastAPI, HTTPException, Query, Request, status

from app.client import UrjaPortalClient, UrjaPortalError
from app.models import (
    ConsumptionResponse,
    HealthResponse,
    Meter,
    MeterListResponse,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = UrjaPortalClient()
    app.state.urja_client = client

    try:
        yield
    finally:
        await client.close()


app = FastAPI(
    title="Flock Energy Meter API",
    description=(
        "REST API wrapper for the legacy Urja Meter Operations portal."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def homepage():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Flock Energy | Meter API</title>
        <style>
            * {
                box-sizing: border-box;
            }

            body {
                margin: 0;
                font-family: Arial, sans-serif;
                background: #0b1020;
                color: #f8fafc;
            }

            header {
                padding: 24px 8%;
                border-bottom: 1px solid #263149;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .brand {
                font-size: 20px;
                font-weight: bold;
            }

            .badge {
                color: #86efac;
                background: #123326;
                border: 1px solid #236647;
                padding: 8px 14px;
                border-radius: 30px;
                font-size: 13px;
            }

            main {
                max-width: 1000px;
                margin: 90px auto;
                padding: 0 24px;
            }

            .eyebrow {
                color: #60a5fa;
                text-transform: uppercase;
                letter-spacing: 3px;
                font-size: 12px;
                font-weight: bold;
            }

            h1 {
                font-size: clamp(38px, 7vw, 68px);
                line-height: 1.08;
                margin: 20px 0;
            }

            h1 span {
                color: #60a5fa;
            }

            .description {
                max-width: 680px;
                color: #b7c2d6;
                font-size: 18px;
                line-height: 1.8;
            }

            .actions {
                display: flex;
                flex-wrap: wrap;
                gap: 14px;
                margin: 32px 0 50px;
            }

            .button {
                display: inline-block;
                padding: 14px 22px;
                border-radius: 9px;
                text-decoration: none;
                font-weight: bold;
            }

            .primary {
                color: #08111f;
                background: #60a5fa;
            }

            .secondary {
                color: #f8fafc;
                border: 1px solid #475569;
            }

            .grid {
                display: grid;
                grid-template-columns: repeat(
                    auto-fit, minmax(220px, 1fr)
                );
                gap: 18px;
            }

            .card {
                background: #121b2e;
                border: 1px solid #293750;
                border-radius: 14px;
                padding: 24px;
            }

            .card h2 {
                font-size: 17px;
                margin-top: 0;
            }

            .card p {
                color: #aebbd0;
                line-height: 1.6;
                font-size: 14px;
            }

            footer {
                text-align: center;
                color: #8b9ab2;
                padding: 30px 20px;
                border-top: 1px solid #263149;
                font-size: 13px;
            }

            @media (max-width: 600px) {
                header {
                    padding: 20px;
                }

                main {
                    margin: 55px auto;
                }
            }
        </style>
    </head>
    <body>
        <header>
            <div class="brand">FLOCK ENERGY</div>
            <div class="badge">● API Service</div>
        </header>

        <main>
            <div class="eyebrow">Meter Operations Platform</div>

            <h1>
                Energy Data.<br>
                <span>Simplified.</span>
            </h1>

            <p class="description">
                A REST API wrapper built with Python and FastAPI
                that connects to the legacy Urja Meter Operations
                portal and exposes meter information and energy
                consumption readings through structured endpoints.
            </p>

            <div class="actions">
                <a class="button primary" href="/docs">
                    Explore API Docs →
                </a>
                <a class="button secondary" href="/api/v1/health">
                    Health Check
                </a>
            </div>

            <section class="grid">
                <article class="card">
                    <h2>01. Meter Search</h2>
                    <p>
                        Retrieve meter records with query and
                        pagination parameters.
                    </p>
                    <a href="/api/v1/meters?page=1">
                        Explore meters →
                    </a>
                </article>

                <article class="card">
                    <h2>02. Meter Details</h2>
                    <p>
                        Retrieve information about an individual
                        meter using its identifier.
                    </p>
                    <a href="/api/v1/meters/J100001">
                        View example →
                    </a>
                </article>

                <article class="card">
                    <h2>03. Energy Consumption</h2>
                    <p>
                        Retrieve available energy readings for
                        a specified meter.
                    </p>
                    <a href="/api/v1/meters/J100001/consumption">
                        View readings →
                    </a>
                </article>
            </section>
        </main>

        <footer>
            Flock Energy Meter API · Built with FastAPI and Python
        </footer>
    </body>
    </html>
    """


def get_client(request: Request) -> UrjaPortalClient:
    return request.app.state.urja_client


@app.get("/api/v1/health", response_model=HealthResponse)
async def health():
    return {
        "status": "ok",
        "portal": "urja",
    }


@app.get("/api/v1/meters", response_model=MeterListResponse)
async def list_meters(
    request: Request,
    q: Annotated[str, Query(description="Search meters by query")] = "",
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
):
    client = get_client(request)

    try:
        result = await client.search_meters(query=q, page=page)

        # Validate upstream data before returning it.
        return {
            "data": result.get("data", []),
            "total": result["total"],
            "page": result["page"],
            "pageSize": result["pageSize"],
        }

    except UrjaPortalError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to retrieve meters from the upstream portal.",
        ) from exc


@app.get("/api/v1/meters/{meter_id}", response_model=Meter)
async def meter_details(request: Request, meter_id: str):
    client = get_client(request)

    try:
        result = await client.get_meter(meter_id)
        return result

    except UrjaPortalError as exc:
        if "was not found" in str(exc):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meter not found.",
            ) from exc

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to retrieve meter details.",
        ) from exc


@app.get(
    "/api/v1/meters/{meter_id}/consumption",
    response_model=ConsumptionResponse,
)
async def meter_consumption(request: Request, meter_id: str):
    client = get_client(request)

    try:
        result = await client.get_consumption(meter_id)
        return result

    except UrjaPortalError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to retrieve meter consumption.",
        ) from exc