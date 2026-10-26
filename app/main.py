from contextlib import asynccontextmanager
from typing import Annotated

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