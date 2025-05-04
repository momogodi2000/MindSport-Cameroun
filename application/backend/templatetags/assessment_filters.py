from django import template

register = template.Library()

@register.filter
def get_range(value):
    """Convert value to integer before creating range"""
    try:
        return range(1, int(value) + 1)
    except (ValueError, TypeError):
        return range(1, 6)  # Default to 5-point scale if conversion fails
    
@register.filter
def range_to(start, end):
    """
    Creates a range from start to end (inclusive)
    """
    return range(int(start), int(end) + 1)