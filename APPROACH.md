# Approach Document — CT-200 Document API

## 1. PDF Parsing Approach

I used pdfplumber to extract text from the CT-200 PDF because it 
preserves text order and works well with structured documents.

I detect headings using regex pattern matching — any line starting 
with a number pattern like "1.", "2.1", "3.4.1" is treated as a heading.
Body text is everything between headings.

### Structural inconsistencies I found:
- Section 3.3 appears AFTER 3.4 in the PDF — I preserve PDF order intentionally
- Section 2.1.1.1 skips two hierarchy levels (no 2.1.1 exists)
- "Error Codes" heading appears twice (sections 4.2 and 7.1)
- Numbered list items (1. Normal, 2. Elevated) were falsely detected as headings

### How I fixed them:
- Out-of-order: preserved as-is, noted in tests
- Skipped levels: walk backwards to find nearest ancestor
- Duplicate headings: both kept as distinct nodes with different IDs
- False headings: added word count and capital letter check to filter them

## 2. Hierarchy Reconstruction

Each node stores: section_number, heading, level, body, parent_id, content_hash.

Level is determined by counting dots in section number.
"3.2" = level 2, "2.1.1.1" = level 4.

Parent is found by progressively shortening the section number
until a match is found in previous nodes.

## 3. Versioning Strategy

I use path-based matching — nodes are matched across versions 
by their section_number (e.g. "3.2" in v1 matches "3.2" in v2).

Content hash (MD5) is compared to detect changes.

### Known failure modes:
- If a section is renumbered (e.g. 3.2 becomes 3.3), it won't match
- A one-word change gets the same treatment as a safety-critical change
- MD5 is not semantic — it cannot tell if a change is significant

## 4. LLM Prompt Design (planned)

Not implemented in this submission. Would use Groq free tier with 
structured JSON output and retry logic for malformed responses.

## 5. Decision Log

**Q1: What's most likely to silently give wrong results?**
The parent assignment for skipped levels. If a section number 
has no ancestor at all, parent_id is None and no error is raised.
I would catch this with a validation script that checks all nodes 
with dots in their section_number have a non-None parent_id.

**Q2: Where did I choose simplicity over correctness?**
Version matching by section_number breaks if sections are renumbered.
In production I would use fuzzy title matching as a fallback.

**Q3: One input I did not handle:**
A PDF with scanned images instead of real text. pdfplumber returns 
empty strings for image-based pages. My parser silently skips them.