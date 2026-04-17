"""
Exercise 01 — Node Registry API

Implement a FastAPI application with the following endpoints:

GET    /health          → health check with DB status
POST   /api/nodes       → register a new node
GET    /api/nodes       → list all nodes
GET    /api/nodes/{name} → get a node by name
PUT    /api/nodes/{name} → update a node
DELETE /api/nodes/{name} → soft-delete a node (set status=inactive)

See README.md for full specification.
"""

# TODO: Implement your FastAPI app here

from datetime import datetime, timezone
from datetime import datetime
from fastapi import Depends, FastAPI, Response, status
import json

from sqlalchemy import text
from sqlalchemy.orm import Session
from src.schemas import NodeCreate, NodeResponse, NodeUpdate
from src.database import get_db
from src.models import Node

app = FastAPI()


@app.get("/health")
def health_check(db: Session = Depends(get_db)):

    nodes_count = getNodeCount(db)

    try:
        
        # verifico que la db esta healthy haciendo una consulta simple
        db.execute(text("SELECT 1")) 
        db_status = "connected"
        app_status = "ok"
        http_status = status.HTTP_200_OK

    except Exception as e:
        db_status = "disconnected"
        app_status = "error"
        http_status = status.HTTP_503_SERVICE_UNAVAILABLE
        
    return Response(
        content=json.dumps({
            "status": app_status,
            "db": db_status,
            "nodes_count": nodes_count,
        }),
        media_type="application/json",
        status_code=http_status
    )


@app.post("/api/nodes")
def register_node(request: NodeCreate, db: Session = Depends(get_db)):
    
    try:

        # si alguno de los campos requeridos no esta, levanto la exceepcion y devuelvo un error 422
        if not isinstance(request, NodeCreate):
            raise ValueError("Missing required fields: name, host, and port are required")
        

        # verifico que no exista otro nodo con el mismo nombre
        node = db.query(Node).filter(Node.name == request.name).first()

        if node:
            if node.status == "active":
                raise ValueError(f"Node with name '{request.name}' already exists")

            # reactivo el nodo inactivo en lugar de crear uno nuevo
            node.host = request.host
            node.port = request.port
            node.status = "active"
            node.updated_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(node)
            http_status = status.HTTP_201_CREATED
            return Response(
                content=json.dumps({
                    "id": node.id,
                    "name": node.name,
                    "host": node.host,
                    "port": node.port,
                    "status": node.status,
                    "created_at": node.created_at.isoformat(),
                    "updated_at": node.updated_at.isoformat(),
                }),
                media_type="application/json",
                status_code=http_status
            )


        node = Node(
            name=request.name,
            host=request.host,
            port=request.port,
            status="active",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        db.add(node)
        db.commit()
        db.refresh(node)

        http_status = status.HTTP_201_CREATED


        return Response(
        content=json.dumps({
            "id": node.id,
            "name": node.name,
            "host": node.host,
            "port": node.port,
            "status": node.status,
            "created_at": node.created_at.isoformat(),
            "updated_at": node.updated_at.isoformat(),
        }),
        media_type="application/json",
        status_code=http_status
    )
        
    except ValueError as e:
            # devuelvo 409 Conflict si el nodo ya existe o 422 Unprocessable Entity si faltan campos requeridos
            if "already exists" in str(e):
                http_status = status.HTTP_409_CONFLICT
            else:
                http_status = status.HTTP_422_UNPROCESSABLE_ENTITY
            
            return Response(
                content=json.dumps({"detail": str(e)}), 
                media_type="application/json",
                status_code=http_status
            )


@app.get("/api/nodes")
def list_nodes(db: Session = Depends(get_db)):

    nodes_list = []

    try:
        
        nodes = db.query(Node).all()

        for node in nodes:
            nodes_list.append({
                "id": node.id,
                "name": node.name,
                "host": node.host,
                "port": node.port,
                "status": node.status,
                "created_at": node.created_at.isoformat(),
                "updated_at": node.updated_at.isoformat(),
            })
    except Exception as e:
        return Response(
            content=json.dumps({"detail": "Error fetching nodes from database"}), 
            media_type="application/json",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    return Response(
        content=json.dumps(nodes_list), 
        media_type="application/json",
        status_code=status.HTTP_200_OK
    )


@app.get("/api/nodes/{name}")
def get_node(name: str, db: Session = Depends(get_db)):
    
    try:

        node = db.query(Node).filter(Node.name == name, Node.status == "active").first()
        if not node:
            raise ValueError("Node not found")
        
        # uso el schema NodeResponse para formatear la respuesta

        node_response = NodeResponse(
            id=node.id,
            name=node.name,
            host=node.host,
            port=node.port,
            status=node.status,
            created_at=node.created_at,
            updated_at=node.updated_at
        )
        

        return Response(
            content=node_response.model_dump_json(),
            media_type="application/json",
            status_code=status.HTTP_200_OK
        )

    except Exception as e:
        return Response(
            content=json.dumps({"detail": "Node not found"}), 
            media_type="application/json",
            status_code=status.HTTP_404_NOT_FOUND
        )


@app.put("/api/nodes/{name}")
def update_node(name: str, request: NodeUpdate, db: Session = Depends(get_db)):
    
    try:

        if not isinstance(request, NodeUpdate):
            raise ValueError("Invalid request body: expected NodeUpdate schema")

        node = db.query(Node).filter(Node.name == name, Node.status == "active").first()
        if not node:
            raise ValueError("Node not found")
        
        # actualizo solo los campos que vienen en el request, si no vienen, mantengo el valor actual del nodo
        node.name = request.name if request.name is not None else node.name
        node.host = request.host if request.host is not None else node.host
        node.port = request.port if request.port is not None else node.port
        node.updated_at = datetime.now(timezone.utc)
        
        db.commit()
        db.refresh(node)

        # uso el schema NodeResponse para formatear la respuesta
        node_response = NodeResponse(
            id=node.id,
            name=node.name,
            host=node.host,
            port=node.port,
            status=node.status,
            created_at=node.created_at,
            updated_at=node.updated_at
        )
        

        return Response(
            content=node_response.model_dump_json(),
            media_type="application/json",
            status_code=status.HTTP_200_OK
        )

    except Exception as e:

        if "Invalid request body" in str(e):
            http_status = status.HTTP_422_UNPROCESSABLE_ENTITY
        else:
            http_status = status.HTTP_404_NOT_FOUND
            
        return Response(
            content=json.dumps({"detail": str(e)}), 
            media_type="application/json",
            status_code=http_status
        )
    

@app.delete("/api/nodes/{name}")
def delete_node(name: str, db: Session = Depends(get_db)):
    
    try:

        node = db.query(Node).filter(Node.name == name, Node.status == "active").first()
        if not node:
            raise ValueError("Node not found")

        node.status = "inactive"
        node.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(node)

        return Response(status_code=status.HTTP_204_NO_CONTENT)
        

    except Exception as e:
        return Response(
            content=json.dumps({"detail": "Node not found"}), 
            media_type="application/json",
            status_code=status.HTTP_404_NOT_FOUND
        )
    

def getNodeCount(db: Session):

    nodes_count = -1
    try: 
        nodes_count = db.query(Node).filter(Node.status == "active").count()
        
    except Exception as e:
        print("Error updating nodes count:", str(e))

    return nodes_count