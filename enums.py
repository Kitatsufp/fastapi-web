from enum import Enum


class PeriodEnum(str, Enum):
    morning = "morning"
    afternoon = "afternoon"
    evening = "evening"


class BlockEnum(str, Enum):
    early_morning = "early_morning"
    mid_morning = "mid_morning"
    late_morning = "late_morning"

    early_afternoon = "early_afternoon"
    mid_afternoon = "mid_afternoon"
    late_afternoon = "late_afternoon"

    early_evening = "early_evening"
    mid_evening = "mid_evening"
    late_evening = "late_evening"
