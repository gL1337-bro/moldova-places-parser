"""
Data models for parsed places.
"""
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any, List
from datetime import datetime
import json


@dataclass
class Place:
    """Represents a place/venue from OSM."""
    # Core identification
    osm_id: str  # "node/123", "way/456", "relation/789"
    osm_type: str  # "node", "way", "relation"
    name: str
    category: str  # cafe, restaurant, bar, etc.

    # Location
    lat: float
    lon: float
    address: str = ""
    street: str = ""
    housenumber: str = ""
    city: str = ""
    suburb: str = ""
    postcode: str = ""
    country: str = "Moldova"

    # Contact
    phone: str = ""
    mobile: str = ""
    fax: str = ""
    email: str = ""
    website: str = ""
    contact_website: str = ""
    contact_facebook: str = ""
    contact_instagram: str = ""
    contact_twitter: str = ""
    contact_linkedin: str = ""
    contact_youtube: str = ""
    contact_whatsapp: str = ""
    contact_telegram: str = ""
    contact_skype: str = ""
    contact_name: str = ""
    operator: str = ""
    brand: str = ""

    # Details
    opening_hours: str = ""
    cuisine: str = ""
    wheelchair: str = ""
    outdoor_seating: str = ""
    takeaway: str = ""
    delivery: str = ""

    # Classification (Step 2)
    group: str = ""  # A, B, C
    social_url: str = ""  # extracted social media URL from group B

    # Scoring (Step 3)
    priority_score: float = 0.0
    priority_level: str = ""  # high, medium, low

    # Metadata
    raw_tags: Dict[str, Any] = field(default_factory=dict)
    fetched_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for DataFrame/export."""
        d = asdict(self)
        # Flatten raw_tags for CSV
        if self.raw_tags:
            for k, v in self.raw_tags.items():
                if k not in d:
                    d[f"tag_{k}"] = v
        return d

    def get_full_address(self) -> str:
        """Build full address string."""
        parts = []
        if self.street:
            addr = self.street
            if self.housenumber:
                addr += f" {self.housenumber}"
            parts.append(addr)
        if self.city:
            parts.append(self.city)
        if self.postcode:
            parts.append(self.postcode)
        if self.country:
            parts.append(self.country)
        return ", ".join(parts)

    def get_primary_phone(self) -> str:
        """Get best available phone number."""
        return self.phone or self.mobile or self.fax or ""

    def get_primary_website(self) -> str:
        """Get best available website."""
        return self.website or self.contact_website or ""

    def get_social_urls(self) -> List[str]:
        """Get all social media URLs."""
        urls = []
        for field in ["contact_facebook", "contact_instagram", "contact_twitter",
                      "contact_linkedin", "contact_youtube", "contact_whatsapp",
                      "contact_telegram", "contact_skype"]:
            val = getattr(self, field, "")
            if val:
                urls.append(val)
        return urls

    def has_contact_info(self) -> bool:
        """Check if place has any contact information."""
        return bool(self.get_primary_phone() or self.email or self.get_primary_website() or self.get_social_urls())

    def get_google_maps_link(self) -> str:
        """Generate Google Maps search link."""
        query = f"{self.name} {self.city} Moldova".replace(" ", "+")
        return f"https://www.google.com/maps/search/?api=1&query={query}"


@dataclass
class ExtractionStats:
    """Statistics for extraction run."""
    total_fetched: int = 0
    by_category: Dict[str, int] = field(default_factory=dict)
    by_city: Dict[str, int] = 0
    duplicates_removed: int = 0
    no_name_removed: int = 0
    excluded_transnistria: int = 0
    errors: List[str] = field(default_factory=list)

    def add_category(self, category: str, count: int = 1):
        self.by_category[category] = self.by_category.get(category, 0) + count

    def add_city(self, city: str, count: int = 1):
        self.by_city[city] = self.by_city.get(city, 0) + count

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_fetched": self.total_fetched,
            "by_category": self.by_category,
            "by_city": self.by_city,
            "duplicates_removed": self.duplicates_removed,
            "no_name_removed": self.no_name_removed,
            "excluded_transnistria": self.excluded_transnistria,
            "errors": self.errors
        }


def parse_osm_element(element: Dict[str, Any], category: str, category_label: str) -> Optional[Place]:
    """Parse OSM element (node/way/relation) into Place object."""
    tags = element.get("tags", {})

    # Skip if no name
    name = tags.get("name", "").strip()
    if not name:
        return None

    # Coordinates
    lat = element.get("lat")
    lon = element.get("lon")
    if lat is None and "center" in element:
        lat = element["center"].get("lat")
        lon = element["center"].get("lon")
    if lat is None or lon is None:
        return None

    # Address
    street = tags.get("addr:street", "")
    housenumber = tags.get("addr:housenumber", "")
    city = tags.get("addr:city", "")
    suburb = tags.get("addr:suburb", "")
    postcode = tags.get("addr:postcode", "")
    addr_full = tags.get("addr:full", "")

    # Contact
    phone = tags.get("phone", "")
    mobile = tags.get("contact:phone", "") or tags.get("contact:mobile", "")
    fax = tags.get("contact:fax", "")
    email = tags.get("email", "") or tags.get("contact:email", "")
    website = tags.get("website", "")
    contact_website = tags.get("contact:website", "")
    contact_facebook = tags.get("contact:facebook", "")
    contact_instagram = tags.get("contact:instagram", "")
    contact_twitter = tags.get("contact:twitter", "")
    contact_linkedin = tags.get("contact:linkedin", "")
    contact_youtube = tags.get("contact:youtube", "")
    contact_whatsapp = tags.get("contact:whatsapp", "")
    contact_telegram = tags.get("contact:telegram", "")
    contact_skype = tags.get("contact:skype", "")
    contact_name = tags.get("contact:name", "")
    operator = tags.get("operator", "")
    brand = tags.get("brand", "")

    # Details
    opening_hours = tags.get("opening_hours", "")
    cuisine = tags.get("cuisine", "")
    wheelchair = tags.get("wheelchair", "")
    outdoor_seating = tags.get("outdoor_seating", "")
    takeaway = tags.get("takeaway", "")
    delivery = tags.get("delivery", "")

    # Build address string
    address_parts = []
    if street:
        addr = street
        if housenumber:
            addr += f" {housenumber}"
        address_parts.append(addr)
    if suburb:
        address_parts.append(suburb)
    if city:
        address_parts.append(city)
    if postcode:
        address_parts.append(postcode)
    address = ", ".join(address_parts) if address_parts else addr_full

    place = Place(
        osm_id=f"{element['type']}/{element['id']}",
        osm_type=element["type"],
        name=name,
        category=category,
        lat=float(lat),
        lon=float(lon),
        address=address,
        street=street,
        housenumber=housenumber,
        city=city,
        suburb=suburb,
        postcode=postcode,
        phone=phone,
        mobile=mobile,
        fax=fax,
        email=email,
        website=website,
        contact_website=contact_website,
        contact_facebook=contact_facebook,
        contact_instagram=contact_instagram,
        contact_twitter=contact_twitter,
        contact_linkedin=contact_linkedin,
        contact_youtube=contact_youtube,
        contact_whatsapp=contact_whatsapp,
        contact_telegram=contact_telegram,
        contact_skype=contact_skype,
        contact_name=contact_name,
        operator=operator,
        brand=brand,
        opening_hours=opening_hours,
        cuisine=cuisine,
        wheelchair=wheelchair,
        outdoor_seating=outdoor_seating,
        takeaway=takeaway,
        delivery=delivery,
        raw_tags=tags
    )

    return place


if __name__ == "__main__":
    # Test parsing
    test_element = {
        "type": "node",
        "id": 12345,
        "lat": 47.0105,
        "lon": 28.8638,
        "tags": {
            "name": "Test Cafe",
            "amenity": "cafe",
            "addr:street": "Strada Stefan cel Mare",
            "addr:housenumber": "10",
            "addr:city": "Chișinău",
            "phone": "+373 22 123 456",
            "website": "https://example.com",
            "contact:instagram": "https://instagram.com/testcafe",
            "opening_hours": "Mo-Su 08:00-22:00"
        }
    }
    place = parse_osm_element(test_element, "cafe", "Кафе")
    print(place)
    print("Google Maps:", place.get_google_maps_link())