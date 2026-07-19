from app.models.database import SessionLocal, init_db, Document, DocumentVersion, Node
from app.parser.pdf_parser import parse_pdf


def ingest(pdf_path: str, doc_name: str = "CT-200 Manual"):
    init_db()
    db = SessionLocal()

    # Get or create document
    doc = db.query(Document).filter(Document.name == doc_name).first()
    if not doc:
        doc = Document(name=doc_name)
        db.add(doc)
        db.commit()
        db.refresh(doc)

    # Version number = how many versions exist + 1
    version_number = len(doc.versions) + 1
    version = DocumentVersion(
        document_id=doc.id,
        version_number=version_number,
        pdf_path=pdf_path
    )
    db.add(version)
    db.commit()
    db.refresh(version)

    # Parse PDF and save all nodes
    nodes = parse_pdf(pdf_path)
    for n in nodes:
        node = Node(
            version_id=version.id,
            section_number=n["section_number"],
            heading=n["heading"],
            level=n["level"],
            body=n["body"],
            parent_id=n["parent_id"],
            content_hash=n["content_hash"]
        )
        db.add(node)

    db.commit()
    db.close()
    print(f"✅ Ingested version {version_number} — {len(nodes)} nodes saved")


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "data/ct200_manual.pdf"
    ingest(path)