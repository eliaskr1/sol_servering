import pandas as pd
from pvlib import location
import math

lat, lon = 59.18, 18.04
alt = 26
tz = 'Europe/Stockholm'
observer = location.Location(latitude=lat, longitude=lon, altitude=alt, tz=tz)

times = pd.date_range('2025-04-01 00:00', '2025-04-01 23:55', freq='5min', tz=tz)
solpos = observer.get_solarposition(times)

buildings = [
    {"name": "Bldg A", "distance": 45.86, "bearing": 120.86, "height": 52},
    {"name": "Bldg B", "distance": 18.12, "bearing": 176.29, "height": 48},
    {"name": "Bldg C", "distance": 31.34, "bearing": 112.9, "height": 47},
    {"name": "Bldg D", "distance": 7.72, "bearing": 88.47, "height": 42}
]

shadow_mask = pd.Series(False, index=solpos.index)

azimuth_margin = 5

for b in buildings:
    height_diff = b["height"] - alt
    min_elev = math.degrees(math.atan2(height_diff, b["distance"]))
    
    # Blocked if sun is behind building direction AND too low
    shadowed = (
        (solpos['elevation'] < min_elev) &
        (abs(solpos['azimuth'] - b["bearing"]) < azimuth_margin)
    )
    
    shadow_mask |= shadowed  # Combine with OR: any building blocks = shadow

# Times when location is in sun
in_sun = (~shadow_mask) & (solpos['elevation'] > 4)

sun_times = solpos[in_sun].index
if sun_times.empty:
    print("No sunlight at this location on this day.")
else:
    diffs = sun_times.to_series().diff() != pd.Timedelta('5min')
    groups = diffs.cumsum()
    intervals = sun_times.to_series().groupby(groups).agg(['first', 'last'])
    print("Sunlit intervals at the location (not blocked by any building):")
    print(intervals)
