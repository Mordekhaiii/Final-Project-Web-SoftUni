from django import template

register = template.Library()

@register.filter(name='rupiah')
def rupiah(value):
    try:
        # Format the value to have the "Rp" prefix and thousands separators
        return "Rp {:,}".format(value).replace(",", ".")
    except (ValueError, TypeError):
        return value
