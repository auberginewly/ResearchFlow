from src.models import ResearchEvent


def build_event(event_type: str, **data) -> ResearchEvent:
    return ResearchEvent(type=event_type, data=data)
