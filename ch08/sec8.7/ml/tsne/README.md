
## t-SNE

The system provided consists of two distinct but interconnected files `tsne.py`and `visual.py` that work together
to transform high-dimensional data into interpretable visualisations. The first file implements the core t-SNE
algorithm along with synthetic data generation capabilities, while the second file handles visualisation and
optional clustering of the resulting embeddings.


### The t-SNE Core

The t-SNE implementation file serves as the computational engine of the entire system. It begins with data generation
functions that create synthetic high-dimensional datasets with known cluster structures. The `generate_realistic_data`
and `generate_mixed_density_clusters` functions produce various types of cluster formations including dense spherical
clusters, elongated structures, ring-shaped patterns, and scattered outliers. These functions assign ground-truth
labels to each data point, creating a reference for later evaluation.

The data normalisation component ensures numerical stability by standardising input features to have zero mean and unit
variance. This preprocessing step proves critical for the t-SNE algorithm's performance, as it prevents features with
larger scales from dominating the similarity calculations.

The heart of the file lies in the `TSNE` class and its `fit_transform` method. This implementation computes pairwise
affinities in the high-dimensional space using Gaussian distributions parameterised by a target perplexity value. The
algorithm then initialises a random low-dimensional embedding and iteratively optimises it through gradient descent.
The optimisation process minimises the Kullback-Leibler divergence between the high-dimensional affinity distribution
and a Student-t distribution in the low-dimensional space.

Several optimisation techniques enhance the algorithm's performance. Early exaggeration amplifies the high-dimensional
affinities during initial iterations, helping to separate clusters more effectively. Adaptive gains and momentum terms
accelerate convergence while maintaining stability. The implementation includes numerical safeguards such as the
log-sum-exp trick and bounded beta values to prevent computational overflow and underflow.

The file concludes by saving the 2D embedding coordinates alongside the original synthetic labels to a TSV file named
`tsne_output.tsv`. This output serves as the bridge between the dimensionality reduction phase and the visualisation
phase.


### The Visualisation

The visualisation operates on the output from the t-SNE core file, reading the 2D coordinates and original labels
from the TSV format. The `load_data_from_file` function parses this input and prepares it for further processing.

When automatic clustering is enabled, the file implements a complete K-means clustering algorithm through the `KMeans`
class. This implementation uses k-means++ initialisation to select well-distributed initial centroids, then iterates
between assignment and update steps until convergence or a maximum iteration limit. (The algorithm includes debugging
output to track cluster assignments and convergence behavior.)

The `estimate_clusters` function implements the elbow method to determine the optimal number of clusters. It computes
the within-cluster sum of squares (WCSS) for different values of k and identifies the point where additional clusters
provide diminishing returns in terms of variance reduction.

The `TSNEVisualizer` class handles the creation of visual scatter plots. It normalises the 2D coordinates to fit within
the plot boundaries and generates distinct colors for different clusters using various color schemes. The visualiser
can create plots using either the original labels from the synthetic data generation or the newly computed K-means
cluster assignments.

The rendering process involves drawing individual points, adding grid lines for reference, creating axes with appropriate
labels, and generating a legend that maps colors to cluster identities. The final visualisation is saved as a PNG file,
with different filenames distinguishing between original label plots and auto-clustered plots.


### Computational Workload Analysis

The computational effort between the two Python code files shows a stark imbalance heavily favoring the t-SNE core
file. The dimensionality reduction process requires calculating pairwise distances and affinities for all data points,
resulting in quadratic complexity with respect to the number of data points. Each optimisation iteration involves
computing gradients for all points in both high-dimensional and low-dimensional spaces, and the default 1000 iterations
multiply this computational burden significantly.

The visualisation file, in contrast, performs relatively lightweight operations. Loading and parsing the TSV file scales
linearly with the number of data points. K-means clustering, while involving iterative computation, operates in the
reduced 2D space and typically converges quickly. Even the elbow method, which runs K-means multiple times for different
cluster counts, remains computationally modest compared to the t-SNE algorithm. The visualisation rendering itself
involves linear-time operations for drawing points and creating plot elements.


### The Clustering Question

The question of where clustering actually occurs reveals an important distinction between implicit and explicit clustering
mechanisms. The t-SNE algorithm does not perform clustering in the traditional sense of assigning discrete labels to data
points. Instead, it creates a spatial arrangement in the low-dimensional space where points that were similar in the
high-dimensional space are positioned close together. This spatial arrangement often reveals cluster structures visually,
but no algorithmic clustering decision is made during the t-SNE process.

The labels that appear in the t-SNE output file originate from the synthetic data generation functions, not from any
clustering analysis of the t-SNE results. These labels represent the ground-truth cluster assignments used to create
the test data and are passed through the t-SNE process unchanged for later reference.

Explicit clustering occurs exclusively in the visualisation file when the K-means algorithm is applied to the 2D embedding.
This represents the only point in the entire system where new cluster assignments are algorithmically determined based on
the data's spatial distribution. The K-means clustering operates on the coordinates produced by t-SNE, attempting to identify
discrete groups based on proximity in the embedding space.


### Conceptual Framework

At its most abstract level, the system implements a two-stage process for making high-dimensional data structure interpretable
to human observers. The first stage, dimensional reduction through t-SNE, acts as a translation mechanism that preserves local
neighborhood relationships while making global structure visible in a 2D plane. This translation is not lossless, but it
prioritises maintaining the relative similarities that existed in the original high-dimensional space.

The second stage, visualisation and optional clustering, serves as an interpretation layer that either accepts predefined
structure labels or attempts to discover new structure in the reduced space. This stage transforms the numerical coordinates
into visual representations that human observers can process and understand.

The relationship between these stages reflects a fundamental principle in data analysis: structure that exists in high-dimensional
space may not be immediately apparent to human observers, but appropriate mathematical transformations can reveal this structure
in forms that match human perceptual capabilities. The t-SNE algorithm specialises in this transformation, while the visualisation
stage specialises in making the transformed data accessible to human interpretation.


### Theoretical Implications

The separation of concerns between dimensional reduction and clustering reflects deeper theoretical considerations about data
structure and its representation. The t-SNE algorithm operates under the assumption that local neighborhoods in high-dimensional
space carry the most important structural information about the data. By preserving these local relationships while allowing global
structure to emerge naturally, t-SNE avoids imposing predetermined assumptions about cluster shapes or sizes.

The optional K-means clustering in the visualisation stage represents a different theoretical approach that assumes cluster structure
can be adequately captured by proximity to centroids in the embedding space. This assumption may or may not align with the actual
structure revealed by the t-SNE embedding, leading to potential discrepancies between the visual clustering apparent in the embedding
and the algorithmic clustering results.

The system's design allows for comparison between ground-truth labels (from synthetic data generation), visual clustering (apparent
in the t-SNE embedding), and algorithmic clustering (from K-means). This comparison capability provides insights into how well the
dimensional reduction preserves cluster structure and how effectively different clustering approaches can recover known structure.


### Synthesis and Implications

The analysis reveals that the apparent simplicity of creating a clustered visualisation from high-dimensional data masks
considerable computational and theoretical complexity. The bulk of the computational effort focuses on the dimensional
reduction phase, which must solve the complex optimisation problem of preserving high-dimensional relationships in a
low-dimensional space. The clustering and visualisation phases, while conceptually important, represent relatively minor
computational overhead.

The system's architecture demonstrates the value of separating dimensional reduction from clustering analysis. This
separation allows the t-SNE embedding to reveal structure without being constrained by particular clustering assumptions,
while still enabling subsequent clustering analysis when desired. The approach provides flexibility for different analytical
goals while maintaining computational efficiency through the division of responsibilities between the two processing stages.

