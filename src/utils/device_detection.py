"""Device detection utilities for determining client type."""

from typing import Optional


def is_mobile_device(user_agent: Optional[str]) -> bool:
    """Detect if request is from a mobile device.
    
    Args:
        user_agent: HTTP User-Agent header string
        
    Returns:
        True if mobile device, False if desktop
    """
    if not user_agent:
        return False
    
    user_agent_lower = user_agent.lower()
    
    # Mobile indicators
    mobile_indicators = [
        'mobile',
        'android',
        'iphone',
        'ipad',
        'ipod',
        'blackberry',
        'windows phone',
        'webos',
        'opera mini',
        'opera mobi',
        'kindle',
        'silk',
        'fennec',
        'maemo',
        'phone',
    ]
    
    # Check for mobile indicators
    for indicator in mobile_indicators:
        if indicator in user_agent_lower:
            return True
    
    # Check for tablet-specific indicators
    tablet_indicators = ['tablet', 'ipad']
    for indicator in tablet_indicators:
        if indicator in user_agent_lower:
            return True
    
    return False


def get_device_type(user_agent: Optional[str]) -> str:
    """Get device type string.
    
    Args:
        user_agent: HTTP User-Agent header string
        
    Returns:
        'mobile', 'tablet', or 'desktop'
    """
    if not user_agent:
        return 'desktop'
    
    user_agent_lower = user_agent.lower()
    
    # Check for tablet first (more specific)
    if 'ipad' in user_agent_lower or 'tablet' in user_agent_lower:
        return 'tablet'
    
    # Check for mobile
    if is_mobile_device(user_agent):
        return 'mobile'
    
    return 'desktop'


def should_use_gps(user_agent: Optional[str]) -> bool:
    """Determine if GPS location should be used.
    
    Mobile devices: Always use GPS (current location)
    Desktop: Use profile location or system fallback
    
    Args:
        user_agent: HTTP User-Agent header string
        
    Returns:
        True if should use GPS, False if should use profile/system location
    """
    device_type = get_device_type(user_agent)
    return device_type in ('mobile', 'tablet')
