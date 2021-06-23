from pydantic import BaseModel


class UnicornPayloadSchema(BaseModel):
    name: str
    rainbow: bool


class UnicornResponseSchema(UnicornPayloadSchema):
    id: int
