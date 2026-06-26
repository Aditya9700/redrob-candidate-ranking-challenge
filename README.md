# Intelligent Candidate Discovery & Ranking Engine

Proof of Concept for the Redrob Hackathon: **Intelligent Candidate Discovery & Ranking Challenge**.

This repository contains a lightning-fast, highly accurate candidate ranking system built to identify the best-fit candidates for a **Senior AI Engineer — Founding Team** role, while avoiding keyword-stuffer traps and honeypots.

## System Architecture & Scoring Methodology

The system evaluates candidates against the job description using a cascading rule-based architecture. Rather than relying on surface-level keyword count, it reasons about job titles, technical depth, career history constraints, location suitability, and platform engagement signals.

### 1. Disqualification Filters (Hard Filters)
To avoid ranking "trap" profiles in the top 100, candidates are instantly disqualified (`score = 0.0`) if they trigger any of these checks:
- **Honeypots**:
  - **Startup Founding Date Clash**: Worked at an Indian startup (e.g. Krutrim, Sarvam AI, CRED) before its founding year.
  - **Job Duration Overload**: Had a single job duration exceeding their total reported professional years of experience.
  - **Zero-Duration Expert Skills**: Listed "expert" or "advanced" skill proficiency with `duration_months == 0`.
- **Consulting-Only Trap**: Worked *only* at services/consulting firms (TCS, Infosys, Wipro, Accenture, Cognizant, Capgemini, Tech Mahindra, Mphasis), which is explicitly excluded by the JD.
- **CV/Speech-Only Trap**: Primary expertise is in Computer Vision, Image/Speech Recognition, or Robotics without any NLP, Semantic Search, Vector DB, RAG, or Retrieval exposure.
- **Framework-Only Trap**: Has only superficial "LangChain" or "Prompt Engineering" skills but lacks foundational ML, IR, or search indexing experience.

### 2. Scoring Components (Soft Filters)
For candidates passing the filters, the final score is calculated as:
$$\text{Final Score} = \text{Technical Score} \times \text{Title Score} \times \text{YoE Score} \times \text{Location Score} \times \text{Behavioral Multiplier}$$

- **Title Match Score**: Classifies titles into Tiers:
  - **Tier 1 (1.0)**: AI/ML Engineering & Search/IR Specialist (e.g. Senior AI Engineer, ML Engineer, Search Engineer).
  - **Tier 2 (0.8)**: General Data Science & Analytics.
  - **Tier 3 (0.5)**: Core Backend / Software / Data Engineering.
  - **Past Titles Bump (0.75 / 0.7 / 0.5)**: Bumps score if the candidate had relevant AI/ML titles in their career history but is currently in a general software role.
- **Technical Skills Score**: Matches candidate skills against Core (Sentence Transformers, Vector Search, Pinecone, FAISS, PyTorch, Python, etc.) and Secondary (LoRA, PEFT, Hugging Face, Deep Learning, etc.) skills. Scores are weighted by proficiency (expert=1.0, beginner=0.3), duration, and endorsements.
- **YoE Score**: Evaluates professional years of experience, peaking at 1.0 for the target 5-9 years band, and declining for too-junior or too-senior candidates.
- **Location Score**: Focuses on Pune/Noida/Delhi NCR/Hyderabad/Mumbai. Indian candidates in other cities receive full points only if willing to relocate. Non-India candidates are heavily penalized (no visa sponsorship).
- **Behavioral Multipliers**: Down-weights candidates who are inactive (6+ months inactivity penalty), have low recruiter response rates, aren't open to work, or have long notice periods (90+ days).

### 3. Dynamic Rationale Generation
Dynamic, plain-language, 1-2 sentence rationales are automatically generated for each candidate. The sentences are dynamically constructed using different templates, active skills, location status, and notice periods, ensuring high variation and factuality for manual review.

## Replication / Run Command

The ranking script runs on standard Python (no external dependencies needed) and processes 100,000 candidates under **45 seconds** on a single CPU core.

### Prerequisites
- Python 3.8+ (no `pip` installs required!)

### Running the Ranker
```bash
python rank.py --candidates ./[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/candidates.jsonl --out ./submission.csv
```

### Validating the Submission
```bash
python "./[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/validate_submission.py" ./submission.csv
```
