from django import template

register = template.Library()


@register.filter(name='add_class')
def add_class(field, new_class):
    old_class = field.field.widget.attrs.get('class', None)
    classes = ' '.join(filter(bool, [old_class, new_class]))
    return field.as_widget(attrs={"class": classes})
