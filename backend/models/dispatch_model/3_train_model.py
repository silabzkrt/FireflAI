#!/usr/bin/env python3
"""
Stage 3: QLoRA Conceptual Fine-Tuning
Trains a conceptual emergency dispatcher LLM using 4-bit QLoRA on `data/firefl_dispatch_dataset.jsonl`.
Optimized for NVIDIA RTX 5070 (8GB VRAM) using `Qwen/Qwen2.5-3B-Instruct` (default)
with PEFT LoRA adapters.
"""

import os
import sys
import json
import argparse
import torch
from pathlib import Path
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
try:
    from trl import SFTTrainer, SFTConfig
    HAS_SFT_CONFIG = True
except ImportError:
    from trl import SFTTrainer
    HAS_SFT_CONFIG = False

DEFAULT_MODEL_NAME = "Qwen/Qwen2.5-3B-Instruct"

def get_device_info():
    if not torch.cuda.is_available():
        return {"device": "cpu", "vram_gb": 0, "name": "CPU"}
    name = torch.cuda.get_device_name(0)
    vram_bytes = torch.cuda.get_device_properties(0).total_memory
    vram_gb = vram_bytes / (1024 ** 3)
    return {"device": "cuda", "vram_gb": vram_gb, "name": name}

def format_prompt(example):
    """Formats training data into structured ChatML / Qwen prompt syntax."""
    instruction = example["instruction"]
    response = example["response"]
    
    text = (
        f"<|im_start|>system\n"
        f"Sen Türkiye Afet Müdahale Planı (TAMP) ve OGM yönergelerine hakim, tüm emirlerini KESİN GPS KOORDİNATLARI ([Enlem°N, Boylam°E]), hedef savunma sektörleri, dozer hendek/yangın şeridi koordinat hatları ve su alım/boşaltım noktaları üzerinden operasyonel askeri emir formatında veren taktiksel bir komuta merkezisin.<|im_end|>\n"
        f"<|im_start|>user\n"
        f"{instruction}<|im_end|>\n"
        f"<|im_start|>assistant\n"
        f"{response}<|im_end|>"
    )
    return {"text": text}

def main():
    parser = argparse.ArgumentParser(description="FireFl-AI QLoRA Fine-Tuning Script")
    parser.add_argument("--model_name", type=str, default=DEFAULT_MODEL_NAME, help="HuggingFace model ID")
    parser.add_argument("--test_mode", action="store_true", help="Run only 5 steps for quick verification")
    parser.add_argument("--epochs", type=int, default=3, help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=2, help="Per device batch size")
    parser.add_argument("--lr", type=float, default=2e-4, help="Learning rate")
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent
    dataset_path = base_dir / "data" / "firefl_dispatch_dataset.jsonl"
    output_dir = base_dir / "models" / "firefl_dispatcher_lora"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("  FIREFL-AI: STAGE 3 - QLoRA CONCEPTUAL LLM FINE-TUNING")
    print("=" * 70)
    
    dev_info = get_device_info()
    print(f"Device Name      : {dev_info['name']}")
    print(f"Available VRAM   : {dev_info['vram_gb']:.2f} GB")
    print(f"Target Base Model: {args.model_name}")
    print(f"Dataset Path     : {dataset_path}")
    print(f"Test Mode        : {args.test_mode}\n")

    if not dataset_path.exists():
        print(f"[ERROR] Dataset {dataset_path} not found! Please run `python 2_generate_dataset.py` first.")
        return

    # 1. Load Dataset
    print("Loading and formatting dataset...")
    dataset = load_dataset("json", data_files=str(dataset_path), split="train")
    dataset = dataset.map(format_prompt)
    print(f"Loaded {len(dataset)} training examples.\n")

    # 2. Configure 4-bit Quantization (QLoRA)
    use_bf16 = torch.cuda.is_bf16_supported()
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16 if use_bf16 else torch.float16,
        bnb_4bit_use_double_quant=True,
    )

    # 3. Load Tokenizer & Model
    print("Loading base model and tokenizer (this may take a few minutes on first run)...")
    tokenizer = AutoTokenizer.from_pretrained(args.model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    model = AutoModelForCausalLM.from_pretrained(
        args.model_name,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True
    )
    model = prepare_model_for_kbit_training(model)

    # 4. Configure PEFT LoRA
    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )

    # 5. Training Arguments
    max_steps = 5 if args.test_mode else -1
    num_train_epochs = 1 if args.test_mode else args.epochs

    if HAS_SFT_CONFIG:
        training_args = SFTConfig(
            output_dir=str(output_dir),
            dataset_text_field="text",
            max_length=1536,
            per_device_train_batch_size=args.batch_size,
            gradient_accumulation_steps=2,
            learning_rate=args.lr,
            lr_scheduler_type="cosine",
            warmup_steps=5,
            num_train_epochs=num_train_epochs,
            max_steps=max_steps,
            logging_steps=1 if args.test_mode else 5,
            save_strategy="steps" if args.test_mode else "epoch",
            save_steps=5 if args.test_mode else 50,
            fp16=not use_bf16,
            bf16=use_bf16,
            optim="paged_adamw_8bit",
            report_to="none"
        )
        trainer = SFTTrainer(
            model=model,
            train_dataset=dataset,
            peft_config=lora_config,
            processing_class=tokenizer,
            args=training_args
        )
    else:
        training_args = TrainingArguments(
            output_dir=str(output_dir),
            per_device_train_batch_size=args.batch_size,
            gradient_accumulation_steps=4,
            learning_rate=args.lr,
            lr_scheduler_type="cosine",
            warmup_steps=5,
            num_train_epochs=num_train_epochs,
            max_steps=max_steps,
            logging_steps=1 if args.test_mode else 5,
            save_strategy="steps" if args.test_mode else "epoch",
            save_steps=5 if args.test_mode else 50,
            fp16=not use_bf16,
            bf16=use_bf16,
            optim="paged_adamw_8bit",
            report_to="none"
        )
        trainer = SFTTrainer(
            model=model,
            train_dataset=dataset,
            peft_config=lora_config,
            dataset_text_field="text",
            max_seq_length=1024,
            tokenizer=tokenizer,
            args=training_args
        )

    print("\nStarting QLoRA training...")
    trainer.train()

    print("\nSaving fine-tuned LoRA adapter...")
    trainer.model.save_pretrained(str(output_dir))
    tokenizer.save_pretrained(str(output_dir))

    # Save model metadata
    metadata = {
        "base_model": args.model_name,
        "lora_rank": 16,
        "lora_alpha": 32,
        "training_examples": len(dataset),
        "test_mode": args.test_mode
    }
    with open(output_dir / "firefl_metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print("\n" + "=" * 70)
    print("  TRAINING COMPLETE!")
    print(f"  LoRA adapter saved to: {output_dir}")
    print("=" * 70)

if __name__ == "__main__":
    main()
