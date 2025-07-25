from workflows_cdk import Response, Request
from flask import request as flask_request
from main import router
import os
import requests
from workflows_cdk.core.errors import ManagedError
import time
import json
from dotenv import load_dotenv
load_dotenv()
# @router.route("/ping", methods=["GET", "POST"])
# def ping():
#     """
#     This is a simple ping endpoint to check if the module is working.
#     """
    
#     return Response(data={"message": "pong"}, metadata={"affected_rows": 0})
# @router.route("/env-check", methods=["GET"])
# def env_check():
#     api_key = os.getenv("NEVERBOUNCE_API_KEY")
#     return Response(data={"NEVERBOUNCE_API_KEY": api_key}, metadata={"affected_rows": 0})

@router.route("/execute", methods=["POST", "GET"])
def execute():
    data = flask_request.get_json(force=True)

    firstname = data.get("firstname")
    lastname = data.get("lastname")
    domain_or_company = data.get("domainOrCompany")

    api_key = os.getenv("ICYPEAS_API_KEY", "").strip()
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }

    # Submit email-search job
    payload = {
        "firstname": firstname,
        "lastname": lastname,
        "domainOrCompany": domain_or_company
    }

    create_response = requests.post(
        "https://app.icypeas.com/api/email-search",
        headers=headers,
        json=payload
    )

    if create_response.status_code != 200:
        return Response(data={
            "success": False,
            "message": "Failed to create email search job",
            "status_code": create_response.status_code,
            "response": create_response.text
        })

    create_data = create_response.json()

    # Handle invalid input (e.g., user not found)
    if create_data.get("error") == "UserNotFoundError":
        return Response(data={
            "success": False,
            "message": "User not found — check name or domain.",
            "code": create_data.get("code")
        })

    job_id = create_data["item"]["_id"]

    return Response(data={
        "success": True,
        "job_id": job_id,
        "status": "pending",
        "note": "Call again with this job_id to fetch the result later."
    })

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
