# In a file like templatetags/mentorship_tags.py
from django import template

register = template.Library()

@register.filter
def get_facilitator_name(program):
    try:
        return program.facilitator.name
    except (AttributeError, TypeError):
        return "No facilitator assigned"