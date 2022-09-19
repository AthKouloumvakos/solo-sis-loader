# SolO-SIS-Loader: A python data loader for Suprathermal Ion Spectrograph (SIS) instrument onboard Solar Orbiter (SolO). 

_SolO-SIS-Loader_ is a python data loader for **Suprathermal Ion Spectrograph (SIS)** instrument onboard **Solar Orbiter's (SolO)**. SIS is part of the Energetic Particle Detector (EPD) suite for the SolO spacecraft and provides observations of He to Fe for an energy range from ∼100 keV/nucleon up to several MeV/nucleon. 

## 🚀 Instrument Specifics

SIS is based on the ACE/ULEIS design which identifies particle species and energy by time-of-flight by energy technique. Particles are detected when they pass through the entrance foils and deposit their energy in the solid state detector at the back of the instrument. The very high mass resolution of m/sigma_m∼50 will allow SIS to measure particle populations with 3He/4He ratios down to <1%.

## 💾 Installation

_SolO-SIS-Loader_ requires ```python >= 3.8``` and can be installed from PyPI using ```pip```. In the terminal do the following:

```python
# install the required packages using pip
pip install SolO-SIS-Loader
```

This will install all the necessary dependencies in the active python enviroment.

_SolO-SIS-Loader_ can also be installed directly from the github repository using the latest developed version (not recomended). First, change to the directory you want to download the source code and install the package, and run 

```python
git clone https://github.com/AthKouloumvakos/SolO-SIS-Loader
cd SolO-SIS-Loader
pip install .
```

## 📙 Usage

An example of how to search and download SIS data and load them in an xarray dataset.

```python
from solo_sis_loader import SIS
import sunpy.net.attrs as a

t_start = '2022-09-04'
t_end = '2022-09-08'
stime = a.Time(t_start, t_end)
level = a.Level('LL02')

sis = SIS(stime, level=level)
sis.search()
sis.fetch()
sis.load()
```

## 📦 Useful Python packages

- [solo-epd-loader](https://github.com/jgieseler/solo-epd-loader): A python data loader for Solar Orbiter's (SolO) Energetic Particle Detector (EPD).
- [SunPy](https://sunpy.org/): The community-developed, free and open-source solar data analysis environment for Python.
- [AstroPy](https://www.astropy.org/): The Astropy Project is a community effort to develop a single core package for Astronomy in Python.

## Disclaimer

This software is provided "as is", with no guarantee. It is not an official data source, and not officially endorsed by the corresponding instrument team.

## 📜 Acknowledging or Citing _SolO-SIS-Loader_

If you use _SolO-SIS-Loader_ for scientific work or research presented in a publication, please mention it in the main text and in the methods or acknowledgements section add the following: "This research has made use of SolO-SIS-Loader, a python data loader for Suprathermal Ion Spectrograph (SIS) instrument onboard Solar Orbiter's (SolO) (Zenodo: [https://doi.org/](https://doi.org/)).". You may also acknowledge _SolO-SIS-Loader_ in posters or talks in the way you prefer. _SolO-SIS-Loader_ has a strong dependency on SunPy and AstroPy Python packages, consider citing these packages as well.