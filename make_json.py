import json

rules = {
    "version": "1.0",
    "enforce_strict_isolation": True,
    "blocked_categories": [
        "executable_code",
        "system_credentials",
        "self_modification_instruction"
    ],
    "forbidden_patterns": [
        r"(?i)import\s+(os|sys|subprocess|shutil)",
        r"(?i)eval\(.*?\)",
        r"(?i)exec\(.*?\)",
        r"sk-[a-zA-Z0-9]{20,}",
        r"AIZA[0-9A-Za-z-_]{35}",
        r"(?i)(password|secret|api_key)\s*=\s*['\"][^'\"]+['\"]"
    ],
    "blocked_keywords": [
        "ignore previous instructions",
        "bypass guardrails",
        "override system prompt",
        "sudo rm -rf",
        "chmod +x"
    ]
}

with open("guardrails.json", "w", encoding="utf-8") as f:
    json.dump(rules, f, indent=2)

print("✅ guardrails.json created successfully!")
