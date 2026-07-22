import logging
from sklearn.preprocessing import MaxAbsScaler, normalize

def normalize_data(embeddings, normaliation):
    if normaliation is not None:
        logging.getLogger().info(f"Running normalization on dataset, normalization={normaliation}")
    if normaliation in ["l1", "l2", "max"]:
        embeddings = normalize(embeddings, norm=normaliation, axis=1)
    elif normaliation == "min_max":
        from sklearn.preprocessing import MinMaxScaler
        scaler = MinMaxScaler(feature_range=(0, 1))
        embeddings = scaler.fit_transform(embeddings)
    elif normaliation == "z_score":
        from sklearn.preprocessing import StandardScaler
        s_scaler = StandardScaler()
        embeddings = s_scaler.fit_transform(embeddings)
    elif normaliation == "robust":
        from sklearn.preprocessing import RobustScaler
        r_scaler = RobustScaler()
        embeddings = r_scaler.fit_transform(embeddings)
    return embeddings