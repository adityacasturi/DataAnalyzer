from pydantic import BaseModel

class UserQuery(BaseModel):
    input: str