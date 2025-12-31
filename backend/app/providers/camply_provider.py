import subprocess
import json
from typing import List, Dict, Any
from datetime import date
from .base import BaseProvider


class CamplyProvider(BaseProvider):
    """Provider that uses camply CLI for supported reservation systems"""

    def __init__(self, provider_name: str):
        """
        Initialize camply provider

        Args:
            provider_name: Name of the provider in camply (e.g., 'ReserveCalifornia')
        """
        self.provider_name = provider_name

    def search_campgrounds(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for campgrounds using camply CLI

        Args:
            query: Search query string

        Returns:
            List of campgrounds
        """
        try:
            # Run camply campgrounds command
            cmd = [
                'camply',
                'campgrounds',
                '--provider', self.provider_name,
                '--search', query
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )

            # Parse the output
            # Camply outputs in a table format, we need to parse it
            campgrounds = self._parse_campgrounds_output(result.stdout)
            return campgrounds

        except subprocess.CalledProcessError as e:
            print(f"Error running camply: {e.stderr}")
            return []
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return []

    def _parse_campgrounds_output(self, output: str) -> List[Dict[str, Any]]:
        """
        Parse camply campgrounds output into structured data

        The output format is typically:
        ⛰  New Brighton SB: Northern End, CA (598)
        ⛰  New Brighton SB: Southern End, CA (597)
        """
        campgrounds = []
        lines = output.strip().split('\n')

        for line in lines:
            line = line.strip()
            if not line or 'Retrieving' in line or 'campgrounds found' in line:
                continue

            # Try to extract ID from parentheses
            if '(' in line and ')' in line:
                # Extract name and ID
                parts = line.rsplit('(', 1)
                name_part = parts[0].strip()
                id_part = parts[1].replace(')', '').strip()

                # Remove emoji if present
                if name_part.startswith('⛰'):
                    name_part = name_part[1:].strip()

                campgrounds.append({
                    'id': id_part,
                    'name': name_part,
                    'provider': self.provider_name
                })

        return campgrounds

    def get_availability(self, campground_id: str, start_date: date, end_date: date) -> Dict[str, Any]:
        """
        Get availability using camply CLI

        Args:
            campground_id: Campground ID
            start_date: Check-in date
            end_date: Check-out date

        Returns:
            Dictionary with available sites
        """
        try:
            cmd = [
                'camply',
                'campsites',
                '--provider', self.provider_name,
                '--campground', campground_id,
                '--start-date', start_date.strftime('%Y-%m-%d'),
                '--end-date', end_date.strftime('%Y-%m-%d')
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=30  # 30 second timeout
            )

            # Parse output to determine if sites are available
            has_availability = self._parse_availability_output(result.stdout)

            return {
                'available': has_availability,
                'raw_output': result.stdout
            }

        except subprocess.TimeoutExpired:
            print(f"Camply command timed out")
            return {'available': False, 'error': 'timeout'}
        except subprocess.CalledProcessError as e:
            # Camply returns non-zero when no sites found
            # Check if it's "no sites found" vs actual error
            if 'no campsites' in e.stdout.lower() or 'no matching' in e.stdout.lower():
                return {'available': False}
            print(f"Error running camply: {e.stderr}")
            return {'available': False, 'error': str(e)}
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return {'available': False, 'error': str(e)}

    def _parse_availability_output(self, output: str) -> bool:
        """
        Parse camply output to check if any sites are available

        Args:
            output: Raw camply output

        Returns:
            True if any sites found, False otherwise
        """
        # Camply shows available sites with emoji/formatting
        # If no sites, typically shows "0 total sites found" or similar
        if '0 total sites found' in output.lower():
            return False
        if 'no campsites' in output.lower():
            return False
        if 'no matching' in output.lower():
            return False

        # If output contains site information, consider it available
        # Look for common indicators like site numbers or "Site"
        if 'site' in output.lower() and ('available' in output.lower() or '✅' in output):
            return True

        # Check for campsite listings (usually contain ⛺ or campsite names)
        if '⛺' in output or 'Campsite' in output:
            return True

        return False

    def get_display_name(self) -> str:
        """Get human-readable provider name"""
        # Convert CamelCase to spaced name
        import re
        name = re.sub(r'([A-Z])', r' \1', self.provider_name).strip()
        if name == 'Recreation Dot Gov':
            return 'Recreation.gov'
        return name

    def is_camply_supported(self) -> bool:
        """This provider uses camply"""
        return True
