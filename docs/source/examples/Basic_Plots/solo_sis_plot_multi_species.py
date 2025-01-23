r"""
Plot SIS Timeseries (multiple species)
--------------------------------------

In this example, we use solo_sis_loader's package to plot timeseries SIS data.
"""

# %%
# Import Required Modules

from datetime import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import sunpy.net.attrs as a

from solo_sis_loader import SIS

# %%

t_start = '2022-09-04'
t_end = '2022-09-08'
stime = a.Time(t_start, t_end)
level = a.Level('L2')

sis = SIS()
response = sis.search(stime, level=level)
files = sis.fetch(response)
sis.load(files)

# %%

energy = 0.26  # MeV/n
resample = '30min'
species_colors = {'H': 'black', 'He3': 'tab:red', 'He4': 'tab:blue', 'O': 'tab:orange', 'Si': 'magenta', 'Fe': 'seagreen'}

fig, axis = plt.subplots(figsize=(6, 4), dpi=200)

species = ['H', 'He3', 'He4', 'O', 'Si', 'Fe']

for specie in species:
    flux = sis.dataset[specie].flux.sel(energy=energy, method='nearest').resample(time=resample).mean()
    flux = flux.where(flux != 0, np.nan)

    flux.plot.line(x='time',
                   color=species_colors[specie],
                   ax=axis,
                   label=f'{specie} ({1e3*flux.energy:.2f} keV/n)')  # , **kwargs

axis.set_xlim([datetime(2022, 9, 4), datetime(2022, 9, 9)])

axis.set_yscale('log')
axis.yaxis.minorticks_on()

axis.xaxis.set_major_locator(mdates.AutoDateLocator())
axis.xaxis.set_minor_locator(mdates.HourLocator())

axis.set_xlabel('Time (UTC)')
axis.set_ylabel('Flux (#/(cm$^2$ s sr MeV/nuc))')
axis.set_title('Solar Orbiter (SIS-A)')

axis.legend(loc='upper left', bbox_to_anchor=(1, 1), fontsize=7)

fig.tight_layout()

plt.show()
