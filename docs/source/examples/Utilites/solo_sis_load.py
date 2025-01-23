r"""
Solar Orbiter SIS data
----------------------

In this example, we use solo_sis_loader's package plot Solar Orbiter SIS data.
"""

# %%
# Import Required Modules

import sunpy.net.attrs as a

from solo_sis_loader import SIS

t_start = '2022-09-04'
t_end = '2022-09-08'
stime = a.Time(t_start, t_end)
level = a.Level('L2')

sis = SIS()
response = sis.search(stime, level=level)
files = sis.fetch(response)
sis.load(files)

# %%
