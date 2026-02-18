import argparse
from datasets import load_from_disk, DatasetDict
from transformers import AutoTokenizer

def format_example(example):
    # Assuming dataset has 'instruction' and 'output' fields; adjust if needed
    prompt = example.get('prompt', example['instruction'])
    completion = example.get('completion', example['output'])
    return {"text": f"<s>[INST] {prompt} [/INST] {completion} </s>"}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--train_split", type=float, default=0.8, help="Train split ratio")
    parser.add_argument("--max_length", type=int, default=512, help="Max sequence length")
    parser.add_argument("--model_name", type=str, default="codellama/CodeLlama-7b-hf", help="Model for tokenizer")
    args = parser.parse_args()

    # Load dataset
    dataset = load_from_disk("data/code_dataset")
    
    # Format
    formatted_dataset = dataset.map(format_example)
    
    # Tokenizer
    tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    tokenizer.pad_token = tokenizer.eos_token

    def tokenize_function(examples):
        return tokenizer(examples["text"], truncation=True, max_length=args.max_length, padding="max_length")

    tokenized_dataset = formatted_dataset.map(tokenize_function, batched=True, remove_columns=formatted_dataset.column_names)
    
    # Split
    split_dataset = tokenized_dataset.train_test_split(test_size=1 - args.train_split)
    
    # Save splits
    split_dataset["train"].save_to_disk("data/train")
    split_dataset["test"].save_to_disk("data/test")
    print(f"Prepared and saved train ({len(split_dataset['train'])}) and test ({len(split_dataset['test'])}) datasets")

if __name__ == "__main__":
    main()
