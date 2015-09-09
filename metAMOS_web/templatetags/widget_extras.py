from django import template

register = template.Library()


@register.filter(name='with_class')
def with_class(field, new_class):
    old_class = field.field.widget.attrs.get('class', None)
    classes = ' '.join(filter(bool, [old_class, new_class]))
    return field.as_widget(attrs={"class": classes})


@register.filter(name='with_css')
def with_css(field, new_css):
    styles = field.field.widget.attrs.get('style', '').split(';')
    styles.append(new_css)
    styles = ';'.join(filter(bool, styles))
    return field.as_widget(attrs={"style": styles})
