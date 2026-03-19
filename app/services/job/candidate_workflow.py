"""
Candidate Status Workflow State Machine

Valid statuses: Applied → Screening → Interview → Offered → Hired
                                                  ↘ Rejected (from any stage)
                                                  ↘ Withdrawn (from any stage)
"""

VALID_STATUSES = {"Applied", "Screening", "Interview", "Offered", "Hired", "Rejected", "Withdrawn"}

TRANSITIONS = {
    "Applied":    {"Screening", "Rejected", "Withdrawn"},
    "Screening":  {"Interview", "Rejected", "Withdrawn"},
    "Interview":  {"Offered", "Rejected", "Withdrawn"},
    "Offered":    {"Hired", "Rejected", "Withdrawn"},
    "Hired":      set(),
    "Rejected":   set(),
    "Withdrawn":  set(),
}


def validate_transition(current: str, target: str) -> bool:
    if target not in VALID_STATUSES:
        raise ValueError(f"Invalid status: {target}. Must be one of {VALID_STATUSES}")
    allowed = TRANSITIONS.get(current, set())
    if target not in allowed:
        raise ValueError(f"Cannot move from '{current}' to '{target}'. Allowed: {allowed or 'none (terminal state)'}")
    return True
