from dataclasses import dataclass, field
from typing import List

@dataclass
class PostContentDto:
    title: str
    body: str

@dataclass
class GetRecommendRequest:
    likePostContentDtoList: List[PostContentDto] = field(default_factory=list)
    popularPostContentDtoList: List[PostContentDto] = field(default_factory=list)
    currentSearchList: List[str] = field(default_factory=list)
    popularSearchList: List[str] = field(default_factory=list)
