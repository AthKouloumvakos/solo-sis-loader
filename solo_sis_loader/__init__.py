import cdflib
import numpy as np
import sunpy.net.attrs as a
import sunpy_soar  # noqa
import xarray as xr
from cdflib.epochs import CDFepoch
from sunpy.net import Fido

from .version import version as __version__  # noqa


class FileNotLoaded(Exception):
    pass


class instrument(object):
    def __init__(self):
        self.Instrument = a.Instrument('EPD')
        self.Detector = a.Detector('')
        self.time = []
        self.level = []
        self.dataset = []

    def search(self, time: a.Time, level: a.Level):
        self.time = time
        self.level = level
        return Fido.search(self.Instrument & self.time & self.level & self._product)

    def fetch(self, response):
        files_downloaded = Fido.fetch(response)
        files_downloaded.sort()
        return files_downloaded

    def load(self, files, species=None):
        if files == []:
            raise FileNotLoaded('No files provided')

        if not species:
            species = self._species

        data = {}
        for file in files:
            print(f'\n Loading file: {file}')
            parameters = cdflib.CDF(str(file))
            # index = CDFepoch.to_datetime(parameters.varget('EPOCH'))
            data_ = {}
            for specie in species:
                data_[specie] = self.specie_todataset(parameters, specie)

                if specie in data:
                    data[specie] = xr.concat([data[specie].isel(time=slice(0, None)), data_[specie].isel(time=slice(0, None))], 'time')
                else:
                    data[specie] = data_[specie]

                print(f'\n The following specie loaded to dataset: {specie}')
                print(data[specie])

        self.dataset = data

        return self.dataset

    def specie_todataset(self, parameters, specie):
        # print(parameters.varattsget(f'{specie}_flux'))

        flux = parameters.varget(f'{specie}_flux')
        atts = parameters.varattsget(f'{specie}_flux')

        filval = atts['FILLVAL']
        flux[flux == filval] = np.nan
        flux_units = atts['UNITS']

        index = CDFepoch.to_datetime(parameters.varget(atts['DEPEND_0']))
        energy = parameters.varget(atts['DEPEND_1'])

        data_ = xr.Dataset(
            {
                'flux': (['time', 'energy'], flux)
            },
            coords={'time': index, 'energy': energy},
            attrs={'title': self.figure_title + f' ({specie}-Flux)',
                    'axis_labels': {'time': 'Time (UTC)', 'energy': 'Energy (MeV)',
                                    'flux': f'Flux ({flux_units})'},  # noqa
                    'units': {'time': 'UTC', 'energy': 'MeV', 'flux': flux_units}  # noqa
                    })
        if self.level not in (a.Level('LL01'), a.Level('LL02'), a.Level('LL03')):
            uncertainty = xr.DataArray(parameters.varget(f'{specie}_Uncertainty'),
                                       coords={'time': index, 'energy': energy},
                                       name='uncertainty')
            if self.Detector == a.Detector('STEP'):
                rates = xr.DataArray(np.nan * parameters.varget(f'{specie}_Uncertainty'),
                                     coords={'time': index, 'energy': energy},
                                     name='rate')
            else:
                rates = xr.DataArray(parameters.varget(f'{specie}_Rate'),
                                     coords={'time': index, 'energy': energy},
                                     name='rate')
            data_ = xr.merge([data_, uncertainty, rates])

        return data_


class SIS(instrument):
    def __init__(self, telescope='A', quantity='RATES', cadence='MEDIUM'):
        super().__init__()

        self.Detector = a.Detector('SIS')

        self.Telescope = telescope.upper()
        self.quantity = quantity.upper()
        self.direction = ''
        self.cadence = cadence.upper()

        self.figure_title = f'{self.Instrument.value}-{self.Detector.value}-{self.Telescope}'

    @property
    def _product(self):
        if self.level in (a.Level('LL01'), a.Level('LL02'), a.Level('LL03')):
            product = a.soar.Product(f'{self.Instrument.value}-{self.Detector.value}-{self.Telescope}-{self.quantity}')
        else:
            product = a.soar.Product(f'{self.Instrument.value}-{self.Detector.value}-{self.Telescope}-{self.quantity}-{self.cadence}')

        return product

    @property
    def _species(self):
        species = ['C', 'Ca', 'Fe', 'H', 'He3', 'He4', 'Mg', 'N', 'Ne', 'O', 'S', 'Si']

        return species
