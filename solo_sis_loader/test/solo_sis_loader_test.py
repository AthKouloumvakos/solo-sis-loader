"""
A place for the more generic tests that do not fit in the other categories

Note
----
Before you start the test the SolO-SIS-Loader pkg should be in the python path
export PYTHONPATH="${PYTHONPATH}:{top_level_dir_that_solo-sis-loader_lives}/solo_sis_loader"
"""

import pkgutil


def test_import_main():
    """
    This imports SolO-SIS-Loader
    """
    no_requests = False
    try:
        pass
    except ImportError:
        no_requests = True
    assert no_requests is False


def test_imports_all():
    """
    This imports all modules in SolO-SIS-Loader
    """
    def on_error():
        try:
            raise
        except Warning:
            pass

    for imper, nm, ispkg in pkgutil.walk_packages(['solo-sis-loader'], 'solo-sis-loader.',
                                                  onerror=on_error):
        imper.find_spec(nm)
