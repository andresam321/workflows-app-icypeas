from workflows_cdk import Response, Request
from flask import request as flask_request
import requests
import os
from main import router
import json

def extract_api_key(api_connection: dict) -> str:
    if not api_connection:
        return None
    return api_connection.get("connection_data", {}).get("value", {}).get("api_key_bearer")

@router.route("/execute", methods=["GET", "POST"])
def execute():
    request = Request(flask_request)
    data = request.data

    job_id_raw = data.get("job_id", "").strip()
    bulk_search = data.get("bulk_search", False)

    if not job_id_raw:
        return Response(
            data={"error": "No job ID provided."},
            metadata={"status": "failed"}
        )

    # Choose the correct URL and payload
    if bulk_search:
        url = "https://app.icypeas.com/api/search-files/read"
        payload = {"file": job_id_raw}
    else:
        url = "https://app.icypeas.com/api/bulk-single-searchs/read"
        payload = {"id": job_id_raw}

    headers = {
        "Authorization": extract_api_key(data.get("api_connection")),
        "Content-Type": "application/json"
    }

    print(f"Requesting results for: {job_id_raw}")
    print(f"Payload: {payload}")
    print(f"Headers: {headers}")

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        json_data = response.json()
        return Response(data=json_data, metadata={"status": "success"})
    except requests.RequestException as e:
        return Response(data={"error": str(e)}, metadata={"status": "failed"})
    except Exception as e:
        return Response(data={"error": str(e)}, metadata={"status": "failed"})


# @router.route("/content", methods=["GET", "POST"])
# def content():
#     request = Request(flask_request)
#     data = request.data

#     form_data = data.get("form_data", {})
#     print(f"Received content request with form_data: {form_data}")
#     content_object_names = data.get("content_object_names", [])
#     print(f"Received content request with form_data: {form_data} and content_object_names: {content_object_names}")
#     # Normalize content_object_names if needed
#     if isinstance(content_object_names, list) and content_object_names and isinstance(content_object_names[0], dict):
#         content_object_names = [obj.get("id") for obj in content_object_names if "id" in obj]

#     content_objects = []

#     # Handle show/hide logic based on selected search_type
#     for name in content_object_names:
#         if name == "show_if_single":
#                 content_objects.append({
#                     "content_object_name": "show_if_single",
#                     "data": [{"value": "true", "label": "Show single_id field"}]
#                 })
#         elif name == "show_if_bulk":
#                 content_objects.append({
#                     "content_object_name": "show_if_bulk",
#                     "data": [{"value": "true", "label": "Show bulk_file field"}]
#                 })

#     return Response(data={"content_objects": content_objects})
