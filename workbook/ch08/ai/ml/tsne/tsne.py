"""
t-SNE (t-Distributed Stochastic Neighbor Embedding)
Pure Python - Fixed version with improved numerical stability
"""

import math
import random
from typing import List, Tuple, Optional
import time


class TSNEConfig:
    """Configuration class for t-SNE parameters."""
    
    def __init__(
        self,
        dims: int = 2,
        perplexity: float = 30.0,
        iterations: int = 1000,
        learning_rate: float = 200.0,
        early_exaggeration: float = 12.0,
        early_exaggeration_iter: int = 250,
        min_gain: float = 0.01,
        momentum: float = 0.9,
        tolerance: float = 1e-5,
        verbose: bool = True
    ):
        self.dims = dims
        self.perplexity = perplexity
        self.iterations = iterations
        self.learning_rate = learning_rate
        self.early_exaggeration = early_exaggeration
        self.early_exaggeration_iter = early_exaggeration_iter
        self.min_gain = min_gain
        self.momentum = momentum
        self.tolerance = tolerance
        self.verbose = verbose


class TSNE:
    """
    t-SNE implementation with improved performance and features.
    
    Features:
    - Early exaggeration for better global structure
    - Adaptive gains for faster convergence
    - Progress tracking and convergence monitoring
    - Better numerical stability
    - Configurable parameters
    """
    
    def __init__(self, config: Optional[TSNEConfig] = None):
        self.config = config or TSNEConfig()
        self.cost_history = []
        
    def euclidean_squared(self, a: List[float], b: List[float]) -> float:
        """Compute squared Euclidean distance between two points."""
        return sum((x - y) ** 2 for x, y in zip(a, b))
    
    def pairwise_distances(self, X: List[List[float]]) -> List[List[float]]:
        """Compute pairwise squared distances matrix."""
        N = len(X)
        D = [[0.0] * N for _ in range(N)]
        
        for i in range(N):
            for j in range(i + 1, N):
                d = self.euclidean_squared(X[i], X[j])
                D[i][j] = d
                D[j][i] = d
                
        return D
    
    def compute_entropy_and_prob(self, distances: List[float], beta: float) -> Tuple[float, List[float]]:
        """
        Compute Shannon entropy and probabilities given distances and precision (beta).
        Improved numerical stability to prevent overflow.
        
        Returns:
            Tuple of (entropy, probabilities)
        """
        if not distances:
            return 0.0, []
        
        # Find minimum distance for numerical stability
        min_dist = min(distances)
        
        # Compute log probabilities to avoid overflow
        log_P = [-beta * (d - min_dist) for d in distances]
        
        # Find maximum log probability for log-sum-exp trick
        max_log_P = max(log_P)
        
        # Compute probabilities using log-sum-exp trick
        exp_vals = []
        for log_p in log_P:
            exp_val = log_p - max_log_P
            # Cap the exponent to prevent overflow/underflow
            if exp_val < -700:  # exp(-700) is approximately 0
                exp_vals.append(0.0)
            else:
                exp_vals.append(math.exp(exp_val))
        
        sum_exp = sum(exp_vals)
        
        if sum_exp == 0:
            # Handle numerical issues - uniform distribution
            P = [1.0 / len(distances) for _ in distances]
            H = math.log(len(distances))
        else:
            # Normalize probabilities
            P = [exp_val / sum_exp for exp_val in exp_vals]
            
            # Compute entropy: H = log(sum_P) + beta * E[distance]
            log_sum_P = max_log_P + math.log(sum_exp)
            expected_dist = sum(d * p for d, p in zip(distances, P))
            H = log_sum_P + beta * (expected_dist - min_dist)
        
        return H, P
    
    def binary_search_precision(self, distances: List[float], target_perplexity: float) -> List[float]:
        """
        Binary search to find the precision (beta) that gives the target perplexity.
        Improved bounds and convergence criteria.
        
        Returns:
            Probability distribution for the given distances
        """
        if not distances:
            return []
        
        # Initialize beta with reasonable bounds
        beta = 1.0
        beta_min, beta_max = 1e-20, 1e20  # Set reasonable bounds
        log_target = math.log(target_perplexity)
        
        # Store best result in case we don't converge perfectly
        best_P = None
        best_error = float('inf')
        
        for iteration in range(50):  # Maximum iterations
            H, P = self.compute_entropy_and_prob(distances, beta)
            error = abs(H - log_target)
            
            # Track best result
            if error < best_error:
                best_error = error
                best_P = P[:]
            
            # Check convergence
            if error < self.config.tolerance:
                return P
            
            # Update beta bounds
            if H > log_target:
                beta_min = beta
                if beta_max == 1e20:
                    beta *= 2.0
                else:
                    beta = (beta + beta_max) / 2.0
            else:
                beta_max = beta
                if beta_min == 1e-20:
                    beta /= 2.0
                else:
                    beta = (beta + beta_min) / 2.0
            
            # Prevent beta from becoming too extreme
            beta = max(min(beta, 1e15), 1e-15)
        
        # Return best result if we didn't converge perfectly
        return best_P if best_P is not None else [1.0 / len(distances) for _ in distances]
    
    def compute_affinities(self, X: List[List[float]]) -> List[List[float]]:
        """
        Compute the high-dimensional affinities P_ij.
        
        Returns:
            Symmetric probability matrix P
        """
        N = len(X)
        D = self.pairwise_distances(X)
        P = [[0.0] * N for _ in range(N)]
        
        if self.config.verbose:
            print("Computing pairwise affinities...")
        
        for i in range(N):
            # Get distances to all other points (excluding self)
            distances = [D[i][j] for j in range(N) if j != i]
            
            if not distances:  # Single point case
                continue
            
            # Find probabilities that give target perplexity
            prob_dist = self.binary_search_precision(distances, self.config.perplexity)
            
            # Fill in the probability matrix
            prob_idx = 0
            for j in range(N):
                if i != j:
                    P[i][j] = prob_dist[prob_idx] if prob_idx < len(prob_dist) else 1e-12
                    prob_idx += 1
        
        # Make P symmetric and normalize
        for i in range(N):
            for j in range(N):
                if i != j:
                    P[i][j] = (P[i][j] + P[j][i]) / (2.0 * N)
                    P[i][j] = max(P[i][j], 1e-12)  # Numerical stability
        
        return P
    
    def compute_low_dim_affinities(self, Y: List[List[float]]) -> Tuple[List[List[float]], List[List[float]]]:
        """
        Compute low-dimensional affinities Q_ij using Student-t distribution.
        
        Returns:
            Tuple of (Q matrix, numerator matrix for gradient computation)
        """
        N = len(Y)
        num = [[0.0] * N for _ in range(N)]
        Q = [[0.0] * N for _ in range(N)]
        
        # Compute numerators
        sum_num = 0.0
        for i in range(N):
            for j in range(i + 1, N):
                dist = self.euclidean_squared(Y[i], Y[j])
                num_ij = 1.0 / (1.0 + dist)
                num[i][j] = num[j][i] = num_ij
                sum_num += 2.0 * num_ij
        
        # Normalize to get Q (avoid division by zero)
        sum_num = max(sum_num, 1e-12)
        for i in range(N):
            for j in range(N):
                Q[i][j] = max(num[i][j] / sum_num, 1e-12) if i != j else 0.0
        
        return Q, num
    
    def compute_gradient(self, P: List[List[float]], Q: List[List[float]], 
                        Y: List[List[float]], num: List[List[float]]) -> List[List[float]]:
        """Compute the gradient of the cost function."""
        N = len(Y)
        dims = len(Y[0])
        dY = [[0.0] * dims for _ in range(N)]
        
        for i in range(N):
            for d in range(dims):
                grad = 0.0
                for j in range(N):
                    if i != j:
                        diff = Y[i][d] - Y[j][d]
                        grad += 4.0 * (P[i][j] - Q[i][j]) * num[i][j] * diff
                dY[i][d] = grad
        
        return dY
    
    def compute_cost(self, P: List[List[float]], Q: List[List[float]]) -> float:
        """Compute KL divergence cost."""
        cost = 0.0
        N = len(P)
        
        for i in range(N):
            for j in range(N):
                if i != j and P[i][j] > 1e-12 and Q[i][j] > 1e-12:
                    cost += P[i][j] * math.log(P[i][j] / Q[i][j])
        
        return cost
    
    def center_embedding(self, Y: List[List[float]]) -> List[List[float]]:
        """Center the embedding around the origin."""
        N = len(Y)
        dims = len(Y[0])
        
        # Compute means
        means = [sum(Y[i][d] for i in range(N)) / N for d in range(dims)]
        
        # Center the data
        for i in range(N):
            for d in range(dims):
                Y[i][d] -= means[d]
        
        return Y
    
    def fit_transform(self, X: List[List[float]]) -> List[List[float]]:
        """
        Fit t-SNE on X and return the embedding.
        
        Args:
            X: High-dimensional data points
            
        Returns:
            Low-dimensional embedding
        """
        if not X or not X[0]:
            return []
        
        if self.config.verbose:
            print(f"Running t-SNE with {len(X)} samples, {len(X[0])} dimensions")
            print(f"Target dimensions: {self.config.dims}")
            print(f"Perplexity: {self.config.perplexity}")
            print(f"Iterations: {self.config.iterations}")
            print(f"Learning rate: {self.config.learning_rate}")
        
        start_time = time.time()
        N = len(X)
        
        # Compute high-dimensional affinities
        P = self.compute_affinities(X)
        
        # Initialize low-dimensional embedding
        Y = [[random.gauss(0, 1e-4) for _ in range(self.config.dims)] for _ in range(N)]
        
        # Initialize optimization variables
        dY = [[0.0] * self.config.dims for _ in range(N)]
        iY = [[0.0] * self.config.dims for _ in range(N)]  # Momentum term
        gains = [[1.0] * self.config.dims for _ in range(N)]
        
        if self.config.verbose:
            print("\nStarting optimization...")
        
        # Main optimization loop
        for iteration in range(self.config.iterations):
            # Apply early exaggeration
            if iteration < self.config.early_exaggeration_iter:
                P_effective = [[P[i][j] * self.config.early_exaggeration for j in range(N)] for i in range(N)]
            else:
                P_effective = P
            
            # Compute low-dimensional affinities
            Q, num = self.compute_low_dim_affinities(Y)
            
            # Compute gradient
            dY = self.compute_gradient(P_effective, Q, Y, num)
            
            # Update gains (adaptive learning rates)
            for i in range(N):
                for d in range(self.config.dims):
                    # Check for sign changes in gradient
                    sign_change = (dY[i][d] > 0) != (iY[i][d] > 0)
                    gains[i][d] = (gains[i][d] + 0.2) if sign_change else (gains[i][d] * 0.8)
                    gains[i][d] = max(gains[i][d], self.config.min_gain)
            
            # Update embedding using momentum
            for i in range(N):
                for d in range(self.config.dims):
                    iY[i][d] = (self.config.momentum * iY[i][d] - 
                               self.config.learning_rate * gains[i][d] * dY[i][d])
                    Y[i][d] += iY[i][d]
            
            # Center the embedding
            Y = self.center_embedding(Y)
            
            # Track progress
            if (iteration + 1) % 50 == 0 or iteration == 0:
                cost = self.compute_cost(P_effective, Q)
                self.cost_history.append(cost)
                
                if self.config.verbose:
                    elapsed = time.time() - start_time
                    print(f"Iteration {iteration + 1:4d}: Cost = {cost:.6f}, "
                          f"Time = {elapsed:.2f}s")
        
        if self.config.verbose:
            total_time = time.time() - start_time
            print(f"\nt-SNE completed in {total_time:.2f} seconds")
        
        return Y


def normalize_data(X: List[List[float]]) -> List[List[float]]:
    """
    Normalize data to zero mean and unit variance per feature.
    
    Args:
        X: Input data matrix
        
    Returns:
        Normalized data matrix
    """
    if not X or not X[0]:
        return X
    
    n_features = len(X[0])
    n_samples = len(X)
    
    # Create a copy to avoid modifying original data
    X_normalized = [row[:] for row in X]
    
    for feature_idx in range(n_features):
        # Extract feature column
        feature_values = [X_normalized[i][feature_idx] for i in range(n_samples)]
        
        # Compute mean and standard deviation
        mean = sum(feature_values) / n_samples
        variance = sum((x - mean) ** 2 for x in feature_values) / n_samples
        std = math.sqrt(variance) if variance > 0 else 1.0
        
        # Normalize feature
        for sample_idx in range(n_samples):
            X_normalized[sample_idx][feature_idx] = (X_normalized[sample_idx][feature_idx] - mean) / std
    
    return X_normalized


def generate_sample_data(n_clusters: int = 3, samples_per_cluster: int = 50, 
                        dimensions: int = 10, noise: float = 0.5) -> Tuple[List[List[float]], List[int]]:
    """
    Generate sample clustered data for testing t-SNE.
    
    Args:
        n_clusters: Number of clusters
        samples_per_cluster: Samples per cluster
        dimensions: Number of dimensions
        noise: Noise level (standard deviation)
    
    Returns:
        Tuple of (data, labels)
    """
    data = []
    labels = []
    
    for cluster_id in range(n_clusters):
        # Random cluster center
        center = [random.gauss(0, 3) for _ in range(dimensions)]
        
        for _ in range(samples_per_cluster):
            # Generate point around cluster center
            point = [center[d] + random.gauss(0, noise) for d in range(dimensions)]
            data.append(point)
            labels.append(cluster_id)
    
    return data, labels


def save_embedding(embedding: List[List[float]], labels: List[int], filename: str = "tsne_output.tsv"):
    """
    Save t-SNE embedding to a TSV file.
    
    Args:
        embedding: 2D embedding coordinates
        labels: Cluster labels
        filename: Output filename
    """
    with open(filename, "w") as f:
        f.write("x\ty\tlabel\n")  # Header
        for point, label in zip(embedding, labels):
            f.write(f"{point[0]:.6f}\t{point[1]:.6f}\t{label}\n")
    
    print(f"Embedding saved to '{filename}'")


if __name__ == "__main__":
    # Set random seed for reproducibility
    random.seed(42)
    
    # Generate sample data
    print("Generating sample data...")
    data, labels = generate_sample_data(n_clusters=4, samples_per_cluster=40, 
                                       dimensions=20, noise=0.8)
    
    # Normalize the data
    data = normalize_data(data)
    
    # Configure t-SNE
    config = TSNEConfig(
        dims=2,
        perplexity=30.0,
        iterations=1000,
        learning_rate=200.0,
        early_exaggeration=12.0,
        verbose=True
    )
    
    # Run t-SNE
    tsne = TSNE(config)
    embedding = tsne.fit_transform(data)
    
    # Save results
    save_embedding(embedding, labels)
    
    # Print some statistics
    if tsne.cost_history:
        print(f"\nFinal cost: {tsne.cost_history[-1]:.6f}")
        if len(tsne.cost_history) > 1:
            print(f"Cost reduction: {tsne.cost_history[0] - tsne.cost_history[-1]:.6f}")

    else:
        print("No cost history available. t-SNE may not have run successfully.")
    # Print final embedding statistics
    print(f"Final embedding shape: {len(embedding)} points, {len(embedding[0])} dimensions")


