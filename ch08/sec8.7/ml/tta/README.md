
> [!IMPORTANT]  
> The code requires (preferably) a virtual environment and torch installations.

## Test-Time Adaptation (TTA)

Test-Time Adaptation (TTA) is a powerful technique designed to tackle the challenge of *distribution shift*
in machine learning, where the data encountered during deployment differs from the data used during training.
Typically, machine learning models rely on the assumption that training and test data are drawn from the same
underlying distribution--a principle known as the i.i.d. (independent and identically distributed) assumption.
However, real-world scenarios often disrupt this assumption. Variations such as changes in lighting, weather,
or sensor noise, differences between synthetic and real-world environments, evolving data trends over time,
or even intentional adversarial manipulations can cause a model's performance to falter. TTA provides a
practical approach to maintain model effectiveness without the need for costly and time-consuming retraining,
adapting the model dynamically during inference to align with the new data distribution.

TTA has become increasingly relevant in modern (2025) large language models and vision-language systems,
where retraining or fine-tuning on new data is often infeasible due to the massive scale of pre-training.
Instead, these models may incorporate lightweight adaptation mechanisms at inference time--such as modifying
attention weights, recalibrating normalisation layers, or using test-time prompts and feedback loops--to
better align with the characteristics of new input domains or user contexts. This enables improved robustness
and personalisation without the need for updating the core model weights.

The Python code in `lm.py` exemplifies this TTA concept through the implementation of a `CorrectionAwareTransformer`
model, which combines corruption-aware training with TTA to handle noisy or corrupted text inputs effectively.
This model is designed not only to generate coherent text but also to recognise and correct errors in real-time,
making it particularly robust for real-world applications where data imperfections are common.


### Core Mechanisms of the CorrectionAwareTransformer

At the heart of the system lies the `CorrectionAwareTransformer`, a PyTorch-based model built upon a standard
Transformer Encoder architecture. The model begins by expanding its vocabulary to include both standard words
and their corrupted variants, such as common misspellings (e.g., "teh" or "hte" for "the"). This expanded
vocabulary, derived from a predefined `corruption_patterns` dictionary, ensures that the model can process noisy
inputs without treating them as unknown tokens. Alongside this, a `correction_map` facilitates the conversion
of corrupted words back to their correct forms, streamlining the correction process.

The model employs embeddings to transform token indices into dense vectors, supplemented by learnable positional
encodings that preserve the sequence's order. The Transformer Encoder, composed of multiple layers, generates
contextualised representations of the input. Two distinct output heads enhance the model's functionality: the
`lm_head` predicts the next token in the sequence for language modelling, while the `confidence_head` produces
a probability score indicating the model's confidence in each token. This dual-head approach allows the model
to balance text generation with error detection.


### Test-Time Adaptation in Action

The TTA process is driven by a custom `TTALoss` class, which optimises the model's behaviour during inference
through three complementary objectives. First, the `entropy_loss` minimises prediction uncertainty, encouraging
the model to produce confident outputs. Second, the `confidence_loss` directly boosts the confidence scores
from the `confidence_head`, typically targeting a high confidence threshold (e.g., 0.8). Finally, the
`consistency_loss` ensures that the model's predictions remain stable across slightly altered versions of the
input, achieved by measuring the Kullback-Leibler (KL) divergence between the original and augmented inputs.
These augmented inputs are created by a function that introduces minor corruptions with a low probability,
simulating real-world noise.

The `adapt_at_test_time_enhanced` function orchestrates TTA by fine-tuning a copy of the pre-trained model on
the specific input at inference time. It supports flexible adaptation modes, allowing updates to all model
parameters, only the final layers, or just normalisation layers, depending on the use case. Using the `AdamW`
optimiser, the function iteratively applies the TTA loss, refines the model's parameters, and ensures
robustness to the specific input's characteristics.


### Text Generation and Correction

Text generation is handled by the `generate_with_correction` function, which integrates TTA for enhanced
performance. When activated, TTA fine-tunes the model on the input sequence before processing it. The function
evaluates the confidence scores of input tokens, correcting those below a specified threshold using the
`correction_map`. It then generates subsequent tokens by sampling from the `lm_head`'s predicted probabilities,
with a temperature parameter controlling the randomness of the output. This process ensures that the generated
text is both coherent and corrected for errors.

Supporting functions, such as `corrupt_word` and `correct_word`, enable controlled introduction and correction
of errors based on the `corruption_patterns` and `correction_map`. During training, the `generate_training_data`
function creates a diverse dataset with a mix of clean and corrupted sentences, assigning higher confidence
to clean words and lower confidence to corrupted ones. The `train_model` function uses this dataset, combining
a cross-entropy loss for next-token prediction with a mean squared error loss for confidence prediction, optimised
via the `AdamW` optimiser and a cosine annealing learning rate scheduler.


### Evaluating Robustness

The `test_corruption_awareness` function demonstrates the model's capabilities by comparing standard text
generation with TTA-enhanced generation across various test cases, including clean and corrupted inputs.
It highlights improvements in confidence scores and output quality when TTA is applied, showcasing the model's
ability to adapt to challenging inputs. The `main` function ties these components together, training the model
and executing the tests to validate its performance.

In summary, the `CorrectionAwareTransformer` model, with its integration of corruption-aware training and TTA,
offers a robust solution for handling noisy text inputs. By dynamically adapting to new data distributions at
test time, it ensures reliable performance in real-world scenarios where data imperfections are inevitable,
making it a tool for practical machine learning applications.

Another example of TTA can be seen regarding [MNIST](./../mnist/tta/).
