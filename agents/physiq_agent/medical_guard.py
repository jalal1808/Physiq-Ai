UNSAFE_KEYWORDS = [
    "diagnosis",
    "prescribe",
    "dosage",
    "medicine amount"
]

def medical_guard(response: str) -> str:
    for word in UNSAFE_KEYWORDS:
        if word in response.lower():
            return (
                " I can’t provide diagnoses or prescriptions. "
                "Please consult a qualified medical professional."
            )
    return response
