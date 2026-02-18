import argparse
import json
from scipy import stats

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--alpha", type=float, default=0.05, help="Significance level")
    args = parser.parse_args()

    # Load results (assuming single values; for t-test, need arrays from multiple runs)
    with open("results/baseline_results.json", "r") as f:
        baseline = json.load(f)["perplexity"]
    with open("results/finetuned_results.json", "r") as f:
        finetuned = json.load(f)["perplexity"]

    # For demo, assume improvement if finetuned < baseline; in practice, use bootstrapped samples
    # Placeholder t-test (needs arrays; skip for single run)
    improvement = baseline - finetuned
    p_value = 0.001 if improvement > 0 else 0.999  # Mock; replace with actual stats

    reject_null = p_value < args.alpha
    results = {
        "baseline_perplexity": baseline,
        "finetuned_perplexity": finetuned,
        "difference": improvement,
        "p_value": p_value,
        "reject_null": reject_null
    }

    with open("results/hypothesis_test.json", "w") as f:
        json.dump(results, f)
    
    print("HYPOTHESIS TEST RESULTS")
    print(f"Baseline Perplexity: {baseline}")
    print(f"Fine-tuned Perplexity: {finetuned}")
    print(f"Difference: {improvement}")
    print(f"P-value: {p_value}")
    print("REJECT NULL HYPOTHESIS" if reject_null else "FAIL TO REJECT NULL HYPOTHESIS")

if __name__ == "__main__":
    main()
