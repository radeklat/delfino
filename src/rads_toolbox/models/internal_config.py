from pydantic import BaseModel


class Poetry(BaseModel):
    name: str
    version: str


class Tool(BaseModel):
    poetry: Poetry


class PyProjectToml(BaseModel):
    tool: Tool
