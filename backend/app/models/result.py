from pydantic import BaseModel

class Result(BaseModel):
    #id?
    accessibility_features: list[str]
    