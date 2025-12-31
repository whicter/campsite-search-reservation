from .base import BaseProvider
from .camply_provider import CamplyProvider

# Import custom providers here
# from .sanmateo_provider import SanMateoProvider

# Registry of all providers
PROVIDERS = {
    'ReserveCalifornia': CamplyProvider('ReserveCalifornia'),
    'RecreationDotGov': CamplyProvider('RecreationDotGov'),
    'GoingToCamp': CamplyProvider('GoingToCamp'),
    # Add custom providers:
    # 'SanMateoCounty': SanMateoProvider(),
}


def get_provider(name: str) -> BaseProvider:
    """Get provider by name"""
    if name not in PROVIDERS:
        raise ValueError(f"Provider '{name}' not supported. Available: {list(PROVIDERS.keys())}")
    return PROVIDERS[name]


def list_providers():
    """List all available providers"""
    return [
        {
            'name': name,
            'display_name': provider.get_display_name(),
            'supported_by_camply': provider.is_camply_supported()
        }
        for name, provider in PROVIDERS.items()
    ]
