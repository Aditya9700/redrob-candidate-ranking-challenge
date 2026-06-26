import json
import os
import math
import argparse
import csv
from datetime import datetime

FOUNDING_YEARS = {
    "Krutrim": 2023,
    "Sarvam AI": 2023,
    "CRED": 2018,
    "Rephrase.ai": 2019,
    "Saarthi.ai": 2018,
    "BYJU'S": 2011,
    "Dream11": 2008,
    "Paytm": 2010,
    "Ola": 2010,
    "Swiggy": 2014,
    "Meesho": 2015,
    "Freshworks": 2010,
    "Zomato": 2008,
    "Flipkart": 2007,
    "Razorpay": 2014,
    "Nykaa": 2012,
    "PharmEasy": 2015,
    "PhonePe": 2015,
    "PolicyBazaar": 2008,
    "Unacademy": 2015,
    "Vedantu": 2011,
    "upGrad": 2015,
    "Wysa": 2015,
    "Yellow.ai": 2016,
    "Niramai": 2016,
    "Observe.AI": 2017,
    "Verloop.io": 2015,
    "Aganitha": 2018,
    "Locobuzz": 2015,
    "Mad Street Den": 2013,
    "Haptik": 2013
}

CONSULTING_FIRMS = {"TCS", "Infosys", "Wipro", "Accenture", "Cognizant", "Capgemini", "Tech Mahindra", "Mphasis"}

CORE_SKILLS = {
    "Sentence Transformers", "Embeddings", "Vector Search", "Semantic Search", "RAG", "BM25",
    "Information Retrieval", "Pinecone", "Weaviate", "Qdrant", "Milvus", "Elasticsearch",
    "OpenSearch", "pgvector", "FAISS", "Learning to Rank", "Python", "PyTorch"
}

SECONDARY_SKILLS = {
    "LLMs", "Fine-tuning LLMs", "LoRA", "QLoRA", "PEFT", "Hugging Face Transformers",
    "LlamaIndex", "LangChain", "Deep Learning", "Machine Learning", "Data Science", "Feature Engineering"
}

CV_SPEECH_SKILLS = {
    "Computer Vision", "Object Detection", "OpenCV", "YOLO", "ASR", "Speech Recognition",
    "TTS", "Diffusion Models", "GANs", "CNN"
}

PREFERRED_TITLES = {
    "Senior AI Engineer", "AI Engineer", "Senior Machine Learning Engineer", "Machine Learning Engineer",
    "Senior NLP Engineer", "NLP Engineer", "Search Engineer", "Recommendation Systems Engineer",
    "Applied ML Engineer", "Senior Software Engineer (ML)", "ML Engineer", "AI Specialist",
    "Applied Scientist", "AI Research Engineer"
}

SECONDARY_TITLES = {
    "Senior Data Scientist", "Data Scientist", "Junior ML Engineer", "Computer Vision Engineer"
}

CORE_DEV_TITLES = {
    "Backend Engineer", "Senior Software Engineer", "Software Engineer", "Data Engineer",
    "Senior Data Engineer", "Analytics Engineer", "Full Stack Developer", "Cloud Engineer",
    "DevOps Engineer", ".NET Developer", "Java Developer"
}

def is_honeypot(cand):
    career = cand.get("career_history", [])
    skills = cand.get("skills", [])
    profile = cand.get("profile", {})
    yoe = profile.get("years_of_experience", 0)
    
    # Check 1: Startup founding dates
    for job in career:
        comp = job.get("company")
        start = job.get("start_date")
        if comp in FOUNDING_YEARS and start:
            try:
                start_year = int(start.split("-")[0])
                if start_year < FOUNDING_YEARS[comp]:
                    return True, f"worked at {comp} in {start_year} before founded in {FOUNDING_YEARS[comp]}"
            except:
                pass
                
    # Check 2: Single job duration > yoe + 0.1
    for job in career:
        dur_m = job.get("duration_months", 0)
        dur_y = dur_m / 12.0
        if dur_y > yoe + 0.1:
            return True, f"single job duration {dur_y:.1f}y exceeds yoe {yoe}"
            
    # Check 3: Expert/advanced skill with 0 duration
    expert_zero = [s for s in skills if s.get("proficiency") in ["expert", "advanced"] and s.get("duration_months", -1) == 0]
    if len(expert_zero) > 0:
        return True, f"expert/advanced skills with 0 duration: {[s['name'] for s in expert_zero]}"
        
    return False, ""

def only_worked_at_consulting(cand):
    career = cand.get("career_history", [])
    if not career:
        return False
    return all(job.get("company") in CONSULTING_FIRMS for job in career)

def check_cv_speech_only(skills_set):
    has_cv = any(s in CV_SPEECH_SKILLS for s in skills_set)
    has_nlp_ir = any(s in CORE_SKILLS or s in SECONDARY_SKILLS for s in skills_set)
    return has_cv and not has_nlp_ir

def check_langchain_only(skills_set):
    has_langchain = "LangChain" in skills_set or "Prompt Engineering" in skills_set
    has_core = any(s in CORE_SKILLS or s in (SECONDARY_SKILLS - {"LangChain", "Prompt Engineering"}) for s in skills_set)
    return has_langchain and not has_core

def generate_reasoning(cand, score, title_tier, has_pref_past):
    profile = cand.get("profile", {})
    skills = cand.get("skills", [])
    signals = cand.get("redrob_signals", {})
    yoe = profile.get("years_of_experience", 0.0)
    curr_title = profile.get("current_title", "")
    location = profile.get("location", "")
    notice = signals.get("notice_period_days", 0)
    
    # Extract core skills
    core_held = [s.get("name") for s in skills if s.get("name") in CORE_SKILLS]
    sec_held = [s.get("name") for s in skills if s.get("name") in SECONDARY_SKILLS]
    
    # 1. Openings based on title match
    openings = []
    if title_tier == 1:
        openings = [
            f"Strong matching {curr_title} with {yoe} years of experience.",
            f"Candidate is a {curr_title} bringing {yoe} years of professional experience.",
            f"Solid {yoe}-year history as a {curr_title}, aligning perfectly with the JD."
        ]
    elif title_tier == 2:
        openings = [
            f"Relevant background as {curr_title} with {yoe} years of experience.",
            f"Data Science profile with {yoe} years as a {curr_title}.",
            f"Brings {yoe} years of experience in analytics/data science as a {curr_title}."
        ]
    else: # Tier 3 or past title bump
        if has_pref_past:
            openings = [
                f"Currently a {curr_title} with {yoe} years of experience, but has past ML/AI titles.",
                f"Backend specialist with {yoe} years of experience and prior ML exposure in career history.",
                f"Software Engineer with {yoe} years of experience and relevant ML/AI background."
            ]
        else:
            openings = [
                f"Core engineer ({curr_title}) with {yoe} years of experience.",
                f"Experienced {curr_title} with {yoe} years in backend/software engineering.",
                f"Software developer ({curr_title}) with a solid {yoe}-year track record."
            ]
            
    # 2. Skill descriptions
    skill_parts = []
    if core_held:
        skill_parts = [
            f"Demonstrates hands-on expertise in {', '.join(core_held[:2])}.",
            f"Brings strong experience in {', '.join(core_held[:2])}.",
            f"Proven skills in core areas like {', '.join(core_held[:2])}."
        ]
    elif sec_held:
        skill_parts = [
            f"Experienced in adjacent technologies like {', '.join(sec_held[:2])}.",
            f"Familiar with frameworks like {', '.join(sec_held[:2])}.",
            f"Brings relevant expertise in {', '.join(sec_held[:2])}."
        ]
    else:
        skill_parts = [
            "Lacks specific semantic search or embeddings experience, but shows strong core engineering fundamentals.",
            "Demonstrates solid general developer capabilities across multiple platforms.",
            "Brings transferable engineering skills to the founding team."
        ]
        
    # 3. Location and notice descriptions
    preferred_cities = ["pune", "noida", "delhi", "gurgaon", "ghaziabad", "faridabad", "hyderabad", "mumbai", "ncr"]
    is_preferred_city = any(city in location.lower() for city in preferred_cities)
    willing_reloc = signals.get("willing_to_relocate", False)
    
    loc_parts = []
    if is_preferred_city:
        loc_parts = [
            f"Based in {location} (target office area) and has a {notice}-day notice period.",
            f"Located in {location} with {notice}-day notice period, fitting hybrid requirements.",
            f"Hybrid-ready and based in {location} with a {notice}-day notice period."
        ]
    elif willing_reloc:
        loc_parts = [
            f"Willing to relocate from {location} and has a {notice}-day notice period.",
            f"Open to relocating to Pune/Noida from {location} (notice: {notice} days).",
            f"Relocation candidate from {location} with a {notice}-day notice period."
        ]
    else:
        loc_parts = [
            f"Located in {location} with a {notice}-day notice period.",
            f"Based in {location} (notice period: {notice} days)."
        ]
        
    # Deterministic selection based on candidate_id hash to avoid duplicate structures across top 100
    cid_hash = hash(cand.get("candidate_id", ""))
    op = openings[cid_hash % len(openings)]
    sk = skill_parts[(cid_hash >> 2) % len(skill_parts)]
    lc = loc_parts[(cid_hash >> 4) % len(loc_parts)]
    
    return f"{op} {sk} {lc}"

def score_candidate(cand):
    profile = cand.get("profile", {})
    career = cand.get("career_history", [])
    skills = cand.get("skills", [])
    signals = cand.get("redrob_signals", {})
    
    # 1. Honeypot Filters
    honeypot, _ = is_honeypot(cand)
    if honeypot:
        return 0.0, 0, False
        
    # 2. Consulting Only Filter
    if only_worked_at_consulting(cand):
        return 0.0, 0, False
        
    # 3. Skills set
    skills_set = {s.get("name") for s in skills}
    
    # 4. CV/Speech only filter
    if check_cv_speech_only(skills_set):
        return 0.0, 0, False
        
    # 5. LangChain only filter
    if check_langchain_only(skills_set):
        return 0.0, 0, False
        
    # 6. Title Score
    curr_title = profile.get("current_title", "")
    all_titles = {job.get("title") for job in career} | {curr_title}
    
    title_score = 0.0
    title_tier = 3
    has_pref_past = False
    
    if curr_title in PREFERRED_TITLES:
        title_score = 1.0
        title_tier = 1
    elif curr_title in SECONDARY_TITLES:
        title_score = 0.8
        title_tier = 2
    elif curr_title in CORE_DEV_TITLES:
        title_score = 0.5
        title_tier = 3
    else:
        # Check past titles to see if they were ever in ML/AI or software engineering
        has_pref_past = any(t in PREFERRED_TITLES for t in all_titles)
        has_sec_past = any(t in SECONDARY_TITLES for t in all_titles)
        has_dev_past = any(t in CORE_DEV_TITLES for t in all_titles)
        if has_pref_past:
            title_score = 0.7
            title_tier = 3
        elif has_sec_past:
            title_score = 0.5
            title_tier = 3
        elif has_dev_past:
            title_score = 0.3
            title_tier = 3
        else:
            title_score = 0.0
            
    if title_score == 0.0:
        return 0.0, 0, False
        
    # 7. YoE Score (fits 5-9 years band)
    yoe = profile.get("years_of_experience", 0.0)
    if 5.0 <= yoe <= 9.0:
        yoe_score = 1.0
    elif 4.0 <= yoe < 5.0:
        yoe_score = 0.8
    elif 9.0 < yoe <= 12.0:
        yoe_score = 0.8
    elif 3.0 <= yoe < 4.0:
        yoe_score = 0.6
    elif 12.0 < yoe <= 15.0:
        yoe_score = 0.5
    else:
        yoe_score = 0.2
        
    # 8. Technical Skills Score
    tech_score_sum = 0.0
    for s in skills:
        name = s.get("name")
        prof = s.get("proficiency", "beginner")
        dur = s.get("duration_months", 0)
        ends = s.get("endorsements", 0)
        
        prof_mult = {"expert": 1.0, "advanced": 0.8, "intermediate": 0.6, "beginner": 0.3}.get(prof, 0.3)
        dur_mult = min(dur / 36.0, 1.0)
        ends_boost = 1.0 + min(ends / 50.0, 0.1)
        
        s_score = prof_mult * dur_mult * ends_boost
        
        if name in CORE_SKILLS:
            tech_score_sum += s_score * 1.5
        elif name in SECONDARY_SKILLS:
            tech_score_sum += s_score * 0.75
            
    tech_score = 1.0 - math.exp(-tech_score_sum / 3.0)
    
    # 9. Location Score
    loc = profile.get("location", "").lower()
    country = profile.get("country", "").lower()
    willing_reloc = signals.get("willing_to_relocate", False)
    
    preferred_cities = ["pune", "noida", "delhi", "gurgaon", "ghaziabad", "faridabad", "hyderabad", "mumbai", "ncr"]
    is_preferred_city = any(city in loc for city in preferred_cities)
    
    if country == "india":
        if is_preferred_city:
            loc_score = 1.0
        elif willing_reloc:
            loc_score = 0.85
        else:
            loc_score = 0.15
    else:
        loc_score = 0.02 # visa barrier
        
    # 10. Behavioral Multipliers
    # A. Active Recency
    last_active = signals.get("last_active_date")
    if last_active:
        try:
            active_dt = datetime.strptime(last_active, "%Y-%m-%d")
            ref_dt = datetime(2026, 6, 1)
            inactive_days = (ref_dt - active_dt).days
            if inactive_days <= 30:
                act_mult = 1.0
            elif inactive_days <= 180:
                act_mult = 1.0 - 0.3 * ((inactive_days - 30) / 150.0)
            else:
                act_mult = 0.3 # inactive for 6+ months
        except:
            act_mult = 0.5
    else:
        act_mult = 0.5
        
    # B. Recruiter Response Rate
    resp_rate = signals.get("recruiter_response_rate", 0.0)
    resp_mult = 0.5 + 0.5 * resp_rate
    
    # C. Open to work flag
    open_to_work = signals.get("open_to_work_flag", False)
    otw_mult = 1.0 if open_to_work else 0.85
    
    # D. Notice Period
    notice = signals.get("notice_period_days", 0)
    if notice <= 30:
        notice_mult = 1.0
    elif notice == 60:
        notice_mult = 0.8
    elif notice == 90:
        notice_mult = 0.5
    else:
        notice_mult = 0.3
        
    # E. Interview Attendance
    completion = signals.get("interview_completion_rate", 0.0)
    completion_mult = 0.6 + 0.4 * completion
    
    # F. Offer Acceptance
    acc_rate = signals.get("offer_acceptance_rate", -1)
    if acc_rate == -1:
        acc_mult = 1.0
    else:
        acc_mult = 0.7 + 0.3 * acc_rate
        
    behavioral_mult = act_mult * resp_mult * otw_mult * notice_mult * completion_mult * acc_mult
    
    # Combine everything
    base_match = tech_score * title_score * yoe_score * loc_score
    final_score = base_match * behavioral_mult
    
    return final_score, title_tier, has_pref_past

def main():
    parser = argparse.ArgumentParser(description="Intelligent Candidate Ranking Engine")
    parser.add_argument("--candidates", required=True, help="Path to candidates.jsonl")
    parser.add_argument("--out", required=True, help="Path to output submission CSV")
    args = parser.parse_args()
    
    print(f"Reading candidates from {args.candidates}...")
    
    scored_candidates = []
    
    with open(args.candidates, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            if not line.strip():
                continue
            cand = json.loads(line)
            score, title_tier, has_pref_past = score_candidate(cand)
            if score > 0:
                scored_candidates.append({
                    "cand": cand,
                    "candidate_id": cand["candidate_id"],
                    "score": score,
                    "title_tier": title_tier,
                    "has_pref_past": has_pref_past
                })
            if (idx + 1) % 25000 == 0:
                print(f"Scanned {idx + 1} candidates...")
                
    print(f"Scanned total {idx + 1} candidates. Found {len(scored_candidates)} candidates with score > 0.")
    
    # Sort candidates by score descending, breaking ties by candidate_id ascending
    print("Sorting and ranking candidates...")
    scored_candidates.sort(key=lambda x: (-x["score"], x["candidate_id"]))
    
    # Get top 100
    top_100 = scored_candidates[:100]
    
    print(f"Writing top 100 candidates to {args.out}...")
    with open(args.out, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        # Header
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])
        
        for rank_idx, item in enumerate(top_100):
            rank = rank_idx + 1
            cid = item["candidate_id"]
            score = round(item["score"], 4)
            # Generate the reasoning dynamically
            reasoning = generate_reasoning(item["cand"], score, item["title_tier"], item["has_pref_past"])
            writer.writerow([cid, rank, score, reasoning])
            
    print("Ranking complete. Output generated successfully.")

if __name__ == "__main__":
    main()
