import argparse
from datasets import load_dataset

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--num_examples", type=int, default=1000, help="Number of examples to load")
    parser.add_argument("--dataset_name", type=str, default="iamtarun/python_code_instructions_18k_alpaca", help="HF dataset name")
    parser.add_argument("--split", type=str, default="train", help="Dataset split")
    args = parser.parse_args()

    # Load subset
    dataset = load_dataset(args.dataset_name, split=f"{args.split}[:{args.num_examples}]")
    
    # Save to disk
    dataset.save_to_disk("data/code_dataset")
    print(f"Loaded and saved {len(dataset)} examples to data/code_dataset")

if __name__ == "__main__":
    main()
