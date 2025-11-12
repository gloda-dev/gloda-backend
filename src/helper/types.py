from enum import StrEnum


class AuthType(StrEnum):
    KAKAO = "kakao"
    NAVER = "naver"
    ## PASS = "pass"


class EventStatus(StrEnum):
    PLANNED = "planned"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
