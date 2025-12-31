from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import date, timedelta
from typing import List
import os
from dotenv import load_dotenv

from .models import (
    Campground,
    AvailabilityRequest,
    AvailabilityResponse,
    AvailabilityResult,
    ProviderInfo
)
from .providers import get_provider, list_providers

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Campsite Search API",
    description="Search for available campsites across multiple providers",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Campsite Search API",
        "version": "1.0.0",
        "endpoints": {
            "providers": "/api/providers",
            "campgrounds": "/api/campgrounds",
            "availability": "/api/availability"
        }
    }


@app.get("/api/providers", response_model=List[ProviderInfo])
async def get_providers():
    """
    Get list of all supported providers

    Returns:
        List of provider information including whether they're supported by camply
    """
    providers = list_providers()
    return [
        ProviderInfo(
            name=p['name'],
            display_name=p['display_name'],
            supported_by_camply=p['supported_by_camply']
        )
        for p in providers
    ]


@app.get("/api/campgrounds", response_model=List[Campground])
async def search_campgrounds(provider: str, search: str):
    """
    Search for campgrounds by name

    Args:
        provider: Provider name (e.g., "ReserveCalifornia")
        search: Search query

    Returns:
        List of matching campgrounds
    """
    try:
        provider_instance = get_provider(provider)
        results = provider_instance.search_campgrounds(search)

        return [
            Campground(
                id=cg['id'],
                name=cg['name'],
                provider=cg['provider'],
                description=cg.get('description')
            )
            for cg in results
        ]
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching campgrounds: {str(e)}")


@app.post("/api/availability", response_model=AvailabilityResponse)
async def search_availability(request: AvailabilityRequest):
    """
    Search for available date ranges

    This endpoint scans through the next N days (default 365) and finds all
    consecutive date ranges where the campground is available for the specified
    number of nights.

    Args:
        request: Availability search parameters

    Returns:
        All available date combinations
    """
    try:
        provider_instance = get_provider(request.provider)

        # Generate all possible date ranges
        today = date.today()
        results = []

        # Scan through search_days
        for day_offset in range(request.search_days):
            start = today + timedelta(days=day_offset)
            end = start + timedelta(days=request.nights)

            # Check availability for this date range
            availability = provider_instance.get_availability(
                request.campground_id,
                start,
                end
            )

            results.append(
                AvailabilityResult(
                    start_date=start.strftime('%Y-%m-%d'),
                    end_date=end.strftime('%Y-%m-%d'),
                    available=availability.get('available', False),
                    site_id=availability.get('site_id'),
                    site_name=availability.get('site_name')
                )
            )

        # Filter to only available dates
        available_results = [r for r in results if r.available]

        # Get campground name (from first search result)
        campground_info = provider_instance.search_campgrounds(request.campground_id)
        campground_name = (
            campground_info[0]['name'] if campground_info
            else f"Campground {request.campground_id}"
        )

        return AvailabilityResponse(
            campground_id=request.campground_id,
            campground_name=campground_name,
            provider=request.provider,
            nights=request.nights,
            results=available_results,
            total_available=len(available_results)
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking availability: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
        reload=True
    )
