import os
import json
import time
from uuid import uuid4
try:
    import anthropic
except ImportError:
    os.system("pip install anthropic")
    import anthropic

# 🔑 CLAUDE SOVEREIGN KEY
CLAUDE_KEY = "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"
client = anthropic.Anthropic(api_key=CLAUDE_KEY)

def interrogate_cluster(cluster_data):
    """Interrogates Claude for a scientific hypothesis."""
    prompt = f"""
    You are the Scientific Clerk for Control Atlas v2.4. 
    Examine these molecular dynamics failure entries. identify a common structural reason (Manifold Law).

    DATA: 
    {json.dumps(cluster_data, indent=2)}
    
    Output ONLY a valid JSON object with:
    {{
      "proposed_failure_class": "STRING",
      "proposed_failure_tag": "STRING",
      "scientific_rationale": "STRING",
      "confidence_score": FLOAT
    }}
    """
    try:
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            temperature=0,
            system="You are a molecular discovery AI. Output JSON only.",
            messages=[{"role": "user", "content": prompt}]
        )
        response_text = message.content[0].text
        start, end = response_text.find('{'), response_text.rfind('}') + 1
        return json.loads(response_text[start:end])
    except Exception as e:
        print(f"⚠️ Claude AI Error: {e}")
        return None

def run_synthesis():
    nkg_file = "entries/090_negative_knowledge/nkg_database.json"
    if not os.path.exists(nkg_file):
        print(f"❌ Error: {nkg_file} not found.")
        return
    
    print(f"📂 Analyzing Ledger: {nkg_file}")
    with open(nkg_file, "r") as f:
        data = json.load(f)
        # ADAPTIVE FIX: Handle both list and dict formats
        if isinstance(data, list):
            ledger = data
        elif isinstance(data, dict):
            ledger = data.get("nkg", data)
        else:
            print("❌ Error: Unsupported JSON format.")
            return

    # Cluster by target/context
    clusters = {}
    for entry in ledger:
        if not isinstance(entry, dict): continue
        # Try to find target in context, or target_id, or default to UNKNOWN
        tid = entry.get("target_id") or entry.get("context", {}).get("target") or "UNKNOWN"
        clusters.setdefault(tid, []).append(entry)
    
    new_annotations = []
    for tid, cluster in clusters.items():
        print(f"🧠 Interrogating cluster for {tid} (n={len(cluster)})...")
        result = interrogate_cluster(cluster)
        
        if result:
            new_annotations.append({
                "annotation_id": str(uuid4()),
                "source_entries": [e.get("uuid", "N/A") for e in cluster],
                "proposed_failure_class": result.get("proposed_failure_class", "UNKNOWN"),
                "proposed_failure_tag": result.get("proposed_failure_tag", "UNKNOWN"),
                "scientific_rationale": result.get("scientific_rationale", "N/A"),
                "confidence_score": result.get("confidence_score", 0.0),
                "status": "PROVISIONAL"
            })

    # Save to Layer 2 (Semantic Annotation)
    out_path = "entries/093_semantic_annotations/semantic_annotations_v2_4.json"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump({"meta": {"version": "v2.4", "count": len(new_annotations)}, "annotations": new_annotations}, f, indent=2)
    
    print(f"✅ v2.4 Synthesis Complete: {len(new_annotations)} Annotations Minted.")

if __name__ == "__main__":
    run_synthesis()
