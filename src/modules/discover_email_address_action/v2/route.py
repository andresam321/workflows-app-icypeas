from workflows_cdk import Response, Request
from flask import request as flask_request
from main import router
import os
import requests
import json
from dotenv import load_dotenv
load_dotenv()

@router.route("/execute", methods=["GET", "POST"])
def execute():
    request = Request(flask_request)
    data = request.data
    # data = flask_request.get_json(force=True)
    api_key = data.get("api_connection", {}).get("connection_data", {}).get("value") or os.getenv("ICYPEAS_API_KEY")
    
    task = data.get("task", "email-search")
    name = data.get("name", "Bulk Search")
    bulk_data = data.get("data", [])
    
    url = "https://app.icypeas.com/api/bulk-search"
    payload = {
        "task": task,
        "name": name,
        "data": bulk_data
    }
    
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print(f"Headers: {headers}")
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        # Return the bulk job ID
        if result.get("success"):
            return Response(
                data={
                    "job_id": result.get("file"),
                    "name": name,
                    "task": task,
                    "total_items": len(bulk_data)
                },
                metadata={"status": "success"}
            )
        else:
            return Response(
                data={"error": "Failed to initiate bulk search"},
                metadata={"status": "failed"}
            )
            
    except requests.exceptions.RequestException as e:
        return Response(
            data={"error": str(e)},
            metadata={"status": "failed"}
        )

# @router.route("/content", methods=["GET", "POST"])
# def content():
#     """
#     This is the function that goes and fetches the necessary data to populate the possible choices in dynamic form fields.
#     For example, if you have a module to delete a contact, you would need to fetch the list of contacts to populate the dropdown
#     and give the user the choice of which contact to delete.

#     An action's form may have multiple dynamic form fields, each with their own possible choices. Because of this, in the /content route,
#     you will receive a list of content_object_names, which are the identifiers of the dynamic form fields. A /content route may be called for one or more content_object_names.

#     Every data object takes the shape of:
#     {
#         "value": "value",
#         "label": "label"
#     }
    
#     Args:
#         data:
#             form_data:
#                 form_field_name_1: value1
#                 form_field_name_2: value2
#             content_object_names:
#                 [
#                     {   "id": "content_object_name_1"   }
#                 ]
#         credentials:
#             connection_data:
#                 value: (actual value of the connection)

#     Return:
#         {
#             "content_objects": [
#                 {
#                     "content_object_name": "content_object_name_1",
#                     "data": [{"value": "value1", "label": "label1"}]
#                 },
#                 ...
#             ]
#         }
#     """
#     request = Request(flask_request)

#     data = request.data

#     form_data = data.get("form_data", {})
#     content_object_names = data.get("content_object_names", [])
    
#     # Extract content object names from objects if needed
#     if isinstance(content_object_names, list) and content_object_names and isinstance(content_object_names[0], dict):
#         content_object_names = [obj.get("id") for obj in content_object_names if "id" in obj]

#     content_objects = [] # this is the list of content objects that will be returned to the frontend

#     for content_object_name in content_object_names:
#         if content_object_name == "requested_content_object_1":
#             # logic here
#             data = [
#                 {"value": "value1", "label": "label1"},
#                 {"value": "value2", "label": "label2"}
#             ]
#             content_objects.append({
#                     "content_object_name": "requested_content_object_1",
#                     "data": data
#                 })
#         elif content_object_name == "requested_content_object_2":
#             # logic here
#             data = [
#                 {"value": "value1", "label": "label1"},
#                 {"value": "value2", "label": "label2"}
#             ]
#             content_objects.append({
#                     "content_object_name": "requested_content_object_2",
#                     "data": data
#                 })
    
#     return Response(data={"content_objects": content_objects})
