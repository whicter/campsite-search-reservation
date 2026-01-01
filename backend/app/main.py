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
    ProviderInfo,
    MultiCampgroundAvailabilityRequest,
    MultiCampgroundAvailabilityResponse
)
from .providers import get_provider, list_providers
from .routers import auth, monitoring

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Campsite Search API",
    description="Search for available campsites across multiple providers with monitoring support",
    version="2.0.0"
)

# Configure CORS - Must be added before routers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:3005"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(monitoring.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Campsite Search API",
        "version": "2.0.0",
        "endpoints": {
            "providers": "/api/providers",
            "campgrounds": "/api/campgrounds",
            "availability": "/api/availability",
            "auth": "/auth",
            "monitoring": "/monitoring"
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
    Check availability for specific dates

    This endpoint checks if a campground is available for the specified
    date range (from start_date to end_date).

    Args:
        request: Availability search parameters (provider, campground_id, start_date, end_date)

    Returns:
        Availability status for the requested dates
    """
    try:
        provider_instance = get_provider(request.provider)

        # Parse dates
        from datetime import datetime
        start = datetime.strptime(request.start_date, '%Y-%m-%d').date()
        end = datetime.strptime(request.end_date, '%Y-%m-%d').date()

        # Validate dates
        if start >= end:
            raise HTTPException(status_code=400, detail="End date must be after start date")
        if start < date.today():
            raise HTTPException(status_code=400, detail="Start date cannot be in the past")

        # Check availability for this date range
        availability = provider_instance.get_availability(
            request.campground_id,
            start,
            end,
            nights=request.nights
        )

        # Get campground name (from first search result)
        campground_info = provider_instance.search_campgrounds(request.campground_id)
        campground_name = (
            campground_info[0]['name'] if campground_info
            else f"Campground {request.campground_id}"
        )

        is_available = availability.get('available', False)

        # Generate message
        nights = (end - start).days
        if is_available:
            message = f"Available for {nights} night(s) from {request.start_date} to {request.end_date}"
        else:
            # Check if there was an error
            if 'error_message' in availability:
                message = availability['error_message']
            else:
                message = f"Not available for {nights} night(s) from {request.start_date} to {request.end_date}"

        return AvailabilityResponse(
            campground_id=request.campground_id,
            campground_name=campground_name,
            provider=request.provider,
            start_date=request.start_date,
            end_date=request.end_date,
            available=is_available,
            message=message,
            reservation_url=availability.get('reservation_url'),
            nights=request.nights,
            availability_details=availability.get('availability_details')
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking availability: {str(e)}")


@app.post("/api/availability/search", response_model=MultiCampgroundAvailabilityResponse)
async def search_multi_campground_availability(request: MultiCampgroundAvailabilityRequest):
    """
    Search availability across all campgrounds matching a name

    This endpoint:
    1. Searches for all campgrounds matching the name query
    2. Checks availability for each campground
    3. Returns aggregated results

    Args:
        request: Multi-campground search parameters

    Returns:
        Aggregated availability results for all matching campgrounds
    """
    try:
        provider_instance = get_provider(request.provider)

        # Step 1: Search for all matching campgrounds
        campgrounds = provider_instance.search_campgrounds(request.campground_name)

        if not campgrounds:
            raise HTTPException(
                status_code=404,
                detail=f"No campgrounds found for '{request.campground_name}'"
            )

        print(f"\n🔍 Found {len(campgrounds)} campground(s) matching '{request.campground_name}':")
        for cg in campgrounds:
            print(f"   - {cg['name']} (ID: {cg['id']})")

        # Parse dates
        from datetime import datetime
        start = datetime.strptime(request.start_date, '%Y-%m-%d').date()
        end = datetime.strptime(request.end_date, '%Y-%m-%d').date()

        # Validate dates
        if start >= end:
            raise HTTPException(status_code=400, detail="End date must be after start date")
        if start < date.today():
            raise HTTPException(status_code=400, detail="Start date cannot be in the past")

        # Step 2: Check availability for each campground
        results = []
        for campground in campgrounds:
            print(f"\n🔍 Checking availability for {campground['name']} (ID: {campground['id']})...")

            availability = provider_instance.get_availability(
                campground['id'],
                start,
                end,
                nights=request.nights
            )

            is_available = availability.get('available', False)

            # Generate message based on search mode
            if request.search_mode == "range" and request.nights:
                if is_available:
                    message = f"Found available {request.nights}-night stays in range {request.start_date} to {request.end_date}"
                else:
                    if 'error_message' in availability:
                        message = availability['error_message']
                    else:
                        message = f"No {request.nights}-night stays available in range {request.start_date} to {request.end_date}"
            else:
                nights = (end - start).days
                if is_available:
                    message = f"Available for {nights} night(s) from {request.start_date} to {request.end_date}"
                else:
                    if 'error_message' in availability:
                        message = availability['error_message']
                    else:
                        message = f"Not available for {nights} night(s) from {request.start_date} to {request.end_date}"

            results.append(AvailabilityResponse(
                campground_id=campground['id'],
                campground_name=campground['name'],
                provider=request.provider,
                start_date=request.start_date,
                end_date=request.end_date,
                available=is_available,
                message=message,
                reservation_url=availability.get('reservation_url'),
                nights=request.nights,
                availability_details=availability.get('availability_details')
            ))

        # Count campgrounds with availability
        available_count = sum(1 for r in results if r.available)

        return MultiCampgroundAvailabilityResponse(
            provider=request.provider,
            search_query=request.campground_name,
            search_mode=request.search_mode,
            results=results,
            total_campgrounds_searched=len(campgrounds),
            campgrounds_with_availability=available_count
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
