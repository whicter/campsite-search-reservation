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

                # Remove # symbol from ID if present
                if id_part.startswith('#'):
                    id_part = id_part[1:]

                campgrounds.append({
                    'id': id_part,
                    'name': name_part,
                    'provider': self.provider_name
                })

        return campgrounds

    def get_availability(self, campground_id: str, start_date: date, end_date: date, nights: int = None) -> Dict[str, Any]:
        """
        Get availability using camply CLI

        Args:
            campground_id: Campground ID
            start_date: Check-in date (or range start for search mode)
            end_date: Check-out date (or range end for search mode)
            nights: If specified, search for consecutive night stays within date range

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
                '--end-date', end_date.strftime('%Y-%m-%d'),
                '--debug'  # Enable debug mode for detailed logs
            ]

            # Add nights and continuous flags for range search mode
            if nights is not None and nights > 0:
                cmd.extend(['--nights', str(nights)])
                cmd.append('--continuous')

            print(f"\n{'='*80}")
            print(f"🔍 Running camply command:")
            print(f"   Command: {' '.join(cmd)}")
            print(f"   Provider: {self.provider_name}")
            print(f"   Campground ID: {campground_id}")
            print(f"   Date Range: {start_date} to {end_date}")
            if nights:
                print(f"   Nights: {nights} (range search mode)")
            print(f"{'='*80}\n")

            # Use longer timeout for range searches (more API calls)
            timeout = 60 if nights else 30

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=timeout
            )

            # Print camply output
            print("📋 CAMPLY STDOUT:")
            print(result.stdout)
            if result.stderr:
                print("⚠️  CAMPLY STDERR:")
                print(result.stderr)
            print(f"{'='*80}\n")

            # Parse output to determine if sites are available
            has_availability = self._parse_availability_output(result.stdout)

            # Extract reservation URL if available
            reservation_url = self._extract_reservation_url(result.stdout)

            # Extract detailed availability info (dates and sites) for range searches
            availability_details = None
            if nights:
                availability_details = self._extract_availability_details(result.stdout)

            return {
                'available': has_availability,
                'reservation_url': reservation_url,
                'availability_details': availability_details,
                'raw_output': result.stdout
            }

        except subprocess.TimeoutExpired:
            print(f"❌ Camply command timed out")
            return {'available': False, 'error': 'timeout'}
        except subprocess.CalledProcessError as e:
            # Camply returns non-zero when no sites found
            # Check if it's "no sites found" vs actual error
            print(f"\n⚠️  Camply exited with code {e.returncode}")
            print("📋 STDOUT:")
            print(e.stdout)
            print("📋 STDERR:")
            print(e.stderr)
            print(f"{'='*80}\n")

            # Check for specific error types
            error_output = (e.stdout + e.stderr).lower()

            if 'no campsites' in error_output or 'no matching' in error_output:
                return {'available': False}

            # JSON decode errors indicate API issues
            if 'jsondecodeerror' in error_output or 'expecting value' in error_output:
                return {
                    'available': False,
                    'error': 'provider_api_error',
                    'error_message': f'{self.provider_name} API is temporarily unavailable. Please try again later.'
                }

            # Other errors
            return {
                'available': False,
                'error': 'camply_error',
                'error_message': f'Error running camply: {str(e)}'
            }

        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")
            import traceback
            traceback.print_exc()

            error_str = str(e).lower()
            if 'json' in error_str or 'decode' in error_str:
                return {
                    'available': False,
                    'error': 'provider_api_error',
                    'error_message': f'{self.provider_name} API is temporarily unavailable. Please try again later.'
                }

            return {
                'available': False,
                'error': 'unexpected_error',
                'error_message': f'Unexpected error: {str(e)}'
            }

    def _parse_availability_output(self, output: str) -> bool:
        """
        Parse camply output to check if any sites are available

        Args:
            output: Raw camply output

        Returns:
            True if any sites found, False otherwise
        """
        print(f"🔍 Parsing camply output for availability...")
        import re

        # PRIORITY 1: Check for positive indicators FIRST
        # 1. Look for "X Reservable Campsites Matching Search Preferences" (MOST RELIABLE)
        match = re.search(r'(\d+)\s+Reservable Campsites Matching', output)
        if match:
            num_sites = int(match.group(1))
            if num_sites > 0:
                print(f"   ✅ Found {num_sites} Reservable Campsites - Available!")
                return True
            else:
                print(f"   ❌ Found 0 Reservable Campsites - No availability")
                return False

        # 2. Look for date with sites count (e.g., "📅 Wed, June 03 🏕  3 sites")
        match = re.search(r'📅.*?(\d+)\s+sites?', output)
        if match:
            num_sites = int(match.group(1))
            if num_sites > 0:
                print(f"   ✅ Found date with {num_sites} sites - Available!")
                return True

        # 3. Look for reservation link (indicates availability)
        if 'reservecalifornia.com' in output.lower() or 'recreation.gov' in output.lower():
            print("   ✅ Found reservation link - Available!")
            return True

        # 4. Check for total sites in month (extract number and verify > 0)
        match = re.search(r'(\d+)\s+total sites found in month', output)
        if match:
            num_sites = int(match.group(1))
            if num_sites > 0:
                print(f"   ✅ Found {num_sites} total sites in month - Available!")
                return True

        # PRIORITY 2: Check for explicit negative indicators
        # These are only checked if no positive indicators found above
        if 'no campsites' in output.lower():
            print("   ❌ Found 'no campsites' - No availability")
            return False
        if 'no matching campsites' in output.lower():
            print("   ❌ Found 'no matching campsites' - No availability")
            return False

        # More specific check for "0 total sites found" (not just substring)
        if re.search(r'\b0\s+total sites found', output):
            print("   ❌ Found '0 total sites found' - No availability")
            return False

        print("   ❌ No availability indicators found")
        return False

    def _extract_reservation_url(self, output: str) -> str:
        """
        Extract and clean reservation URL from camply output

        Args:
            output: Raw camply output

        Returns:
            Cleaned reservation URL or None
        """
        import re

        # Look for URLs in the output
        url_pattern = r'https?://[^\s<>"\']+'
        urls = re.findall(url_pattern, output)

        for url in urls:
            # Fix ReserveCalifornia URLs
            if 'reservecalifornia.com' in url.lower():
                # Convert from: https://www.reservecalifornia.com/Web/Default.aspx#!park/685/598
                # To: https://www.reservecalifornia.com/park/685/598
                match = re.search(r'reservecalifornia\.com/Web/Default\.aspx#!(.+)', url, re.IGNORECASE)
                if match:
                    path = match.group(1)
                    cleaned_url = f"https://www.reservecalifornia.com/{path}"
                    print(f"   🔗 Found reservation URL: {cleaned_url}")
                    return cleaned_url
                else:
                    # Already in correct format or different format
                    print(f"   🔗 Found reservation URL: {url}")
                    return url

            # Other reservation systems (recreation.gov, etc.)
            elif any(domain in url.lower() for domain in ['recreation.gov', 'reserveamerica.com']):
                print(f"   🔗 Found reservation URL: {url}")
                return url

        print("   ℹ️  No reservation URL found in output")
        return None

    def _extract_availability_details(self, output: str) -> List[Dict[str, Any]]:
        """
        Extract detailed availability information from camply output

        Parses lines like:
        📅 Mon, May 11 🏕  15 sites

        And debug output with campsite info

        Args:
            output: Raw camply output

        Returns:
            List of availability details with dates and site counts
        """
        import re
        details = []

        # Pattern to match date lines: 📅 Mon, May 11 🏕  15 sites
        date_pattern = r'📅\s+([A-Za-z]+,\s+[A-Za-z]+\s+\d+)\s+🏕\s+(\d+)\s+sites?'

        matches = re.findall(date_pattern, output)

        for date_str, site_count in matches:
            details.append({
                'date': date_str,
                'site_count': int(site_count)
            })

        # Also try to extract campsite IDs from debug output
        # Pattern: 'campsite_id': 43392, 'campsite_site_name': 'Group Campsite #G002'
        campsite_pattern = r"'campsite_id':\s*(\d+).*?'campsite_site_name':\s*'([^']+)'"
        campsite_matches = re.findall(campsite_pattern, output, re.DOTALL)

        # Add unique campsites to a set to avoid duplicates
        unique_sites = {}
        for site_id, site_name in campsite_matches:
            if site_id not in unique_sites:
                unique_sites[site_id] = site_name

        # Add campsite info if found
        if unique_sites:
            campsite_info = [
                {'site_id': site_id, 'site_name': site_name}
                for site_id, site_name in unique_sites.items()
            ]
            # Only include first 20 to avoid overwhelming the UI
            if len(campsite_info) > 20:
                campsite_info = campsite_info[:20]
        else:
            campsite_info = None

        print(f"\n📊 Extracted availability details:")
        print(f"   Found {len(details)} available dates")
        if campsite_info:
            print(f"   Found {len(campsite_info)} unique campsites")

        return {
            'available_dates': details,
            'campsites': campsite_info,
            'total_dates': len(details),
            'total_unique_sites': len(unique_sites) if unique_sites else 0
        }

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
