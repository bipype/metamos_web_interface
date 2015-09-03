"""
Provides widgets to be used as replacements for Django's Select and
SelectMultiple widgets, implemented with use of BootstrapTable.

This version was written for Django 1.4.*.
"""


from django.forms.widgets import Widget
from django.utils.safestring import mark_safe
from bootstrap_tables import BootstrapTable


def is_iterable(item):
    """
    Check whether an item is iterable.
    """
    from collections import Iterable
    return isinstance(item, Iterable)


class BootstrapTableWidget(BootstrapTable, Widget):
    """
    Base widget class implementing Select widget with use of BootstrapTable.
    After defining first column with radio or checkbox it may be passed
    as another widget to ChoiceField for example, with code like:

    new_widget = BootstrapTableWidget('sample')
    new_widget.columns.add(field='state', radio=True)
    new_widget.columns.add(field='first_column', name='First column')
    my_field = ChoiceField(choices=enumerate(my_list), widget=new_widget)
    """

    def __init__(self, id_field, attrs=None, choices=()):
        """
        Initializes parent classes BootstrapTable and Widget and sets some
        variables to allow imitating Select widget with use of BootstrapTable.

        Args:

        id_field: name of field, from which value will be send to server,
        when submitting your form.

        attrs: standard Django's attributes, to pass into Widget initializer.

        choices: iterable with options available to choose (rows' contents).
        """
        BootstrapTable.__init__(self)
        Widget.__init__(self, attrs)
        self._choices = None
        self.choices = list(choices)
        self.set(clickToSelect=True)
        self.set(idField=id_field)

    @property
    def choices(self):
        return self._choices

    @choices.setter
    def choices(self, options):
        """
        Resets data representing available options (rows), when setting choices
        field of BootstrapTableWidget. Use of this 'hack' is needed,
        because Django's 'Select' Widget doesn't touch this field - it is
        set by other classes like ChoiceField, by overwriting this field.
        """
        self.data.clean()
        for items in options:
            fields = [x.all().get('field', '') for x in self.columns.all()]
            kwargs = dict(zip(fields, [''] + list(items)))
            self.data.add(**kwargs)
        self._choices = options

    def render(self, name, value, attrs=None, choices=()):
        """
        Renders HTML to be shown inside form when called from *Field class
        """
        self.set(selectItemName=name)
        output = self.as_html(additional_attributes=attrs, auto_load=True)

        if value:
            if is_iterable(value) and not isinstance(value, str):
                values = value
            else:
                values = [value]

            output += self.js_select_by_values(attrs['id'], values)

        return mark_safe(output)

    def js_select_by_values(self, my_id, values):
        """
        Returns HTML code with JavaScript which activates (radios or checkboxes)
        of rows with values from 'values' list. Only values from column set
        during initialization as 'id_field'
        (the field which will be passed with form to server after submitting)
        will be tested against elements from 'values' list.

        values: variable of any type
        """
        values = ', '.join([repr(value) for value in values])

        return """
        <script>
        $(document).ready(
            function()
            {{
                $('#{id}').bootstrapTable('checkBy',
                    {{
                        field: '{field}',
                        values: [{values}]
                    }})
            }}
        )
        </script>
        """.format(field=self.get('idField'), values=values, id=my_id)


class BootstrapTableSelect(BootstrapTableWidget):
    """
    Extends BootstrapTableWidget class, to imitate Select widget (single choice
    available only - it uses input of radio type)
    """
    def __init__(self, id_field, attrs=None, choices=()):
        BootstrapTableWidget.__init__(self, id_field, attrs, choices)
        self.columns.add(field='state', radio=True)


class BootstrapTableSelectMultiple(BootstrapTableWidget):
    """
    Extends BootstrapTableWidget class, to imitate SelectMultiple widget
    (with multiple choice available - it uses input of checkbox type)
    """
    def __init__(self, id_field, attrs=None, choices=()):
        BootstrapTableWidget.__init__(self, id_field, attrs, choices)
        self.columns.add(field='state', checkbox=True)
