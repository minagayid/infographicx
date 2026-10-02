"""God's Eye atlas endpoints.

This catalog deliberately returns source-linked public archives rather than copying
media. Clients can use the coordinates for an open map layer and follow the source
links to inspect licensing and download the original footage.
"""
from fastapi import APIRouter

router = APIRouter()

OPEN_SOURCES = [
    {"id": 1, "title": "Night lights over Manhattan", "location": "New York, United States", "region": "Americas", "country": "US", "type": "City aerial", "duration": "01:42", "source": "NASA / Wikimedia Commons", "source_url": "https://commons.wikimedia.org/wiki/Category:Videos_of_New_York_City", "footage_url": "https://commons.wikimedia.org/w/index.php?search=New+York+City+night+video&title=Special:MediaSearch&type=video", "lat": 40.7, "lon": -74.0, "tags": ["urban", "night"]},
    {"id": 2, "title": "Kraków old town walk", "location": "Kraków, Poland", "region": "Europe", "country": "PL", "type": "Street level", "duration": "03:18", "source": "Wikimedia Commons", "source_url": "https://commons.wikimedia.org/wiki/Category:Videos_of_Krak%C3%B3w", "footage_url": "https://commons.wikimedia.org/w/index.php?search=Krakow+street+video&title=Special:MediaSearch&type=video", "lat": 50.06, "lon": 19.94, "tags": ["heritage", "street"]},
    {"id": 3, "title": "Aerial view of Cape Town", "location": "Cape Town, South Africa", "region": "Africa", "country": "ZA", "type": "Coastal aerial", "duration": "02:26", "source": "Wikimedia Commons", "source_url": "https://commons.wikimedia.org/wiki/Category:Videos_of_Cape_Town", "footage_url": "https://commons.wikimedia.org/w/index.php?search=Cape+Town+aerial+video&title=Special:MediaSearch&type=video", "lat": -33.92, "lon": 18.42, "tags": ["coast", "landscape"]},
    {"id": 4, "title": "Tokyo from above", "location": "Tokyo, Japan", "region": "Asia-Pacific", "country": "JP", "type": "City aerial", "duration": "00:58", "source": "Wikimedia Commons", "source_url": "https://commons.wikimedia.org/wiki/Category:Videos_of_Tokyo", "footage_url": "https://commons.wikimedia.org/w/index.php?search=Tokyo+aerial+video&title=Special:MediaSearch&type=video", "lat": 35.68, "lon": 139.69, "tags": ["urban", "transit"]},
    {"id": 5, "title": "Amazon river basin", "location": "Manaus, Brazil", "region": "Americas", "country": "BR", "type": "Nature / river", "duration": "04:12", "source": "Internet Archive", "source_url": "https://archive.org/search?query=amazon%20river%20video", "footage_url": "https://archive.org/search?query=amazon%20river%20open%20footage", "lat": -3.12, "lon": -60.02, "tags": ["nature", "water"]},
    {"id": 6, "title": "Helsinki harbor cam", "location": "Helsinki, Finland", "region": "Europe", "country": "FI", "type": "Live camera", "duration": "LIVE", "source": "Wikimedia Commons", "source_url": "https://commons.wikimedia.org/wiki/Category:Videos_of_Helsinki", "footage_url": "https://commons.wikimedia.org/w/index.php?search=Helsinki+harbor+video&title=Special:MediaSearch&type=video", "lat": 60.17, "lon": 24.94, "tags": ["harbor", "live"]},
    {"id": 7, "title": "Kathmandu valley", "location": "Kathmandu, Nepal", "region": "Asia-Pacific", "country": "NP", "type": "Documentary", "duration": "05:04", "source": "Wikimedia Commons", "source_url": "https://commons.wikimedia.org/wiki/Category:Videos_of_Kathmandu", "footage_url": "https://commons.wikimedia.org/w/index.php?search=Kathmandu+valley+video&title=Special:MediaSearch&type=video", "lat": 27.72, "lon": 85.32, "tags": ["culture", "valley"]},
    {"id": 8, "title": "Iceland volcanic field", "location": "Reykjanes, Iceland", "region": "Europe", "country": "IS", "type": "Field recording", "duration": "02:51", "source": "Internet Archive", "source_url": "https://archive.org/search?query=iceland%20volcano%20video", "footage_url": "https://archive.org/search?query=iceland%20volcano%20open%20footage", "lat": 63.86, "lon": -22.55, "tags": ["geology", "field"]},
]


@router.get("/catalog")
async def list_open_catalog(region: str | None = None, q: str | None = None):
    """Return source-linked, public-footage points for the atlas."""
    results = OPEN_SOURCES
    if region and region.lower() != "all regions":
        results = [item for item in results if item["region"].lower() == region.lower()]
    if q:
        needle = q.lower()
        results = [item for item in results if needle in f'{item["title"]} {item["location"]} {" ".join(item["tags"])}'.lower()]
    return {"count": len(results), "map": {"provider": "OpenStreetMap", "attribution_url": "https://www.openstreetmap.org/copyright"}, "items": results}


@router.get("/sources")
async def list_open_sources():
    """Describe the open services used by God's Eye."""
    return {"sources": [
        {"name": "OpenStreetMap", "role": "Basemap and place geometry", "url": "https://www.openstreetmap.org/", "license": "ODbL"},
        {"name": "Wikimedia Commons", "role": "Community-uploaded media and video archive", "url": "https://commons.wikimedia.org/", "license": "Per-file license; inspect attribution"},
        {"name": "Internet Archive", "role": "Public archive search for open footage", "url": "https://archive.org/", "license": "Per-item license; inspect rights metadata"},
    ]}
