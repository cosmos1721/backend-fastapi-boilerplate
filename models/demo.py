from typing import Optional, Tuple
from pydantic import BaseModel, Field




class DEMO_SUB_MODEL(BaseModel):
    TEST : str = Field(...)

class DEMO_MODEL(BaseModel):
    video_url : str = Field(...)