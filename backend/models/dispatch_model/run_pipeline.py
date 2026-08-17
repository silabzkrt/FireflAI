#!/usr/bin/env python3
"""
FireFl-AI Master Pipeline Orchestrator
Executes Stage 1 (PDF Extraction) -> Stage 2 (Dataset Generation) -> verification.
"""

import os
import sys
import subprocess
from pathlib import Path

def run_step(script_name: str, desc: str):
    print("\n" + "=" * 70)
    print(f"  RUNNING: {desc} ({script_name})")
    print("=" * 70)
    
    cmd = [sys.executable, script_name]
    res = subprocess.run(cmd)
    if res.returncode != 0:
        print(f"[ERROR] Step failed: {script_name}")
        sys.exit(res.returncode)

def main():
    base_dir = Path(__file__).resolve().parent
    os.chdir(base_dir)
    
    print("=" * 70)
    print("  FIREFL-AI: CONCEPTUAL EMERGENCY DISPATCHER TRAINING PIPELINE")
    print("=" * 70)
    
    # Stage 1: Extraction
    run_step("1_extract_papers.py", "Stage 1: Knowledge Extraction & PDF Corpus Mining")
    
    # Stage 2: Dataset Generation
    run_step("2_generate_dataset.py", "Stage 2: SFT Instruction-Response Dataset Generation")
    
    print("\n" + "=" * 70)
    print("  STAGE 1 & STAGE 2 COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print("Next Steps:")
    print("  1. To start QLoRA Fine-Tuning on your RTX 5070 GPU:")
    print("       python 3_train_model.py")
    print("  2. For a quick 5-step test training run:")
    print("       python 3_train_model.py --test_mode")
    print("  3. To evaluate benchmark dispatch scenarios:")
    print("       python 4_evaluate_dispatcher.py --benchmark")
    print("  4. To launch the interactive Tactical Dispatch Console:")
    print("       python 4_evaluate_dispatcher.py --interactive")
    print("=" * 70)

if __name__ == "__main__":
    main()
