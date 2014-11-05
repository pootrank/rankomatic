import os.path


def _make_file_path(filename):
    file_path = os.path.realpath(__file__)
    dirname = os.path.dirname(file_path)
    return os.path.join(dirname, filename)


png_filename = _make_file_path('arnold.png')
