# FireflAI: Tactical Dispatch Agent (LLM)

## 1. Overview
This sub-module houses the **Tactical Dispatch Agent**, the central decision-support engine of the FireflAI platform. Functioning as an Intelligent Virtual Situation Room (IVSR) orchestrator, this Large Language Model (LLM) synthesizes multimodal disaster telemetry (spread polygons, wind vectors) and GIS inventory data to autonomously generate actionable, military-grade tactical deployment orders for human responders.

## 2. Model Architecture and Optimization
The core intelligence is built upon the **Qwen/Qwen2.5-3B-Instruct** foundation model. To achieve high operational reliability while running entirely on edge hardware, the architecture implements several advanced optimization techniques:
* **Parameter-Efficient Fine-Tuning (PEFT):** The model is fine-tuned using **Low-Rank Adaptation (LoRA)** on historical dispatch logs and emergency response manuals. This aligns the model's internal weights with the strict bureaucratic and tactical terminology required by institutional protocols.
* **4-bit Quantization:** To drastically reduce VRAM overhead and inference latency (Time-to-Action), the model is loaded using **BitsAndBytes (nf4 - NormalFloat4)**. This allows the 3-billion parameter model to run highly efficiently on consumer-grade GPUs without significant degradation in reasoning capabilities.

## 3. Spatial RAG (Retrieval-Augmented Generation)
Standard LLMs are prone to spatial hallucination (e.g., inventing nonexistent resources or false GPS coordinates). To mitigate this, the Dispatch Model employs a dynamic GIS injection mechanism:
1. **Haversine Proximity Search:** Upon receiving a fire coordinate, the system calculates the exact geographic distance to all regional water sources (`su_kaynaklari.json`) and vulnerable infrastructure (`yerlesim_ve_tesisler.json`).
2. **Context Injection:** The top-$K$ nearest verified assets are injected directly into the LLM's system prompt prior to inference, grounding the generation strictly in verifiable geographic reality.

## 4. Inference and Decoding Strategy
The generation pipeline is mathematically constrained to prioritize factual determinism over creative divergence:
* **Greedy Decoding:** `do_sample=False` is enforced to ensure the model takes the highest-probability token at every step, virtually eliminating hallucinations in GPS coordinate regurgitation.
* **Repetition Penalty:** Set to `1.05` to prevent degenerative looping when formulating complex tactical instructions.
* **System Prompting Constraint:** The model is strictly instructed to format its output according to the **TAMP (Türkiye Afet Müdahale Planı)** directives, enforcing the use of exact `[Latitude, Longitude]` coordinates for defense sectors and asset deployments.

## 5. Scientific Evaluation Metrics
The efficacy of the Dispatch Agent is evaluated against standard NLP and emergency management metrics:
* **Spatial Exact Match (EM):** A binary metric (0 or 1) verifying that the GPS coordinates produced in the output text flawlessly match the injected GIS data without corruption.
* **ROUGE-L & BERTScore:** Measures the structural and semantic alignment of the generated tactical orders against historical ground-truth orders drafted by veteran Incident Commanders.
* **Inference Latency:** Measured in Tokens Per Second (TPS) and Time-to-First-Token (TTFT), ensuring the model maintains critical operational speed during internet-denied disaster scenarios where cloud APIs fail.
