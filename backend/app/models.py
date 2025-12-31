from pydantic import BaseModel
from typing import List, Optional
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
    nights: int
    search_days: int = 365


class AvailabilityResult(BaseModel):
    """Single availability result"""
    start_date: str  # YYYY-MM-DD format
    end_date: str    # YYYY-MM-DD format
    available: bool
    site_id: Optional[str] = None
    site_name: Optional[str] = None


class AvailabilityResponse(BaseModel):
    """Response containing all available date ranges"""
    campground_id: str
    campground_name: str
    provider: str
    nights: int
    results: List[AvailabilityResult]
    total_available: int


class ProviderInfo(BaseModel):
    """Provider information"""
    name: str
    display_name: str
    supported_by_camply: bool
    description: Optional[str] = None
