import numpy as np

def create_vrp_instance():
    """Creates a simple VRP instance for demonstration."""
    locations = {
        "depot": (0, 0),
        "customer_1": (1, 3),
        "customer_2": (-2, 1),
        "customer_3": (3, -1)
    }
    # Calculate distance matrix (Euclidean distance)
    coords = np.array(list(locations.values()))
    dist_matrix = np.sqrt(np.sum((coords[:, np.newaxis, :] - coords[np.newaxis, :, :])**2, axis=-1))

    return locations, dist_matrix