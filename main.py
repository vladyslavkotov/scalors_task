import pandas as pd

df = pd.read_excel("Test.xlsx")  # For .xlsx files

df.columns = df.columns.str.strip()
df.columns = df.columns.str.replace(" ", "_")

df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0])
grouped = df.groupby(df.columns[0])

dates = list(grouped.groups.keys())
print(dates)

first_group_key = next(iter(grouped.groups))  # Get the first group key
first_group_df = grouped.get_group(first_group_key)  # Get the first group's DataFrame

initial_portfolio = first_group_df.set_index('P_Ticker')['Close_Quantity'].to_dict()
print(initial_portfolio)


for group_key in list(grouped.groups)[1:]:
    group_df = grouped.get_group(group_key)
    print(group_df.set_index('P_Ticker')['Close_Quantity'].to_dict())

# for group, group_data in grouped:
#     print(f"Group: {group}")
#     print(group_data)

# for row in df.itertuples(index=False):
#     if is_incorrect_long(row):
#         print(f"Open_Quantity: {row.Open_Quantity}, Close_Quantity: {row.Close_Quantity} Traded_Today: {row.Traded_Today} {row.Short_Pos}")
