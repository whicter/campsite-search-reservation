from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import date


class BaseProvider(ABC):
    """Base class for all campsite providers"""

    @abstractmethod
    def search_campgrounds(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for campgrounds by name

        Args:
            query: Search query string

        Returns:
            List of campgrounds with id, name, and other info
        """
        pass

    @abstractmethod
    def get_availability(self, campground_id: str, start_date: date, end_date: date) -> Dict[str, Any]:
        """
        Get availability for a specific campground and date range

        Args:
            campground_id: Campground identifier
            start_date: Check-in date
            end_date: Check-out date

        Returns:
            Dictionary with availability information
        """
        pass

    @abstractmethod
    def get_display_name(self) -> str:
        """Get human-readable provider name"""
        pass

    @abstractmethod
    def is_camply_supported(self) -> bool:
        """Whether this provider uses camply or custom implementation"""
        pass
