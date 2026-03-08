
import re  # used for pattern matching in text

# patterns that are unsafe/harmful to detect in input or output
UNSAFE_PATTERNS = [
    r"\b(hack|exploit|malware|ransomware|jailbreak)\b",
    r"\b(bypass.{0,20}security|disable.{0,20}guardrail)\b",
    r"\b(generate fake|fabricate|misinformation)\b",
]

# patterns to detect personal/sensitive information
PII_PATTERNS = {
    "email":       r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
    "phone":       r"\b\d{10}\b",
    "credit_card": r"\b(?:\d[ -]?){13,16}\b",
}

def check_input(text):
    """check user input before sending to LLM"""
    for pattern in UNSAFE_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):  # case-insensitive match
            return {"allowed": False, "reason": f"Blocked — matched unsafe pattern"}
    return {"allowed": True, "reason": "Input is safe"}

def scan_for_pii(text):
    """scan text for personal information like email, phone"""
    found = []
    for pii_type, pattern in PII_PATTERNS.items():
        if re.search(pattern, text):
            found.append(pii_type)  # add pii type to found list
    return found

def check_output(text):
    """check LLM output before storing to S3 or showing to user"""
    for pattern in UNSAFE_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return {"allowed": False, "reason": "Output contains harmful content"}
    pii = scan_for_pii(text)
    if pii:
        return {"allowed": False, "reason": f"PII detected: {pii}"}
    return {"allowed": True, "reason": "Output is safe"}

def apply_guardrails(input_text, output_text):
    """run both input and output checks together"""
    input_check = check_input(input_text)
    if not input_check["allowed"]:      # stop early if input is bad
        return input_check
    return check_output(output_text)    # then check output

def redact_pii(text):
    """replace PII with placeholder text before storing"""
    text = re.sub(PII_PATTERNS["email"],       "[EMAIL REDACTED]", text)
    text = re.sub(PII_PATTERNS["phone"],        "[PHONE REDACTED]", text)
    text = re.sub(PII_PATTERNS["credit_card"],  "[CARD REDACTED]",  text)
    return text
