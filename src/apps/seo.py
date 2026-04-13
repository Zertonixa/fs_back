from datetime import datetime, UTC

from fastapi import APIRouter, Response, status
from fastapi.responses import PlainTextResponse

seo_router = APIRouter()

SITE_URL = "http://localhost:3000"

INDEXABLE_ROUTES: list[str] = [
    "/",
    "/welcome",
    "/booking",
    "/login",
]

DISALLOW_ROUTES: list[str] = [
    "/admin",
    "/ban",
]


@seo_router.get("/robots.txt", response_class=PlainTextResponse, include_in_schema=False)
async def robots_txt() -> str:
    disallow_lines = "\n".join(f"Disallow: {route}" for route in DISALLOW_ROUTES)

    return (
        "User-agent: *\n"
        f"{disallow_lines}\n\n"
        f"Sitemap: {SITE_URL}/sitemap.xml\n"
    )


@seo_router.get("/sitemap.xml", include_in_schema=False)
async def sitemap_xml() -> Response:
    now = datetime.now(UTC).date().isoformat()

    urls = "\n".join(
        f"""
    <url>
        <loc>{SITE_URL}{route}</loc>
        <lastmod>{now}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>{"1.0" if route == "/" else "0.8"}</priority>
    </url>
        """.strip()
        for route in INDEXABLE_ROUTES
    )

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset
    xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    {urls}
</urlset>
"""

    return Response(content=xml, media_type="application/xml")


@seo_router.get("/gone", include_in_schema=False)
async def gone_page() -> Response:
    return Response(
        content="This page has been permanently removed.",
        status_code=status.HTTP_410_GONE,
        media_type="text/plain",
    )