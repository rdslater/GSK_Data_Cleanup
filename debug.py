import os
from dotenv import load_dotenv
import flywheel

load_dotenv()
fw = flywheel.Client(os.getenv("FLYWHEEL_API_KEY"))

# --- REPLACE THESE WITH YOUR KNOWN VALUES ---
KNOWN_PROJECT = 'OCT_GA_GSK'
KNOWN_SUBJECT = "084614-001302"
KNOWN_FILENAME = "00000045.nrrd"


def debug_flywheel_lookup(
    project_label: str, subject_label: str, target_filename: str
):
    print("=== FLYWHEEL DIAGNOSTIC RUN ===")

    # 1. Test Project Existence
    print(f"\n1. Looking for Project: '{project_label}'...")
    project = fw.projects.find_first("label='OCT_GA_GSK'")
    if not project:
        print(
            "   ❌ PROJECT NOT FOUND. Available projects you have access to:"
        )
        for p in fw.projects():
            print(f"      - '{p.label}' (ID: {p.id})")
        return
    print(f"   ✓ Found Project ID: {project.id}")

    # 2. Test Subject Existence under Project
    print(
        f"\n2. Looking for Subject: '{subject_label}' inside Project '{project_label}'..."
    )
    subject = fw.subjects.find_first(f"label='{subject_label}'")
    if not subject:
        print(
            "   ❌ SUBJECT NOT FOUND in this project. Available subjects in this project (first 10):"
        )
        for s in project.subjects()[:10]:
            print(f"      - '{s.label}' (ID: {s.id})")
        return
    print(f"   ✓ Found Subject ID: {subject.id}")

    # 3. Direct Hierarchy Traversal (Bypasses Search Index)
    print("\n3. Scanning Sessions and Acquisitions directly (No Search Engine)...")
    found_via_sdk = False
    all_files_found = []

    for session in subject.sessions():
        # Check session-level files
        for f in session.files:
            all_files_found.append(f.name)
            if f.name == target_filename:
                print(
                    f"   ✓ FOUND FILE at Session level! (Session: {session.label})"
                )
                found_via_sdk = True

        # Check acquisition-level files
        for acq in session.acquisitions():
            for f in acq.files:
                all_files_found.append(f.name)
                if f.name == target_filename:
                    print(
                        f"   ✓ FOUND FILE at Acquisition level! (Acquisitions: {acq.label})"
                    )
                    found_via_sdk = True

    if not found_via_sdk:
        print(f"   ❌ File '{target_filename}' NOT found via direct traversal.")
        print(
            f"   ℹ️ Actual files found under Subject '{subject_label}' ({len(all_files_found)} total):"
        )
        for f_name in all_files_found[:15]:  # Show first 15 files
            print(f"      - {f_name}")

    # 4. Test Search API Query Syntax
    print("\n4. Testing `fw.search()` query execution...")
    exact_query = f"project.label == '{project_label}' AND subject.label == '{subject_label}' AND file.name == '{target_filename}'"
    print(f"   Query: {exact_query}")

    search_results = fw.search(
        {"key": "file", "query": exact_query, "return_type": "file"}
    )
    if search_results:
        print(
            f"   ✓ Search API successfully returned {len(search_results)} match(es)."
        )
    else:
        print("   ❌ Search API returned 0 results.")
        if found_via_sdk:
            print(
                "   ⚠️ CAUTION: File exists on disk but Search Index hasn't indexed it yet (or query field key mismatch)."
            )


if __name__ == "__main__":
    debug_flywheel_lookup(KNOWN_PROJECT, KNOWN_SUBJECT, KNOWN_FILENAME)
