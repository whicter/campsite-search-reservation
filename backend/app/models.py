from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import date


class Campground(BaseModel):
    """Campground information"""
    id: str
    name: str
    provider: str
    description: Optional[str] = None


class AvailabilityRequest(BaseModel):
    """Request for availability search"""
    provider: str
    campground_id: str
    start_date: str  # YYYY-MM-DD format
    end_date: str    # YYYY-MM-DD format
    nights: Optional[int] = None  # If specified, search for consecutive nights within range


class AvailabilityResult(BaseModel):
    """Single availability result"""
    start_date: str  # YYYY-MM-DD format
    end_date: str    # YYYY-MM-DD format
    available: bool
    site_id: Optional[str] = None
    site_name: Optional[str] = None


class AvailabilityDetails(BaseModel):
    """Detailed availability information for range searches"""
    available_dates: List[Dict[str, Any]] = []
    campsites: Optional[List[Dict[str, Any]]] = None
    total_dates: int = 0
    total_unique_sites: int = 0


class AvailabilityResponse(BaseModel):
    """Response containing availability for requested dates"""
    campground_id: str
    campground_name: str
    provider: str
    start_date: str
    end_date: str
    available: bool
    message: Optional[str] = None
    reservation_url: Optional[str] = None
    nights: Optional[int] = None  # Number of nights if range search
    availability_details: Optional[AvailabilityDetails] = None  # Detailed info for range searches


class MultiCampgroundAvailabilityRequest(BaseModel):
    """Request for searching multiple campgrounds"""
    provider: str
    campground_name: str  # Search query for campground name
    start_date: str
    end_date: str
    nights: Optional[int] = None
    search_mode: str = "exact"  # "exact" or "range"


class MultiCampgroundAvailabilityResponse(BaseModel):
    """Response with results from multiple campgrounds"""
    provider: str
    search_query: str
    search_mode: str
    results: List[AvailabilityResponse]
    total_campgrounds_searched: int
    campgrounds_with_availability: int


class ProviderInfo(BaseModel):
    """Provider information"""
    name: str
    display_name: str
    supported_by_camply: bool
    description: Optional[str] = None
