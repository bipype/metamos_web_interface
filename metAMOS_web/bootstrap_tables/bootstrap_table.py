"""
This module provides a BootstrapTable class, which enable
convenient rendering of bootstrapTables with Python.

BootstrapTable is able to generate for you:

 - full HTML table, prepared for later post process with bootstrapTable.
 - a string representing JavaScript Object Literal, containing all
   information about table that should be passed to a constructor,
   if you wish to create a table with JavaScript call.
 - out-of-box ready JavaScript call to bootstrapTable constructor,
   but only if you specified 'table_id' earlier.

As an addition, elements containing data can be exported as JSON string,
and later passed to browser with use of AJAX-like technologies.

What is JavaScript Object Literal Notation?

    It is a native notation used in JavaScript to represent objects
    as plain text, with use of different brackets and assignments.
    It's something more then JSON, which is a subset of JSOL(N).

    For example in JSON we are not allowed to pass a function name or
    declaration, but in JSOL it is possible (JSON is data-only format).

    It is defined by ECMA 262 standard (look for ObjectLiteral).

How can I pass a function declaration or variable name to JSOL?

    In this module you should encapsulate your string with desired
    content by Raw() class, so it could be later identified as the
    string, that should be left without quotes during output-string
    assembly (yes, unquoted strings are the way, how in JSOL datum is
    identified as function or variable, the same way as in Python)

Example I:

    from bootstrap_tables import BootstrapTable

    sample_list = ['Sample 1', 'Sample 2', 'Sample 3']

    table = BootstrapTable(html_id='some-id')
    table.set(search=True)
    table.columns.add(field='id', title='ID')
    table.columns.add(field='sample', title='Name', sortable=True)

    for i, sample in enumerate(sample_list):
        table.data.add(id=i, sample=sample)

    # And now you can use
    print table.as_html()
    # or:
    # print table.as_js()
    # print table.as_json()
    # print table.as_json(restrict_to='data')
    # print table.as_json(restrict_to='columns')
    # print table.get_html_data_rows()
    # print table.get_html_columns()
    # print table.as_js_with_constructor()

Example II:

    from bootstrap_tables import BootstrapTable, Raw

    js = Raw(
    "function (value) {"
        "var color='#'+Math.floor(Math.random()*6777215).toString(16);"
        "return '<div  style=\"color: ' + color + '\">' +"
                "'<i class=\"glyphicon glyphicon-usd\"></i>' +"
                "value.substring(1) +"
                "'</div>';"
        "}"
    )

    sample_list = ['Sample 1', 'Sample 2', 'Sample 3']

    table = BootstrapTable(html_id="table")
    table.set(pagination=True, search=True, showColumns=True)
    table.set(showToggle=True, clickToSelect=True)
    table.set(idField='id', selectItemName='sample')
    table.columns.add(field='state', radio=True)

    table.columns.add(field='id',
                      title="Sample ID",
                      sortable=True)

    table.columns.add(field='sample',
                      title="Sample Name",
                      sortable=True,
                      formatter=js)

    for i, sample in enumerate(sample_list):
        table.data.add(id=i, sample=sample)

    print table.as_js_with_constructor()

More advanced exemplars TBA.
"""

import copy
import json
import re


def is_container(variable):
    """
    Check if 'variable' is descendant of Container class.
    """
    return isinstance(variable, Container) or issubclass(type(variable), Container)


class Raw(str):
    """
    This class should be used to pass names of JavaScript functions,
    variables or even functions declarations to BootstrapTable.

    Using this container for string allows you to pass information,
    that this string should be treated slightly different than others
    - it should be integrated into response without quotes.
    """

    def __init__(self, string):
        str.__init__(string)


class Container(object):
    """
    Basic class for generation JSON-like, enhanced string responses.
    Except standard JSON generation it allows to handle JavaScript
    variables and function names or even functions declarations.
    """

    def __init__(self, level=0):
        """
        level:  How deeply current instance is nested in structure.
                Determines number of tabulators to use.
        """
        self.level = level
        self._data = []
        self.wrappers = ["[", "]"]
        self.indent = "\t"
        self.new_line = "\n"

    def test_wrappers(self):
        """
        Check whether both wrappers are in place.

        To use before string generation if invoked from parent, to
        ensure that our consistent formatting will be kept.
        """
        assert len(filter(bool, self.wrappers)) == 2

    def all(self):
        """
        Return all data from container
        """
        return self._data

    def _convert_to_js(self, value):
        """
        Convert variable to string representation, which meets
        JavaScript Object Literal Notation. It is based on standard
        json.dumps() function, but also preserves names of
        JavaScript variables, functions and function declarations
        without quotes if they are delivered inside Raw object.
        """

        # These lines allows you to pass JavaScript names *without
        # quotes*, so they can be properly interpreted
        if isinstance(value, Raw):
            return unicode(value)

        # In case if we need some recursion
        if is_container(value):
            value.test_wrappers()
            return unicode(value)

        # Eventually if it is some list, dict, numeral etc,
        # let it be parsed be standard json module
        return json.dumps(value)

    def _format(self, data):
        """
        Stub: Allows sub classes to modify data formatting
        """
        return self._convert_to_js(data)

    def _get_formatted_contents(self):
        """
        Returns list with formatted contents
        """
        return [self._format(data) for data in self._data]

    def __unicode__(self):
        """
        Prints pretty representation of container in JSOL notation.
        """
        contents = self._get_formatted_contents()

        indents_parent = self.indent * self.level
        indents_own = indents_parent + self.indent

        output = self.wrappers[0]

        if filter(bool, contents):

            separator = "," + self.new_line + indents_own

            output += self.new_line + indents_own
            output += separator.join(contents)
            output += self.new_line + indents_parent

        output += self.wrappers[1]

        return output

    def compressed_str(self):
        """
        Prints compressed representation of container in JSOL notation.
        """
        contents = self._get_formatted_contents()

        output = self.wrappers[0]

        if filter(bool, contents):
            output += ",".join(contents)

        output += self.wrappers[1]

        return output

    def clean(self):
        self._data = []


class Object(Container):
    """
    Represents JavaScript object; As data storage a dict is used, where:
        - keys are names of properties,
        - values are values associated with these properties
    """
    camel_regex = re.compile('([A-Z]+)')

    def __init__(self, level=0):
        Container.__init__(self, level)
        self._data = {}
        self.wrappers = ["{", "}"]

    def set(self, **kwargs):
        self._data.update(kwargs)

    def get(self, key):
        return self._data.get(key, '')

    def _format(self, key):
        """
        Formats dicts entry of given key to JavaScript representation
        (that one, which is used for object declarations).
        """
        return '"' + key + '": ' + self._convert_to_js(self._data[key])

    def decamelize(self, name):
        """
        Transforms string from form like: sortOrder to sort-order.
        """
        return self.camel_regex.sub(r'-\1', name).lower()

    def clean(self):
        self._data = {}

    def as_attributes(self):
        """
        Return contents, formatted as it is required to use them as
        HTML attributes (keys will be decamelized and prefixed with 'data-', so
        BactrianCamel will become data-bactrian-camel). Items with empty string
        values will be skipped.
        """
        item_iterator = self._data.iteritems()
        return {'data-' + self.decamelize(x): y
                for x, y in item_iterator if y != ''}  # allow False, but not ''


class List(Container):
    """
    Represents JavaScript list.
    Formatting options and storage are entirely inherited from Container.
    """

    def __init__(self, level=0):
        Container.__init__(self, level)

    def add_item(self, item):
        self._data.append(item)

    def add_object(self, **kwargs):
        obj = Object(self.level+1)
        obj.set(**kwargs)
        self._data.append(obj)

    def add_list(self, args):
        lis = List(self.level+1)
        for arg in args:
            lis.add(arg)
        self._data.append(lis)

    def add(self, *args, **kwargs):
        """
        Add an Object, List or ordinary variable (here: 'item') to List.

        It is input format specific function, so passed attributes will
        be treated initializing variables for:
            - Object if there are keyword attributes
            - List if there are multiple positioned attributes
            - ordinary variable if there is only one positioned argument

        If you want to add an empty Object, List or List containing only
        one element, please use respectively: add_object or add_list.
        """
        if kwargs:
            self.add_object(**kwargs)
        elif len(args) > 1:
            self.add_list(args)
        elif len(args):
            self.add_item(args[0])


class BootstrapTable(Object):
    """
    Allows to easily create bootstrapTable with Python and later
    export it to HTML, JavaScript or JSON (also only some parts).
    """

    js_call_template = "function(){{$('#{id}').bootstrapTable({data})}}"

    def __init__(self, html_id=None):
        """
        Creates BootstrapTable Object. If html_id specified, the HTML
        table tag will have additional attribute: id="<html_id>".
        """
        Object.__init__(self)

        self.columns = List(level=1)
        self.data = List(level=1)
        self.html_id = html_id

    def create_attribute(self, attr_tuple):
        """
        Create an attribute of name 'key', with value 'value',
        to use inside HTML tags. Raw values will be treated as
        plain text. Objects, lists, etc will be dumped to JSON.
        """
        key, value = attr_tuple

        if is_container(value):
            value = value.compressed_str()
        value = json.dumps(value)

        # avoid redundant quotes
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]

        return key + u'="' + value + u'"'

    def start_tag(self, tag, attr_dict):
        """
        Creates HTML opening tag with attributes from 'attr_dict'.
        """
        out = u'<' + tag

        attributes = map(self.create_attribute, attr_dict.iteritems())

        if attributes:
            out += u' '

        out += u' '.join(attributes) + u'>'

        return out

    def create_tag(self, tag, attr_dict, contents):
        """
        Creates HTML tag 'tag' containing 'contents',
        with attributes from 'attr_dict'.
        """
        out = self.start_tag(tag, attr_dict)
        out += contents
        out += u'</' + tag + u'>'

        return out

    def get_html_columns(self, spacer=u'\n'):
        """
        Creates HTML table cells with content corresponding to data
        gathered about columns in 'self.columns' List.
        """
        out = ''
        for item in self.columns.all():
            # TODO: if it is list, then one more loop?
            if isinstance(item, Object):
                data = copy.copy(item.as_attributes())
                title = data.pop('title', u'')
            else:
                data = {}
                title = json.dumps(item)
            out += spacer + self.create_tag(u'th', data, title)
        return out

    def get_html_data_rows(self, spacer=u'\n'):
        """
        Creates HTML table rows with content corresponding to data
        gathered about rows in 'self.rows' List.
        Only data referred by columns will be rendered.
        """
        out = u''
        for item in self.data.all():
            out += spacer + u'<tr>'

            if is_container(item):
                for column in self.columns.all():
                    field = column.all()['field']
                    raw_content = item.all().get(field, u'-')
                    if raw_content == 'None':
                        raw_content = u'-'
                    content = unicode(raw_content)

                    out += spacer + self.indent
                    out += self.create_tag(u'td', {}, content)

            out += spacer + u'</tr>'
        return out

    def as_html(self, additional_attributes=None, auto_load=False):
        """
        Return HTML table representing current Bootstrap Table instance.

        Please not, that all names of attributes from Objects will be
        decamelized and prefixed with 'data-', to follow HTML5 formatting (it
        means conversion from BactrianCamel to data-bactrian-camel notation).

        Args:

        additional_attributes: a dict with attributes to be added into <table>
        HTML tag, such as class or id. For example, to add class 'stripped',
        the dict should be: {'class': 'stripped'}. Note, that in case of
        conflict items from this dict will be preferred over instance's ones.

        auto_load: boolean value - determines, whether table should be
        immediately converted to bootstrapTable (by setting data-toggle option)
        """
        data = self.as_attributes()

        tr_spacer = self.new_line + self.indent

        if self.html_id:
            data[u'id'] = self.html_id

        if additional_attributes:
            data.update(additional_attributes)

        if auto_load:
            data[u'data-toggle'] = u'table'

        out = self.start_tag(u'table', data)

        out += tr_spacer + u'<thead>'
        out += tr_spacer + u'<tr>'
        out += self.get_html_columns(spacer=tr_spacer + self.indent)
        out += tr_spacer + u'</tr>'
        out += tr_spacer + u'</thead>'

        out += tr_spacer + u'<tbody>'
        out += self.get_html_data_rows(spacer=tr_spacer)
        out += tr_spacer + u'</tbody>'

        out += self.new_line + u'</table>'

        return out

    def as_js(self):
        """
        Returns all information about current table in form of
        JavaScript Object Literal Notation string, so it could be
        used as an argument for BootstrapTable initializer.
        """
        return self.__unicode__()

    def as_json(self, restrict_to=None):
        """
        Returns JavaScript representation of table converted from
        JavaScript Object Literal Notation to JSON string.
        """

        if restrict_to == 'columns':
            jsol = unicode(self.columns)
        elif restrict_to == 'data':
            jsol = unicode(self.data)
        else:
            jsol = self.as_js()

        return json.dumps(json.loads(jsol))

    def as_js_with_constructor(self):
        """
        Creates bootstrapTable constructor with use of table data.
        Note, that currently this function has obvious constraint in
        elements selection to picking elements only by id,
        but it will be easy to change in future.
        """
        assert self.html_id
        return self.js_call_template.format(id=self.html_id, data=self.as_js())

    def __unicode__(self):
        """
        Returns string representation, including columns and data
        """
        self.set(columns=self.columns, data=self.data)
        out = Object.__unicode__(self)
        self.set(columns='', data='')
        return out

