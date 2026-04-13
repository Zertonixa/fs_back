import enum

class ComplaintStatus(enum.Enum):
    SENT = "Sent"
    RECEIVED = "Received"
    SOLVED = "Solved"
    UPDATED = "Updated"