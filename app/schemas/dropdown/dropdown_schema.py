from pydantic import BaseModel, ConfigDict

class DropdownRead(BaseModel):
    id: int
    value_text: str
    
    model_config = ConfigDict(
        from_attributes=True,
    )