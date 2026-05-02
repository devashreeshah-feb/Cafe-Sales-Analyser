"""
Generate synthetic cafe sales dataset matching PRD specifications.
10,000 transactions, Jan-Dec 2023
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

np.random.seed(42)
random.seed(42)

# --- Item definitions from PRD ---
items = {
    'Coffee':    {'price_range': (2.00, 3.50), 'margin': 0.70, 'target_transactions': 1165},
    'Tea':       {'price_range': (1.50, 3.00), 'margin': 0.70, 'target_transactions': 1089},
    'Salad':     {'price_range': (4.00, 5.00), 'margin': 0.45, 'target_transactions': 1148},
    'Sandwich':  {'price_range': (3.50, 5.00), 'margin': 0.40, 'target_transactions': 1131},
    'Smoothie':  {'price_range': (3.50, 5.00), 'margin': 0.55, 'target_transactions': 1096},
    'Juice':     {'price_range': (2.50, 4.00), 'margin': 0.50, 'target_transactions': 1171},
    'Cake':      {'price_range': (2.50, 4.00), 'margin': 0.50, 'target_transactions': 1139},
    'Cookie':    {'price_range': (1.00, 2.00), 'margin': 0.60, 'target_transactions': 1092},
}

# Missing/error items: 969 records (9.7%)
TOTAL_RECORDS = 10000
MISSING_ITEM_COUNT = 969  # 9.7%
VALID_ITEM_COUNT = TOTAL_RECORDS - MISSING_ITEM_COUNT

# --- Generate dates ---
start_date = datetime(2023, 1, 1)
end_date = datetime(2023, 12, 31)
date_range = (end_date - start_date).days + 1

# 4.6% missing dates = 460 records
MISSING_DATE_COUNT = 460

dates = []
for _ in range(TOTAL_RECORDS):
    random_day = random.randint(0, date_range - 1)
    dates.append(start_date + timedelta(days=random_day))

# --- Generate items ---
item_list = []
for item_name, config in items.items():
    count = config['target_transactions']
    item_list.extend([item_name] * count)

# Pad remaining with valid items
remaining = VALID_ITEM_COUNT - len(item_list)
if remaining > 0:
    extra_items = random.choices(list(items.keys()), k=remaining)
    item_list.extend(extra_items)

# Add missing/error items
error_items = ['UNKNOWN'] * (MISSING_ITEM_COUNT // 2) + ['ERROR'] * (MISSING_ITEM_COUNT - MISSING_ITEM_COUNT // 2)
item_list.extend(error_items)
random.shuffle(item_list)
item_list = item_list[:TOTAL_RECORDS]

# --- Generate quantities and prices ---
quantities = []
prices = []
for item_name in item_list:
    qty = random.randint(1, 5)
    quantities.append(qty)
    
    if item_name in items:
        price_low, price_high = items[item_name]['price_range']
        price = round(random.uniform(price_low, price_high), 2)
    else:
        # For UNKNOWN/ERROR items, use average price
        price = round(2.949, 2)
    prices.append(price)

# --- Payment methods ---
# 31.8% missing = 3178
MISSING_PAYMENT_COUNT = 3178
payment_methods = ['Cash', 'Credit Card', 'Digital Wallet']
payment_list = random.choices(payment_methods, k=TOTAL_RECORDS - MISSING_PAYMENT_COUNT)
payment_list.extend([None] * MISSING_PAYMENT_COUNT)
random.shuffle(payment_list)

# --- Locations ---
# 39.6% missing = 3961
MISSING_LOCATION_COUNT = 3961
locations = ['In-store', 'Takeaway']
# In-store vs Takeaway: 50.5% vs 49.5% of known revenue
location_list = []
for _ in range(TOTAL_RECORDS - MISSING_LOCATION_COUNT):
    if random.random() < 0.505:
        location_list.append('In-store')
    else:
        location_list.append('Takeaway')
location_list.extend([None] * MISSING_LOCATION_COUNT)
random.shuffle(location_list)

# --- Build DataFrame ---
df = pd.DataFrame({
    'transaction_id': [f'TXN-{str(i+1).zfill(5)}' for i in range(TOTAL_RECORDS)],
    'transaction_date': dates,
    'item': item_list,
    'quantity': quantities,
    'price_per_unit': prices,
    'payment_method': payment_list,
    'location': location_list,
})

# Make 460 dates missing
missing_date_indices = random.sample(range(TOTAL_RECORDS), MISSING_DATE_COUNT)
df.loc[missing_date_indices, 'transaction_date'] = None

# Calculate total_spent
df['total_spent'] = round(df['quantity'] * df['price_per_unit'], 2)

# Format dates
df['transaction_date'] = pd.to_datetime(df['transaction_date']).dt.strftime('%Y-%m-%d')

# Reorder columns
df = df[['transaction_id', 'transaction_date', 'item', 'quantity', 'price_per_unit', 'total_spent', 'payment_method', 'location']]

# Save
output_path = os.path.join(os.path.dirname(__file__), '..', 'data')
os.makedirs(output_path, exist_ok=True)
csv_path = os.path.join(output_path, 'cafe_sales.csv')
df.to_csv(csv_path, index=False)

print(f"Dataset generated: {csv_path}")
print(f"Total records: {len(df)}")
print(f"Total revenue: £{df['total_spent'].sum():,.2f}")
print(f"Missing items: {df['item'].isin(['UNKNOWN', 'ERROR']).sum()}")
print(f"Missing dates: {df['transaction_date'].isna().sum()}")
print(f"Missing payments: {df['payment_method'].isna().sum()}")
print(f"Missing locations: {df['location'].isna().sum()}")
print(f"\nItem distribution:")
print(df['item'].value_counts())
