"""
Pydantic schemas for request/response validation.

NodeCreate: for POST body (name, host, port — all required)
NodeUpdate: for PUT body (host, port — optional)
NodeResponse: for API responses (includes id, status, timestamps)
"""

# TODO: Implement your Pydantic schemas here
import datetime
from pydantic import BaseModel, Field

class NodeCreate(BaseModel):
    
    name: str = Field(..., example="node-alpha")
    host: str = Field(..., example="192.168.1.10")
    port: int = Field(..., example=8081)
    # status, created_at, updated_at no se incluyen porque se generan automáticamente con valores por defecto.

class NodeUpdate(BaseModel):
    # Como pueden venir cualquier combinacion de campos, todos son opcionales
    name: str = Field(None, example="node-alpha")  # Aunque el enunciado no menciona que se pueda actualizar el nombre, lo incluyo para mayor flexibilidad
    host: str = Field(None, example="192.168.1.10")
    port: int = Field(None, example=8081)

class NodeResponse(BaseModel):
    id: int = Field(..., example=1)
    name: str = Field(..., example="node-alpha")
    host: str = Field(..., example="192.168.1.10")
    port: int = Field(..., example=8081)
    status: str = Field(..., example="active")
    created_at: datetime.datetime = Field(..., example="2026-04-01T12:00:00")
    updated_at: datetime.datetime = Field(..., example="2026-04-01T12:00:00")



