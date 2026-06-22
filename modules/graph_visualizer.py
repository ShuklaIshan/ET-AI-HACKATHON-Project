import pandas as pd
import random

chemistries = ["LFP", "NMC", "NCA"]

passport = []

for i in range(1, 501):  # 500 batteries

    soh = random.randint(75, 100)

    passport.append([
        f"B{i:04}",                       # Battery ID
        random.choice(chemistries),       # Chemistry
        random.randint(60, 120),          # Carbon footprint
        f"BAT{random.randint(1,50):03}",  # Manufacturing batch
        soh,                              # Current SoH
        random.randint(100, 2000),        # Charge cycles
        random.randint(1, 8),             # Age
        random.randint(50000, 300000)     # Resale value
    ])

passport_df = pd.DataFrame(
    passport,
    columns=[
        "battery_id",
        "chemistry",
        "carbon_footprint_kgco2",
        "manufacturing_batch",
        "current_soh",
        "charge_cycles",
        "age_years",
        "estimated_resale_value"
    ]
)

passport_df.to_csv(
    "data/battery_passport.csv",
    index=False
)

print("battery_passport.csv created")