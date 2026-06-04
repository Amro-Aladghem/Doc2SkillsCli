from dataclasses import dataclass

@dataclass
class Config:
    api_key:str
    model:str
    max_content_size:str

