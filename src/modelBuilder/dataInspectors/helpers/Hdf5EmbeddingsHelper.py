import h5py
import numpy as np
import os
import logging 

def save_embeddings(embeddings: np.ndarray, 
                    path: str, 
                    params: dict = None) -> None:

    logging.getLogger().info(f"Saving embeddings path={path}")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    with h5py.File(path, "w") as f:
        # Create dataset with variable n_components
        dset = f.create_dataset(
            "embeddings",
            data=embeddings,
            chunks=True  # Better for large datasets
        )
        
        # Store metadata
        dset.attrs["n_components"] = embeddings.shape[1]
        if params:
            for key, value in params.items():
                dset.attrs[key] = str(value)  # Store as string

def load_embeddings(path: str) -> tuple[np.ndarray, dict]:
    logging.getLogger().info(f"Loading embeddings path={path}")
    try:
        with h5py.File(path, "r") as f:
            dset = f["embeddings"]
            embeddings = dset[:]
            
            # Load metadata
            metadata = {
                "n_components": dset.attrs["n_components"],
            }
            
            # Load additional parameters
            for key in dset.attrs.keys():
                if key != "n_components":
                    try:
                        metadata[key] = eval(dset.attrs[key])  # Convert from string
                    except:
                        metadata[key] = dset.attrs[key]
            
            return embeddings, metadata
            
    except FileNotFoundError:
        raise ValueError(f"File {path} not found")
    except KeyError:
        raise ValueError("Invalid HDF5 format - missing 'embeddings' dataset")