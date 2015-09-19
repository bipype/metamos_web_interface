import os
from paths import app_paths
from openpyxl import load_workbook
from glob import glob


class NotADirectoryError(Exception):
    """
    This is an analogy to Python3 NotADirectoryError
    """
    pass


class FilesNotFoundError(Exception):
    """
    This is NOT an equivalent of Python3 FileNotFoundError - it indicates plural
    """
    pass


class MetadataManager(object):

    ID_COLUMN = 'library_id'

    def __init__(self, id_column=ID_COLUMN):
        self.id_column = id_column
        self.id_index = None
        self.headers = []
        self.rows = []

    def from_file(self, path=app_paths.metadata):

        self.headers = []
        self.rows = []

        workbook = load_workbook(filename=path, read_only=True)

        for sheet in workbook:
            sheet_rows = sheet.rows
            self.headers += [unicode(h.value) for h in next(sheet_rows)]
            self.rows += [[unicode(cell.value) for cell in row] for row in sheet_rows]

        self.update_id_index()

    def from_dict(self, dictionary):
        self.headers = dictionary['headers']
        self.rows = dictionary['rows']

        self.update_id_index()

    def update_id_index(self):
        # raises ValueError if self.ID_COLUMN is not in header
        self.id_index = self.headers.index(self.id_column)

    def column_index(self, name):
        return self.headers.index(name)

    def get_column(self, name):
        index = self.headers.index(name)
        return [row[index] for row in self.rows]

    def get_row(self, row_id):

        for row in self.rows:
            if row[self.id_index] == row_id:
                return row

        return None

    def get_rows(self, id_list):

        rows = []
        for row_id in id_list:
            row = self.get_row(row_id)
            rows.append(row)

        return rows

    def get_subset(self, id_list):

        return {'headers': self.headers,
                'rows': self.get_rows(id_list)}

    def explain_row(self, row):
        columns = zip(self.headers, row)
        return {column[0]: column[1] for column in columns}

    def explain_rows(self, rows=None):
        if not rows:
            rows = self.rows

        columns = zip(self.headers, *rows)
        return {column[0]: column[1:] for column in columns}

    def discover_paths(self):
        """
        Creates a list of paths to files mentioned in libraries dict;
        Only {library_name}*.fasta.gz files will be taken.

        Args:
            libraries - a dict where keys are names of columns and values are
                        lists of cells in corresponding columns from metadata table.

        Raises:
            FilesNotFound if no library files were found
        """
        self.headers.append('paths')

        paths = []
        count = 0
        sources = self.get_column('localization')

        for index, source in enumerate(sources):

            if not os.path.isdir(source):
                raise NotADirectoryError(source)

            name = self.get_column('library_name')[index]
            path = os.path.join(source, name)

            row = self.rows[index]

            row.append([])

            for packed_name in glob(path + '*.fastq.gz'):

                count += 1
                packed_path = os.path.join(source, packed_name)
                paths.append(packed_path)
                row[-1].append(packed_path)

        if count < 1:
            raise FilesNotFoundError('No libraries found')

        return paths

