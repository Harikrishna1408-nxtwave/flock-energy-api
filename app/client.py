import httpx

from app.config import settings


class UrjaPortalError(Exception):
    """Raised when communication with the Urja portal fails."""


class UrjaPortalClient:
    def __init__(self) -> None:
        self.base_url = settings.urja_base_url.rstrip("/")
        self.client = httpx.AsyncClient(
            timeout=settings.request_timeout,
            follow_redirects=False,
        )
        self.authenticated = False

    async def login(self) -> None:
        """Authenticate with the Urja portal and verify the session."""
        try:
            headers = {
                "Accept": "application/json",
                "Origin": self.base_url,
                "Referer": f"{self.base_url}/login",
                "X-Sveltekit-Action": "true",
            }

            response = await self.client.post(
                f"{self.base_url}/login",
                data={
                    "email": settings.urja_username,
                    "password": settings.urja_password,
                },
                headers=headers,
            )

            print("Login HTTP status:", response.status_code)
            print(
                "Set-Cookie header present:",
                "set-cookie" in response.headers,
            )

            # Do not print response headers or cookie values.
            response.raise_for_status()

            # The portal may return a JSON redirect instruction.
            try:
                payload = response.json()
            except ValueError as exc:
                raise UrjaPortalError(
                    "The portal returned an unexpected login response."
                ) from exc

            if isinstance(payload, dict):
                print("Login response type:", payload.get("type"))
                print("Login redirect status:", payload.get("status"))

            # Verify that the session can access protected meter data.
            check = await self.client.get(
                f"{self.base_url}/portal/meters/search",
                params={"q": "", "page": 1},
                headers={"Accept": "application/json"},
            )

            print("Protected endpoint status:", check.status_code)

            if check.status_code in (401, 403):
                raise UrjaPortalError(
                    "Login did not establish a valid portal session."
                )

            check.raise_for_status()

            try:
                meter_data = check.json()
            except ValueError as exc:
                raise UrjaPortalError(
                    "The portal returned invalid meter-search JSON."
                ) from exc

            if not isinstance(meter_data, dict) or not isinstance(
                meter_data.get("data"), list
            ):
                raise UrjaPortalError(
                    "The meter-search response has an unexpected structure."
                )

            self.authenticated = True
            print("Portal authentication verified successfully.")

        except httpx.HTTPError as exc:
            print("HTTP error type:", type(exc).__name__)
            print("HTTP error details:", str(exc))
            raise UrjaPortalError(
                "Unable to connect to or authenticate with the Urja portal."
            ) from exc
    
    async def _ensure_authenticated(self) -> None:
        if not self.authenticated:
            await self.login()

    async def _get_json(self, path: str, **params):
        await self._ensure_authenticated()

        try:
            response = await self.client.get(
                f"{self.base_url}{path}",
                params=params,
            )

            if response.status_code in (401, 403):
                self.authenticated = False
                raise UrjaPortalError(
                    "Portal session expired or access was denied."
                )

            response.raise_for_status()
            return response.json()

        except httpx.HTTPError as exc:
            raise UrjaPortalError(
                "The Urja portal request failed."
            ) from exc
        except ValueError as exc:
            raise UrjaPortalError(
                "The Urja portal returned invalid JSON."
            ) from exc

    async def search_meters(
        self, query: str = "", page: int = 1
    ) -> dict:
        return await self._get_json(
            "/portal/meters/search",
            q=query,
            page=page,
        )

    async def get_consumption(self, meter_id: str) -> dict:
        return await self._get_json(
            f"/portal/meters/{meter_id}/energy"
        )


    async def get_meter(self, meter_id: str) -> dict:
            result = await self.search_meters(query=meter_id, page=1)
    
            for meter in result.get("data", []):
                if meter.get("meterId") == meter_id:
                    return meter
    
            raise UrjaPortalError(f"Meter '{meter_id}' was not found.")

    async def close(self) -> None:
        await self.client.aclose()