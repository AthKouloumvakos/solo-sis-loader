import cdflib
import numpy as np
import pandas as pd
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
        self.dataset = {}

    def search(self, time: a.Time, level: a.Level):
        self.time = time
        self.level = level
        return Fido.search(self.Instrument & self.time & self.level & self._product)

    def fetch(self, response):
        files_downloaded = Fido.fetch(response)
        files_downloaded.sort()
        return files_downloaded

    def load(self, files, species=None, resample=None):
        if files == []:
            raise FileNotLoaded('No files provided')

        if (species is None) and hasattr(self, '_species'):
            species = self._species

        data = {}
        for file in files:
            print(f'\n Loading file: {file}')
            parameters = cdflib.CDF(str(file))
            data_ = {}
            for specie in species:
                data_[specie] = self.cdf_specie_to_dataset(parameters, specie)
                if resample:
                    data_[specie] = data_[specie].resample(time=resample).mean()

                if specie in data:
                    data[specie] = xr.concat([data[specie].isel(time=slice(0, None)), data_[specie].isel(time=slice(0, None))], 'time')
                else:
                    data[specie] = data_[specie]
                print(f'\n The following specie loaded to dataset: {specie}')
                # print(data[specie])
        self.dataset = data

        return self.dataset

    def cdf_specie_to_dataset(self, parameters, specie):
        # print(parameters.varattsget(f'{specie}_flux'))

        flux = parameters.varget(f'{specie}_flux')
        atts = parameters.varattsget(f'{specie}_flux')

        filval = atts['FILLVAL']
        flux[flux == filval] = np.nan
        flux_units = atts['UNITS']

        # Original SolO/EPD data hast timestamp at 'start' of interval. Move index time from start of time interval to its center by adding half the DELTA_EPOCH value to the index.
        dt = parameters.varget('DELTA_'+atts['DEPEND_0'])
        index = CDFepoch.to_datetime(parameters.varget(atts['DEPEND_0'])) + np.timedelta64(1, 's') * dt / 2

        if f'{specie}_Bins_Low_Energy' != atts['DEPEND_1']:
            print(f'{specie}_Bins_Low_Energy do not match the {atts["DEPEND_1"]} value')

        energy_low = parameters.varget(f'{specie}_Bins_Low_Energy')
        energy_bins_width = parameters.varget(f'{specie}_Bins_Width')
        energy_bins_text = parameters.varget(f'{specie}_Bins_Text')
        energy = energy_low + energy_bins_width/2

        data_ = xr.Dataset(
            {
                'flux': (['time', 'energy'], flux)
            },
            coords={'time': index, 'energy': energy},
            attrs={
                'instrument': getattr(self, 'Instrument', ''),
                'detector': getattr(self, 'Detector', ''),
                'telescope': getattr(self, 'Telescope', ''),
                'specie': specie,
                'axis_title': self.figure_title + f' ({specie}-Flux)',
                'axis_label_time': 'Time (UTC)',
                'axis_label_energy': 'Energy (MeV)',
                'axis_label_flux': f'Flux ({flux_units.replace("cm^2","cm$^ 2$")})',
                'units_time': 'UTC',
                'units_energy': 'MeV/n',
                'units_flux': flux_units,
                'energy_low': energy_low,  # noqa
                'energy_bin_width': energy_bins_width,  # noqa
                'energy_bin_text': energy_bins_text
                    })
        if self.level not in (a.Level('LL01'), a.Level('LL02'), a.Level('LL03')):
            uncertainty = xr.DataArray(parameters.varget(f'{specie}_Uncertainty'),
                                       coords={'time': index, 'energy': energy},
                                       name='uncertainty')

            rates = xr.DataArray(parameters.varget(f'{specie}_Rate'),
                                 coords={'time': index, 'energy': energy},
                                 name='rate')

            data_ = xr.merge([data_, uncertainty, rates])

        return data_

    def get_species_df(self, species):
        if species not in self.dataset.keys():
            raise ValueError('Selected specie does not exist in the dataset')

        df = pd.DataFrame()

        for i in self.dataset[species]['energy'].values:
            tdf = self.dataset[species].flux.sel(energy=i).to_dataframe()
            tdf.drop(columns=['energy'], inplace=True)
            tdf.rename(columns={'flux': f'{species}_flux[{i}]'}, inplace=True)
            df = pd.concat([df, tdf])

        return df

    def save_netcdf(self, filename):
        # save dataset to netcdf

        # Convert keys to a list for indexing
        species_list = list(self.dataset.keys())

        # Write the first species
        self.dataset[species_list[0]].to_netcdf(filename, engine='netcdf4', group=species_list[0])

        # Append the rest
        for specie in species_list[1:]:
            self.dataset[specie].to_netcdf(filename, engine='netcdf4', group=specie, mode='a')

        print(f'Dataset saved to file: {filename}')

    @staticmethod
    def load_netcdf(cdf_file, species):
        species_dataset = {}

        for specie in species:
            species_dataset[specie] = xr.open_dataset(cdf_file, group=specie)

        return species_dataset


class SIS(instrument):
    def __init__(self, telescope='A', quantity='RATES-MEDIUM'):
        super().__init__()

        self.Detector = a.Detector('SIS')

        self.Telescope = telescope.upper()
        self.quantity = quantity.upper()

        self.figure_title = f'{self.Instrument.value}-{self.Detector.value}-{self.Telescope}'

    @property
    def _product(self):
        if self.level in (a.Level('LL01'), a.Level('LL02'), a.Level('LL03')):
            product = a.soar.Product(f'{self.Instrument.value}-{self.Detector.value}-{self.Telescope}-{self.quantity}')
        else:
            product = a.soar.Product(f'{self.Instrument.value}-{self.Detector.value}-{self.Telescope}-{self.quantity}')

        return product

    @property
    def _species(self):
        species = ['C', 'Ca', 'Fe', 'H', 'He3', 'He4', 'Mg', 'N', 'Ne', 'O', 'S', 'Si']

        return species


class SIS_histo(instrument):
    # (stime, level):
    def __init__(self, telescope='A'):
        super().__init__()

        self.Detector = a.Detector('SIS')

        self.Telescope = telescope.upper()
        self.quantity = 'HEHIST'

        self.figure_title = f'{self.Instrument.value}-{self.Detector.value}-{self.Telescope}'

    @property
    def _product(self):
        product = a.soar.Product(f'{self.Instrument.value}-{self.Detector.value}-{self.Telescope}-{self.quantity}')

        return product

    def load(self, files):
        if files == []:
            raise FileNotLoaded('No files provided')

        data = {}
        for i, file in enumerate(files):
            print(f'\n Loading file: {file}')
            parameters = cdflib.CDF(str(file))

            # Original SolO/EPD data hast timestamp at 'start' of interval. Move index time of DataFrame df from start of time interval to its center by adding half the DELTA_EPOCH value to the index.
            dt = parameters.varget('DELTA_EPOCH')
            index = CDFepoch.to_datetime(parameters.varget('EPOCH')) + np.timedelta64(1, 's') * dt / 2

            mass_bins = parameters.varget('Mass_Bins')  # lower bound of the bin
            mass_bin_width = parameters.varget('Mass_Bins_Width')
            mass = mass_bins + mass_bin_width/2
            histo = parameters.varget('He_Histogram')

            data_ = xr.Dataset(
                    {
                        'flux': (['time', 'mass'], histo)
                    },
                    coords={'time': index, 'mass': mass},
                    attrs={
                        'instrument': getattr(self, 'Instrument', ''),
                        'detector': getattr(self, 'Detector', ''),
                        'telescope': getattr(self, 'Telescope', ''),
                        'axis_title': self.figure_title + f' Mass Histogram)',
                        'axis_label_time': 'Time (UTC)',
                        'axis_label_mass': 'Mass (amu)',
                        'axis_label_flux': f'Flux (counts)',
                        'units_time': 'UTC',
                        'units_mass': 'amu',
                        'units_flux': 'counts',
                        'mass_bins_low': mass_bins,  # noqa
                        'mass_bin_width': mass_bin_width,  # noqa
                    })

            if i == 0:
                data = data_
            else:
                data = xr.concat([data.isel(time=slice(0, None)), data_.isel(time=slice(0, None))], 'time')

        self.dataset = data

        return self.dataset
