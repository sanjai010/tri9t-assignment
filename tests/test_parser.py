from app.parser.pdf_parser import parse_pdf, is_heading, get_level, get_section_number

# ── Test 1: Out-of-order sections (3.4 appears before 3.3 in PDF) ──
def test_out_of_order_sections():
    nodes = parse_pdf("data/ct200_manual.pdf")
    section_nums = [n["section_number"] for n in nodes]
    
    idx_33 = section_nums.index("3.3")
    idx_34 = section_nums.index("3.4")
    
    # 3.4 appears BEFORE 3.3 in the PDF — parser must preserve this
    assert idx_34 < idx_33, "3.4 should appear before 3.3 (PDF order preserved)"
    print("✅ Test 1 passed: out-of-order 3.3/3.4 preserved correctly")


# ── Test 2: Skipped hierarchy level (2.1.1.1 has no 2.1.1 parent) ──
def test_skipped_level_parent():
    nodes = parse_pdf("data/ct200_manual.pdf")
    
    node_2111 = next(n for n in nodes if n["section_number"] == "2.1.1.1")
    node_21 = next(n for n in nodes if n["section_number"] == "2.1")
    
    # 2.1.1.1 should be parented to 2.1 (nearest ancestor)
    assert node_2111["parent_id"] == node_21["id"], \
        f"2.1.1.1 should have parent 2.1 (id={node_21['id']}), got {node_2111['parent_id']}"
    print("✅ Test 2 passed: skipped level 2.1.1.1 correctly parented to 2.1")


# ── Test 3: Duplicate heading produces two distinct nodes ──
def test_duplicate_heading_distinct_nodes():
    nodes = parse_pdf("data/ct200_manual.pdf")
    
    error_code_nodes = [n for n in nodes if "Error Codes" in n["heading"]]
    
    # Both 4.2 and 7.1 are named "Error Codes"
    assert len(error_code_nodes) == 2, \
        f"Expected 2 'Error Codes' nodes, found {len(error_code_nodes)}"
    
    ids = [n["id"] for n in error_code_nodes]
    assert ids[0] != ids[1], "Duplicate headings must have distinct IDs"
    
    parents = [n["parent_id"] for n in error_code_nodes]
    assert parents[0] != parents[1], "Duplicate headings must have different parents"
    print("✅ Test 3 passed: duplicate 'Error Codes' heading = 2 distinct nodes with different parents")


if __name__ == "__main__":
    test_out_of_order_sections()
    test_skipped_level_parent()
    test_duplicate_heading_distinct_nodes()
    print("\n✅ All 3 tests passed!")