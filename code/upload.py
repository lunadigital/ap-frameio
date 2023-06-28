import anchorpoint as ap
import apsync as aps
import requests
import mimetypes
from copy import deepcopy

ctx = ap.get_context()
settings = aps.SharedSettings(ctx.workspace_id, "Frameio")
token = settings.get("token", "")

headers = {
    "Authorization": f"Bearer {token}",
}

def get_team_id():
    team_id = settings.get("team_id", "")

    if not team_id:
        response = requests.get(
            "https://api.frame.io/v2/teams/",
            headers=headers
        )

        if response.status_code == 200:
            data = response.json()[0]
            return data["id"]

        settings.store()
    
    return team_id

def get_projects(params={}):
    team_id = get_team_id()

    response = requests.get(
        f"https://api.frame.io/v2/teams/{team_id}/projects",
        headers=headers,
        params=params
    )

    if response.status_code == 200:   
        return [{"id": project["id"], "name": project["name"]} for project in response.json()]

    print("ERROR: No team id found.")
    return []

def upload(project_id, file_data):
    payload = {
        "name": file_data.name,
        "type": "file",
        "filetype": mimetypes.guess_type(file_data.path)
    }

    create_headers = deepcopy(headers)
    create_headers["Content-Type"] = "application/json"

    with open(file_data.path, 'rb') as file:
        response = requests.post(
            f"https://api.frame.io/v2/files/{project_id}",
            json=payload,
            headers=create_headers,
            file={"file": file}
        )

    if response.status_code == 200:
        print(f"{file_data.name} uploaded successfully!")
    else:
        print(f"There was a problem uploading {file_data.name}.")

if len(ctx.selected_files) > 0:
    ap_project = aps.get_project(ctx.path)
    project_settings = aps.Settings(identifier=ap_project.id)
    project_id = project_settings.get("frameio_id", "")

    if not project_id:
        # Frameio project id not associated in Anchorpoint, try to find
        # project based on name first
        frameio_project = get_projects({ "name": ap_project.name })

        if not frameio_project:
            # Then create a new project as a last resort
            print("Frameio project not found, creating...")

            payload = {
                "name": ap_project.name
            }

            create_headers = deepcopy(headers)
            create_headers["Content-Type"] = "application/json"

            team_id = get_team_id()

            response = requests.post(
                f"https://api.frame.io/v2/teams/{team_id}/projects",
                json=payload,
                headers=create_headers
            )

            if response.status_code == 200:
                project_id = response.json()[0]["id"]
        else:
            project_id = frameio_project[0]["id"]
        
        project_settings.set("frameio_id", project_id)
        project_settings.store()

    for f in ctx.selected_files:
        print(f"Uploading {f.name}...")
        ctx.run_async(upload, [project_id, f])