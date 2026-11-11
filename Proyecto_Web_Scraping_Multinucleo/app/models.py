from pydantic import BaseModel, Field
from typing import Optional


class StoreOffer(BaseModel):
    store: str
    current_price: Optional[float] = None
    regular_price: Optional[float] = None
    format: Optional[str] = None
    platform: Optional[str] = None
    url: Optional[str] = None
    updated_at: Optional[str] = None


class GameRecord(BaseModel):
    id: str
    name: str
    platforms: list[str] = Field(default_factory=list)
    release_date: Optional[str] = None
    reference_price: Optional[float] = None
    image_url: Optional[str] = None
    metacritic_score: Optional[float] = None
    metacritic_scores: Optional[dict[str, int]] = None
    hltb_main_hours: Optional[float] = None
    hltb_extra_hours: Optional[float] = None
    hltb_completionist_hours: Optional[float] = None
    offers: list[StoreOffer] = Field(default_factory=list)
    updated_at: Optional[str] = None
