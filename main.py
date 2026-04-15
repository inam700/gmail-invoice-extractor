import base64
import sys
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()
client = Anthropic()


class Invoice(BaseModel):
    """The shape we want Claude to return. Like a TS interface, but enforced at runtime."""

    vendor: str = Field(description="Company or person who issued the invoice")
    invoice_number: str = Field(description="Invoice ID / number as printed")
    date: str = Field(description="Issue date in ISO format YYYY-MM-DD")
    total_amount: float = Field(description="Total amount due, as a number")
    currency: str = Field(description="3-letter ISO currency code, e.g. USD, EUR, PKR")


def media_type_for(suffix: str) -> str:
    """Map a file suffix (.jpg, .png, .webp) to the media type Claude expects."""
    ext = suffix.lstrip(".").lower()
    if ext == "jpg":
        ext = "jpeg"
    return f"image/{ext}"


def extract_invoice(image_path: Path) -> Invoice:
    image_bytes = image_path.read_bytes()
    image_b64 = base64.standard_b64encode(image_bytes).decode("utf-8")
    media_type = media_type_for(image_path.suffix)

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {"type": "base64", "media_type": media_type, "data": image_b64},
                    },
                    {
                        "type": "text",
                        "text": (
                            "Extract invoice fields. Return a JSON object matching this schema:\n"
                            f"{Invoice.model_json_schema()}"
                        ),
                    },
                ],
            },
            {"role": "assistant", "content": "{"},
        ],
    )

    raw = "{" + response.content[0].text
    return Invoice.model_validate_json(raw)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: uv run python main.py <path-to-invoice-image>")
        sys.exit(1)
    invoice = extract_invoice(Path(sys.argv[1]))
    print(invoice.model_dump_json(indent=2))
