import pdfplumber
import hashlib
import re
from pathlib import Path

# This function creates a unique fingerprint for any text
# If the text changes even slightly, the hash changes
# This is how we detect "stale" test cases later
def make_hash(text: str) -> str:
    return hashlib.md5(text.strip().encode()).hexdigest()


# This function checks if a line is a section heading
# Examples it should match: "1.", "2.1", "3.4.1", "2.1.1.1"
def is_heading(text: str) -> bool:
    # Must start with a number followed by dot and space and real heading word
    # Excludes single numbers like "1. Normal" which are list items
    # Real headings have a capitalized word after the number
    pattern = r'^\d+(\.\d+)+\.?\s+[A-Z]'
    simple = r'^\d+\.\s+[A-Z][a-z]+\s+[A-Z]'
    
    # Reject if it's a short numbered list item (less than 4 words typically)
    stripped = text.strip()
    word_count = len(stripped.split())
    
    # Top level sections like "1. Device Overview" - must have few words and capital start
    top_level = re.match(r'^\d+\.\s+[A-Z]', stripped)
    sub_level = re.match(r'^\d+(\.\d+)+\.?\s+[A-Z]', stripped)
    
    if sub_level:
        return True
    if top_level and word_count <= 5:
        return True
    return False

# This extracts the section number from a heading
# "3.2 Cuff Inflation Sequence" → returns "3.2"
def get_section_number(text: str) -> str:
    match = re.match(r'^(\d+(\.\d+)*)', text.strip())
    return match.group(1) if match else ""


# This calculates heading level from section number
# "1" → level 1,  "2.1" → level 2,  "3.4.1" → level 3
def get_level(section_num: str) -> int:
    if not section_num:
        return 0
    return len(section_num.split("."))
def parse_pdf(pdf_path: str) -> list:
    """
    Opens a PDF and extracts all sections as a list of nodes.
    Each node is a dictionary with all the info about that section.
    """
    nodes = []
    current_node = None
    node_id = 0

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue

            lines = text.split("\n")

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                if is_heading(line):
                    # Save the previous node before starting a new one
                    if current_node:
                        nodes.append(current_node)

                    section_num = get_section_number(line)
                    level = get_level(section_num)
                    node_id += 1

                    current_node = {
                        "id": node_id,
                        "section_number": section_num,
                        "heading": line,
                        "level": level,
                        "body": "",
                        "parent_id": None,
                        "content_hash": ""
                    }

                else:
                    # This line is body text — add it to current node
                    if current_node:
                        current_node["body"] += line + " "

        # Don't forget the last node on the last page
        if current_node:
            nodes.append(current_node)

    # Now generate hash for each node and assign parent IDs
    for node in nodes:
        node["content_hash"] = make_hash(node["body"])

    nodes = assign_parents(nodes)
    return nodes

def assign_parents(nodes: list) -> list:
    """
    Figures out parent by walking backwards to find
    any ancestor — handles skipped levels like 2.1.1.1
    """
    for i, node in enumerate(nodes):
        sec = node["section_number"]
        if "." not in sec:
            node["parent_id"] = None
        else:
            parts = sec.split(".")
            # Try progressively shorter parent paths
            found = False
            for length in range(len(parts) - 1, 0, -1):
                parent_num = ".".join(parts[:length])
                for prev in nodes[:i]:
                    if prev["section_number"] == parent_num:
                        node["parent_id"] = prev["id"]
                        found = True
                        break
                if found:
                    break

    return nodes