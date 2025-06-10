from pydantic import BaseModel
from pydantic import Field


class AlkotekaConfig(BaseModel):
    """Centralized configuration for Alkoteka spider with validated settings."""

    BASE_URL: str = "https://alkoteka.com"
    API_BASE_URL: str = "/web-api/v1/product"
    CITY_UUID: str = "4a70f9e0-46ae-11e7-83ff-00155d026416"

    CATEGORY_SLUGS: list[str] = [
        "shampanskoe-i-igristoe",
        "krepkiy-alkogol",
        "slaboalkogolnye-napitki-2",
        "enogram",
        "axioma-spirits",
        "bezalkogolnye-napitki-1",
        "produkty-1",
        "aksessuary-2",
        "podarki-i-nabory-1",
        "skidki",
    ]

    HEADERS: dict[str, str] = Field(
        default_factory=lambda: {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.5",
        }
    )

    @property
    def full_api_url(self) -> str:
        """Construct full API URL from base components."""
        return f"{self.BASE_URL}{self.API_BASE_URL}"


aconfig = AlkotekaConfig()
