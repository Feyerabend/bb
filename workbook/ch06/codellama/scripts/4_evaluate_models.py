import argparse
import json
import math
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from datasets import load_from_disk
from tqdm import tqdm

def compute_perplexity(model, tokenizer, dataset, max_length=512, batch_size=4):
    model.eval()
    total_loss = 0
    total_tokens = 0
    device = next(model.parameters()).device

    for i in tqdm(range(0, len(dataset), batch_size)):
        batch = dataset[i:i+batch_size]
        inputs = tokenizer(batch["text"], return_tensors="pt", truncation=True, max_length=max_length, padding=True).to(device)
        with torch.no_grad():
            outputs = model(**inputs, labels=inputs["input_ids"])
        total_loss += outputs.loss.item() * inputs["attention_mask"].sum().item()
        total_tokens += inputs["attention_mask"].sum().item()

    perplexity = math.exp(total_loss / total_tokens) if total_tokens > 0 else float("inf")
    return perplexity

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_path", type=str, default="./fine_tuned_model", help="Fine-tuned model path")
    parser.add_argument("--base_model", type=str, default="codellama/CodeLlama-7b-hf", help="Base model for baseline")
    args = parser.parse_args()

    # Load tokenizer (shared)
    tokenizer = AutoTokenizer.from_pretrained(args.base_model)
    tokenizer.pad_token = tokenizer.eos_token

    # Load test dataset
    test_dataset = load_from_disk("data/test")

    # Baseline
    baseline_model = AutoModelForCausalLM.from_pretrained(args.base_model, device_map="auto")
    baseline_ppl = compute_perplexity(baseline_model, tokenizer, test_dataset)
    
    # Fine-tuned (load with PEFT)
    from peft import PeftModel
    finetuned_model = AutoModelForCausalLM.from_pretrained(args.base_model, device_map="auto")
    finetuned_model = PeftModel.from_pretrained(finetuned_model, args.model_path)
    finetuned_ppl = compute_perplexity(finetuned_model, tokenizer, test_dataset)

    # Save results
    results = {
        "baseline": {"perplexity": baseline_ppl},
        "finetuned": {"perplexity": finetuned_ppl}
    }
    with open("results/baseline_results.json", "w") as f:
        json.dump({"perplexity": baseline_ppl}, f)
    with open("results/finetuned_results.json", "w") as f:
        json.dump({"perplexity": finetuned_ppl}, f)
    print(results)

if __name__ == "__main__":
    main()
