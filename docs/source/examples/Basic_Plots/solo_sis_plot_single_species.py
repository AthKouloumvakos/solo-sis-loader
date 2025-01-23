r"""
Plot SIS Timeseries (single species)
------------------------------------

In this example, we use solo_sis_loader's package plot timeseries SIS data.
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

species = 'He4'

flux = sis.dataset[species].flux.resample(time='30min').mean()

fig, axis = plt.subplots(figsize=(6, 5), dpi=200)

axis.set_prop_cycle(color=plt.cm.Dark2.colors)

for i, energy in enumerate(flux.energy.values):
    flux_ = flux.sel(energy=energy,
                     method='nearest')
    flux_ = flux_.where(flux_ != 0, np.nan)

    flux_.plot.line(x='time',
                    ax=axis,
                    label=f'{1e3*energy:.0f} keV/n')

axis.set_xlim([datetime(2022, 9, 4), datetime(2022, 9, 9)])

axis.set_yscale('log')
axis.yaxis.minorticks_on()

axis.xaxis.set_major_locator(mdates.AutoDateLocator())
axis.xaxis.set_minor_locator(mdates.HourLocator())

axis.set_xlabel('Time (UTC)')
axis.set_ylabel('Flux (#/(cm$^2$ s sr MeV/nuc))')
axis.set_title(f'Solar Orbiter (SIS-A {species})')

axis.legend(loc='upper left', bbox_to_anchor=(1, 1), fontsize=8)

fig.tight_layout()

plt.show()
