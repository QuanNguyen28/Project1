from typing import List, Optional, Literal

from pydantic import BaseModel


class JDImproveRequest(BaseModel):

    content_md: str

    instruction: Optional[str] = (
        "Improve clarity, structure, and tone; keep Markdown; preserve facts."
    )

    language: Optional[Literal["vi", "en"]] = "vi"

    create_new_version: bool = False


class JDImproveResponse(BaseModel):

    content_md: str

    version: Optional[int] = None


class JDSuggestRequest(BaseModel):

    content_md: str

    section: Optional[str] = None

    goal: Optional[str] = (
        "Suggest 5-8 concise bullets aligned with the tone. Keep Markdown."
    )

    language: Optional[Literal["vi", "en"]] = "vi"

    chunks_text: Optional[str] = None


class JDSuggestResponse(BaseModel):

    suggestions: List[str]

    rationale: Optional[str] = None
