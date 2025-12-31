from .base import BaseProvider
from .camply_provider import CamplyProvider

# Import custom providers here
# from .sanmateo_provider import SanMateoProvider

# Dynamically import all providers from camply
try:
    from camply import providers as camply_providers

    # Get all camply provider names (excluding base classes and utilities)
    CAMPLY_PROVIDER_NAMES = [
        name for name in camply_providers.__all__
        if name not in ['BaseProvider', 'ProviderType']
        and not name.startswith('RecreationDotGov')  # Exclude specialized RecDotGov variants
        or name == 'RecreationDotGov'  # But keep the main RecreationDotGov
    ]

    # Create provider registry dynamically
    PROVIDERS = {
        name: CamplyProvider(name)
        for name in CAMPLY_PROVIDER_NAMES
    }

    print(f"✅ Loaded {len(PROVIDERS)} camply providers: {', '.join(sorted(PROVIDERS.keys()))}")

except ImportError as e:
    print(f"⚠️  Warning: Could not import camply providers: {e}")
    # Fallback to manual list
    PROVIDERS = {
        'RecreationDotGov': CamplyProvider('RecreationDotGov'),
        'Yellowstone': CamplyProvider('Yellowstone'),
        'GoingToCamp': CamplyProvider('GoingToCamp'),
        'ReserveCalifornia': CamplyProvider('ReserveCalifornia'),
    }

# Add custom providers here:
# PROVIDERS['SanMateoCounty'] = SanMateoProvider()


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
