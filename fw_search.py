import flywheel
import os
from dotenv import load_dotenv

def find_file_in_subject(
    fw_client: flywheel.Client,
    project_label: str,
    subject_label: str,
    filename: str,
):
    """Find a file inside a specific Project and Subject container.

    :param fw_client: Initialized Flywheel Client
    :param project_label: Name of the Flywheel project
    :param subject_label: Code/ID of the Subject
    :param filename: Exact target filename
    """
    try:
        # Resolve project and subject directly via SDK pathing
        project = fw_client.projects.find_first(f'label == "{project_label}"')
        if not project:
            return None

        subject = fw_client.subjects.find_first(
            f'project == "{project.id}" and label == "{subject_label}"'
        )
        if not subject:
            return None

        # Search sessions/acquisitions under this subject for the target file
        for session in subject.sessions():
            # Check session-level files
            for f in session.files:
                if f.name == filename:
                    return {
                        "file_id": f.id,
                        "file_name": f.name,
                        "parent_type": "session",
                        "session_label": session.label,
                    }

            # Check acquisition-level files
            for acq in session.acquisitions():
                for f in acq.files:
                    if f.name == filename:
                        return {
                            "file_id": f.id,
                            "file_name": f.name,
                            "parent_type": "acquisition",
                            "session_label": session.label,
                            "acquisition_label": acq.label,
                        }

        return None

    except flywheel.ApiException as e:
        print(f"Error querying Flywheel: {e}")
        return None

def test(client,project_label="", subject_label="", filename=""):
    out = find_file_in_subject(
            client,
            project_label,
            subject_label,
            filename)
    print(out)
    return 0
if __name__ == "__main__":
    load_dotenv()

# Initialize Flywheel Client
    api_key = os.getenv("FLYWHEEL_API_KEY")
    if not api_key:
        raise ValueError(
            "FLYWHEEL_API_KEY not found. Ensure your .env file is configured."
        )

    fw = flywheel.Client(api_key)
    print(f"Connected to Flywheel as: {fw.get_current_user().email}")
    test(fw,project_label="OCT_GA_GSK",subject_label="084614-001302",filename="00000045.nrrd")
