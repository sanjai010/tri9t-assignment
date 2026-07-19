from app.parser.pdf_parser import parse_pdf

nodes = parse_pdf("data/ct200_manual.pdf")

print(f"Total sections found: {len(nodes)}")
print("\n--- All sections ---")
for node in nodes:
    indent = "  " * (node["level"] - 1)
    print(f"{indent}[{node['section_number']}] {node['heading'][:50]} | parent={node['parent_id']}")