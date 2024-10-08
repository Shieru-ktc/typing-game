from enum import Enum
from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional
import requests
import os

ENDPOINT = os.getenv("SCORE_ENDPOINT")


class RecordType(str, Enum):
    TYPING = "TYPING"
    SHOOTING = "SHOOTING"


@dataclass
class PartialRecordSchema:
    score: int
    name: str
    type: RecordType
    metadata: Optional[Dict[str, Any]]


def send_record(record: PartialRecordSchema):
    if ENDPOINT:
        return requests.post(ENDPOINT + ("/"), json=asdict(record)).json()
    else:
        raise ValueError("SCORE_ENDPOINT is not specified.")
