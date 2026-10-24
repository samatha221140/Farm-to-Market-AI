
from crop_seasons import CROP_SEASONS

print("Crops with season information:", len(CROP_SEASONS))

for crop, seasons in CROP_SEASONS.items():
    print(f"{crop}: {', '.join(seasons)}")