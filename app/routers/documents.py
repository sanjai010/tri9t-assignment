from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.database import get_db, Node, DocumentVersion, Document

router = APIRouter()


@router.get("/sections")
def get_sections(version: int = None, db: Session = Depends(get_db)):
    """Get all top-level sections for a version (default = latest)"""
    if version is None:
        v = db.query(DocumentVersion).order_by(DocumentVersion.version_number.desc()).first()
    else:
        v = db.query(DocumentVersion).filter(DocumentVersion.version_number == version).first()

    if not v:
        raise HTTPException(status_code=404, detail="Version not found")

    nodes = db.query(Node).filter(
        Node.version_id == v.id,
        Node.level == 1
    ).all()

    return {
        "version": v.version_number,
        "sections": [
            {
                "id": n.id,
                "section_number": n.section_number,
                "heading": n.heading,
                "level": n.level,
                "content_hash": n.content_hash
            }
            for n in nodes
        ]
    }


@router.get("/nodes/{node_id}")
def get_node(node_id: int, db: Session = Depends(get_db)):
    """Get a specific node with its children"""
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    children = db.query(Node).filter(
        Node.version_id == node.version_id,
        Node.parent_id == node.id
    ).all()

    return {
        "id": node.id,
        "section_number": node.section_number,
        "heading": node.heading,
        "level": node.level,
        "body": node.body,
        "content_hash": node.content_hash,
        "parent_id": node.parent_id,
        "children": [
            {
                "id": c.id,
                "section_number": c.section_number,
                "heading": c.heading,
                "content_hash": c.content_hash
            }
            for c in children
        ]
    }


@router.get("/search")
def search(q: str, db: Session = Depends(get_db)):
    """Search nodes by heading or body text"""
    results = db.query(Node).filter(
        (Node.heading.contains(q)) | (Node.body.contains(q))
    ).all()

    return {
        "query": q,
        "results": [
            {
                "id": n.id,
                "section_number": n.section_number,
                "heading": n.heading,
                "body": n.body[:200]
            }
            for n in results
        ]
    }


@router.get("/nodes/{node_id}/diff")
def diff_node(node_id: int, db: Session = Depends(get_db)):
    """Check if a node changed between versions"""
    node = db.query(Node).filter(Node.id == node_id).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    # Find same section in other version
    other = db.query(Node).filter(
        Node.section_number == node.section_number,
        Node.version_id != node.version_id
    ).first()

    if not other:
        return {"changed": None, "message": "Section not found in other version"}

    changed = node.content_hash != other.content_hash
    return {
        "section_number": node.section_number,
        "changed": changed,
        "current_hash": node.content_hash,
        "other_hash": other.content_hash,
        "message": "Content changed between versions" if changed else "Content identical"
    }