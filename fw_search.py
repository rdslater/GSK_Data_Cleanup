import flywheel
import os
from dotenv import load_dotenv
import pandas as pd
import re

def find_file_in_subject(
    fw_client: flywheel.Client,
    project_label: str,
    subject_label: str,
    filename_pattern: str,
):
    """Find a file inside a specific Project and Subject container.

    :param fw_client: Initialized Flywheel Client
    :param project_label: Name of the Flywheel project
    :param subject_label: Code/ID of the Subject
    :param filename_pattern: Search pattern for file (regex)
    """
    try:
        # Resolve project and subject directly via SDK pathing
        pattern = re.compile(filename_pattern, re.IGNORECASE)
        project = fw_client.projects.find_first(f'label="{project_label}"')
        if not project:
            return None
        subject = project.subjects.find_first(
           f'label="{subject_label}"'
        )
        if not subject:
            return None

        # Search sessions/acquisitions under this subject for the target file
        for session in subject.sessions():
            for acq in session.acquisitions():
                for f in acq.files:
                    if pattern.search(f.name):
                        return {
                            "file_id": getattr(f, "id", None),
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
    data = load_xl("./GSK_EZRPE_missing.xlsx")
    item = (get_info(0,data))
    out = find_file_in_subject(
            client,
            project_label,
            subject_label,
            filename)
    print(out)
    return 0

def load_xl(file_path):
    data = pd.read_excel(file_path)
    return data

def get_info(row,dataFrame):
    values = dataFrame.iloc[row,:]
    return values


if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("FLYWHEEL_API_KEY")
    if not api_key:
        raise ValueError(
            "FLYWHEEL_API_KEY not found. Ensure your .env file is configured."
        )

    fw = flywheel.Client(api_key)
    print(f"Connected to Flywheel as: {fw.get_current_user().email}")
    data = load_xl("./GSK_EZRPE_missing.xlsx")
    data['MainFile'] = "NA"
    for i in range(data.shape[0]):
        item = get_info(i, data)
        file_pattern = item['EZ_FileName']
        #test(fw,project_label="OCT_GA_GSK",subject_label=item['Subject'],filename=item['EZ_FileName'])
        file = find_file_in_subject(
            fw,
            "OCT_GA_GSK",
            item['Subject'],
            file_pattern
            )
        if not file:
            print(f"Not found:{item['Subject']} : {item['EZ_FileName']}")
        else: 
            data.iloc[i,14] = file['file_id']

    data.to_csv("./test_output.csv")
