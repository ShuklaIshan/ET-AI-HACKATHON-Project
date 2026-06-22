import pandas as pd

mapping_df = pd.read_csv("data/battery_vehicle_mapping.csv")
batch_df = pd.read_csv("data/battery_batches.csv")
suppliers_df = pd.read_csv("data/suppliers.csv")


def find_affected_vehicles(batch_id):

    affected = mapping_df[
        mapping_df["batch_id"] == batch_id
    ]

    return affected["vehicle_id"].tolist()


def get_supplier(batch_id):

    row = batch_df[
        batch_df["batch_id"] == batch_id
    ].iloc[0]

    supplier_id = row["supplier_id"]

    supplier_row = suppliers_df[
        suppliers_df["supplier_id"] == supplier_id
    ].iloc[0]

    return supplier_row["supplier_name"]