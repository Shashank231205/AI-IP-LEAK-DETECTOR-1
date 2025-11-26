def compute_match(bom, buyer_df):
    matches = 0
    for _, bom_row in bom.iterrows():
        found = buyer_df[
            (buyer_df['Description'] == bom_row['Product Description']) &
            (buyer_df['Origin Country'] == bom_row['Origin Country'])
        ]
        if not found.empty:
            matches += 1
    return matches / len(bom) if len(bom) > 0 else 0
