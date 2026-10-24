
from crop_rules import CROP_RULES

print("Number of crops:", len(CROP_RULES))
print("\nAvailable crops:")

for crop, rules in CROP_RULES.items():
    print(
        f"{crop}: water={rules['water_need']}, "
        f"soil types={rules['soil_types']}"
    )

