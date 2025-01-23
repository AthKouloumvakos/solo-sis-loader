"""
A place for the more generic tests that do not fit in the other categories

Note
----
Before you start the test the SolO-SIS-Loader pkg should be in the python path
export PYTHONPATH="${PYTHONPATH}:{top_level_dir_that_solo-sis-loader_lives}/solo_sis_loader"
"""

import os
import pkgutil

import numpy as np
import sunpy.net.attrs as a
import xarray as xr

from solo_sis_loader import SIS


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


def test_class_propetries():
    sis = SIS(telescope='B')

    assert sis.Detector.value == 'SIS'
    assert sis.Telescope == 'B'
    assert sis.quantity == 'RATES-MEDIUM'


def test_search():
    """
    This tests if any files returned for a random search.
    """

    response_A = SIS(telescope='A').search(
        a.Time('2022-09-04', '2022-09-04'),
        level=a.Level('L2'))

    response_B = SIS(telescope='B').search(
        a.Time('2022-09-04', '2022-09-04'),
        level=a.Level('L2'))

    assert response_A.file_num == 1
    assert response_B.file_num == 1


def test_fetch():
    """
    This tests if any files downloaded.
    """

    sis_A = SIS(telescope='A')
    response_A = sis_A.search(
        a.Time('2022-09-04', '2022-09-04'),
        level=a.Level('L2'))
    files_A = sis_A.fetch(response_A)

    sis_B = SIS(telescope='B')
    response_B = sis_B.search(
        a.Time('2022-09-04', '2022-09-04'),
        level=a.Level('L2'))
    files_B = sis_B.fetch(response_B)

    assert os.path.basename(files_A[0]) == 'solo_L2_epd-sis-a-rates-medium_20220904_V01.cdf'
    assert os.path.basename(files_B[0]) == 'solo_L2_epd-sis-b-rates-medium_20220904_V01.cdf'


def test_load():
    """
    This tests if any files downloaded.
    """

    sis = SIS()
    response = sis.search(
        a.Time('2022-09-04', '2022-09-04'),
        level=a.Level('L2'))

    files = sis.fetch(response)
    sis.load(files)

    assert set(sis.dataset.keys()) == {'C', 'Ca', 'Fe', 'H', 'He3', 'He4', 'Mg', 'N', 'Ne', 'O', 'S', 'Si'}

    for key in sis.dataset.keys():
        assert isinstance(sis.dataset[key], xr.Dataset), f"Value for key '{key}' is not an xarray.Dataset."


def test_xarray_time_values():
    """
    This tests if the times are consistent.
    """

    sis = SIS()
    response = sis.search(
        a.Time('2022-09-04', '2022-09-04'),
        level=a.Level('L2'))

    files = sis.fetch(response)
    sis.load(files)

    times = ['2022-09-04T00:00:28.000000000',
             '2022-09-04T00:25:28.000000000',
             '2022-09-04T00:50:28.000000000',
             '2022-09-04T23:59:58.000000000']
    for i, t in zip([0, 50, 100, -1], times):
        assert sis.dataset['H'].time.values[i] == np.datetime64(t)
