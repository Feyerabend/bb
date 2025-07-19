
> [!IMPORTANT]  
> Requires recommended virtual environment and torch.
> Installment of MNIST data is done through the script.

## Test-Time Adaptation (TTA)

At its core, TTA directly addresses the pervasive problem of *distribution shift*. Machine learning
models are typically trained under the i.i.d. (independent and identically distributed) assumption,
meaning training and test data are drawn from the same underlying distribution. However, in real-world
deployments, this assumption frequently breaks down. Causes of distribution shift include:

* *Natural variations:* Changes in lighting, weather, sensor noise, or camera angles.
* *Domain differences:* A model trained on synthetic data deployed in a real environment.
* *Temporal shifts:* Data characteristics evolving over time (e.g., trends in user behaviour,
  changes in object appearance).
* *Adversarial attacks:* Intentional manipulation of input data.

When such shifts occur, the model's performance can degrade significantly, even if it performed exceptionally
well on the original training distribution. TTA offers a pragmatic solution to mitigate this degradation
without the prohibitive cost and delay of full model retraining.


### Diving Deeper into "Core Idea"

You mentioned "parts of the model (often normalisation layers or small modules) to update or
reconfigure on the fly." This is a crucial point. TTA strategies aim for *minimal changes* to
the pre-trained model. The goal is to leverage the vast knowledge already encoded in the trained
weights while making localised adjustments for the new data.

This minimal change philosophy leads to several advantages:

* *Efficiency:* Adapting a small part of the model is orders of magnitude faster and more
  computationally inexpensive than retraining the entire network.
* *Catastrophic Forgetting Avoidance:* Full retraining on new data might lead to "catastrophic
  forgetting," where the model forgets what it learned about the original domain. TTA, by making
  small, targeted updates, aims to preserve the original knowledge.
* *Feasibility in Resource-Constrained Environments:* Edge devices, embedded systems, and real-time
  applications often lack the computational resources for frequent full retraining. TTA makes
  adaptation viable in these scenarios.


### Common Contexts: Nuances and Connections

* *Test-Time Training (TTT):* This is a specific subset of TTA. The emphasis here is on leveraging
  *self-supervision* at test time. This means creating auxiliary tasks (e.g., predicting rotations,
  solving jigsaw puzzles, or ensuring consistency of predictions under augmentations) for which
  labels can be generated from the test input itself. The model then fine-tunes on these self-supervised
  losses. The "no labels" constraint is key, as obtaining labels at test time is often impossible
  or delayed.

* *Test-Time Adaptation (TTA) (Broader Category):* This umbrella term includes TTT but also encompasses
  simpler, non-optimisation-based methods. 
  Statistical adaptations might involve re-calculating statistics for other types of normalisation
  layers or even adjusting thresholds for classification. Architectural adaptations could involve
  adding small, learnable "adapter" modules that are optimised at test time, while the bulk of the
  pre-trained network remains frozen.

* *Online / Continual Settings:* TTA fits seamlessly into these paradigms. In online learning, data
  arrives sequentially, and the model must adapt incrementally. In continual learning, the model
  needs to learn new tasks or domains without forgetting previous ones. TTA can be a critical
  component, allowing for continuous refinement as new data streams in. The distinction often lies
  in the frequency and scope of adaptation: TTA is often batch- or sample-based, while continual
  learning might involve more sustained adaptation over longer periods and multiple tasks.


### Why It Matters: Expanding on Impact

Beyond the points you listed, TTA's importance stems from its potential to bridge the gap between
theoretical model performance and real-world utility:

* *Increased Robustness and Reliability:* TTA makes models more resilient to unforeseen changes
  in their operating environment, leading to more dependable AI systems.

* *Reduced Operational Costs:* By minimising the need for constant data collection, labelling,
  and full retraining cycles, TTA significantly lowers the operational expenditure of deploying
  and maintaining ML models.

* *Faster Deployment and Iteration:* Models can be deployed more quickly, and adaptations can
  be made on the fly, accelerating the development and improvement cycles.

* *Enabling AI in Challenging Domains:* TTA opens up possibilities for deploying AI in domains
  where distribution shifts are frequent and unpredictable (e.g., environmental monitoring,
  predictive maintenance in highly variable industrial settings).


### Example: BatchNorm TTA

During training, BN layers compute running means and variances of activations across batches
and use these to normalise the data, which helps in stabilising training. These running
statistics are then typically frozen and used at inference time.

The TTA approach for BN is simple yet powerful:

1. *Original State:* At test time, the model normally uses the accumulated mean ($\mu_{train}$)
   and variance ($\sigma^2_{train}$) learned during training.

2. *Distribution Shift:* If the test data distribution is different, these $\mu_{train}$ and
   $\sigma^2_{train}$ might no longer be representative. Applying them to the shifted data
   can lead to incorrect normalisation and degraded performance.

3. *TTA Action:* Instead of using the stale training statistics, for each incoming test batch,
   the BN layers *recompute* the mean ($\mu_{test\_batch}$) and variance ($\sigma^2_{test\_batch}$)
   *on that specific test batch*. These new statistics are then used to normalise the activations
   for that batch.

4. *Benefits:* This dynamic re-normalisation effectively "centres" and "scales" the activations
   of the test data according to its *current* distribution, making the model less sensitive
   to domain shifts. The core weights of the convolutional or fully connected layers remain
   untouched, preserving the learned features.


### Advanced TTA Concepts and Techniques

While BN adaptation is simple, research has explored more sophisticated TTA methods:

* *Entropy Minimisation (Tent):* Tent (Wang et al.) proposes minimising the prediction entropy
  of the model on the test data. The idea is that for a confident model, the predictions should
  be sharp (low entropy). By backpropagating this entropy loss and updating, for example, the
  BN affine parameters ($\gamma$ and $\beta$), the model can adapt to produce more confident
  predictions on the new domain. This is an unsupervised loss, as it doesn't require labels.

* *Contrastive Learning for TTA:* Some methods leverage contrastive learning principles, where
  the model learns to group similar samples together and separate dissimilar ones. At test time,
  these methods might use the current batch to refine the embedding space, ensuring that similar
  samples from the new domain are still clustered effectively.

* *Meta-Learning for TTA:* Meta-learning (or "learning to learn") approaches can train a model
  to *adapt quickly* to new domains with minimal data. This involves training the model on a
  variety of source domains such that it learns a good initialisation or a good adaptation
  strategy that can be quickly fine-tuned at test time on an unseen target domain.

* *Feature-Space Alignment:* Some TTA methods focus on aligning the feature distributions of
  the test data with those of the training data in a learned feature space. This can involve
  using techniques like Maximum Mean Discrepancy (MMD) or adversarial training to reduce the
  discrepancy between feature distributions.

* *Gradient-Based Optimisation:* Many TTA methods involve performing a few gradient descent
  steps on the test data. The challenge is defining an appropriate unsupervised loss function
  that guides this optimisation effectively without access to labels.


### Challenges and Limitations

Despite its promise, TTA is not without its challenges:

* *No Labels for Supervision:* The primary limitation is the absence of ground truth labels at
  test time, forcing reliance on unsupervised or self-supervised losses, which might not always
  perfectly align with classification accuracy.

* *Batch Size Dependency (for BN):* For BN-based TTA, small batch sizes can lead to noisy
  statistics, potentially degrading performance rather than improving it.

* *Catastrophic Forgetting (even with TTA):* While less severe than full retraining, repeated
  or prolonged TTA without re-visiting original data can still lead to some degree of forgetting
  of the original domain, especially if the distribution shift is extreme or continuous.

* *Computational Overhead:* While less than full retraining, performing gradient updates or
  re-computing statistics on every test batch still adds computational overhead compared to
  a purely static inference model. This needs to be considered for real-time applications.

* *Determining What to Adapt:* Deciding which parts of the model to adapt (e.g., only BN
  parameters, last layer, or a small adapter network) and how much to adapt (learning rate,
  number of steps) is crucial and often heuristic.

* *Risk of Mal-adaptation:* If the unsupervised loss is poorly chosen or the distribution shift
  is truly adversarial, TTA could potentially lead the model astray, causing it to adapt incorrectly
  and degrade performance.


### Future Directions

TTA is a vibrant area of research. Future directions include:

* *More Robust Unsupervised Losses:* Developing novel self-supervised or unsupervised
  loss functions that are more resilient to various types of distribution shifts and
  less prone to mat-adaptation.

* *Adaptive Adaptation Strategies:* Creating methods that can automatically determine
  the optimal adaptation strategy (what to adapt, how much) based on the characteristics
  of the incoming test data.

* *Combining TTA with Other Robustness Techniques:* Integrating TTA with adversarial
  training, domain generalisation, and uncertainty quantification to build even more
  robust and trustworthy AI systems.

* *Practical Deployment Tools:* Developing frameworks and libraries that simplify the
  implementation and deployment of TTA in real-world applications.


In summary, Test-Time Adaptation represents a pragmatic and powerful paradigm for making
machine learning models more robust and adaptable in dynamic real-world environments,
bridging the gap between controlled training conditions and the unpredictable nature of
deployed systems.



### Results from MNIST example

__Training Performance__

The training loss decreases steadily across epochs and batches:

- Epoch 0 starts with a high loss (2.4593) but drops significantly to 0.0575 by Batch 800.
- Epoch 1 shows consistently low losses (0.0834 to 0.0691), indicating the model is learning
  effectively on the clean MNIST training data.

This suggests the model is converging well during training, which is expected for a simple
dataset like MNIST with a lightweight model (fully connected layers with BatchNorm).


__Clean Test Accuracy__

Accuracy on the clean test set is 97.58%, which is excellent for MNIST with a simple model
like SimpleNet. MNIST is a relatively easy dataset, and top-performing models often achieve
99%+ accuracy, but 97.58% is very respectable for a basic architecture with only two
epochs of training.


__Noisy Test Accuracy (Before TTA)__

Accuracy on the noisy test set (before TTA) is 60.72%, a significant drop from the clean test
accuracy. This is expected, as the noise (added via torch.randn_like(x) * 0.3) introduces a
domain shift, making the task harder. The low accuracy confirms that the model struggles
with the noisy data without adaptation.


__Test-Time Adaptation (TTA)__

- TTA uses entropy minimisation to adapt the BatchNorm parameters, and the entropy loss during
  adaptation fluctuates (e.g., 0.5011 to 0.5956 to 0.3001).
- After TTA, the noisy test accuracy improves dramatically to 90.18%, an improvement of 29.46%.
  This shows that adapting the BatchNorm parameters effectively mitigates the domain shift caused by noise.

__Overall Improvement__

The jump from 60.72% to 90.18% on the noisy test set is a strong indicator that TTA is working as
intended. While the adapted accuracy doesn’t quite reach the clean test accuracy (97.58%), it’s a
significant recovery, suggesting the adaptation process is effective.

Another example of TTA in relation to a [language model](./../../tta/) (think 2025 status of LLMs).
 
