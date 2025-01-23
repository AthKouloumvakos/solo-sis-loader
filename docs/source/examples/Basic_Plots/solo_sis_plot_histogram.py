r"""
Plot SIS He Mass Spectrogram
----------------------------

In this example, we use solo_sis_loader's package to plot the He mass spectrogram.
"""

# %%
# Import Required Modules

from datetime import datetime

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import sunpy.net.attrs as a
from matplotlib import colors

from solo_sis_loader import SIS_histo

# %%

t_start = '2022-11-11'
t_end = '2022-11-16'
stime = a.Time(t_start, t_end)
level = a.Level('L2')

sish = SIS_histo()
response = sish.search(stime, level=level)
files = sish.fetch(response)
sish.load(files)

# %%

fig, axis = plt.subplots(figsize=(6, 5), dpi=200)

sish.dataset.flux.plot.pcolormesh(x='time',
                                  cmap='turbo',
                                  add_colorbar=False,
                                  norm=colors.LogNorm(vmin=1, vmax=100),
                                  ax=axis)

axis.axhline(y=3.016029, linestyle='--', color='tab:red')
axis.axhline(y=4.002603, linestyle='--', color='tab:blue')

axis.set_xlim([datetime(2022, 11, 11), datetime(2022, 11, 16)])
axis.set_ylim([2, 5])

axis.set_yticklabels(axis.get_yticks(), rotation=90, va='center')

axis.set_ylabel('Mass (AMU)')
axis.set_xlabel('Time (UTC)')

axis.yaxis.minorticks_on()

axis.xaxis.set_major_locator(mdates.AutoDateLocator())
axis.xaxis.set_minor_locator(mdates.HourLocator())

plt.setp(axis.get_xticklabels(), rotation=0, ha='center')

axis.set_title('Helium mass spectrogram (SolO SIS-A, 0.5-2 MeV/nuc)')

fig.tight_layout()

plt.show()
