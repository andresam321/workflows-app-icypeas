from workflows_cdk import Response, Request
from flask import request as flask_request
import requests
import os
from main import router

@router.route("/execute", methods=["GET", "POST"])
def execute():
    request = Request(flask_request)
    data = request.data
    # data = flask_request.get_json(force=True)
    api_key = data.get("api_connection", {}).get("connection_data", {}).get("value") or os.getenv("ICYPEAS_API_KEY")
    
    job_id = data.get("id", "")
    is_bulk = data.get("file", False)
    
    # For single searches or bulk results
    url = "https://app.icypeas.com/api/bulk-single-searchs/read"
    
    payload = {}
    if is_bulk:
        payload["file"] = job_id  # For bulk searches, use file parameter
    else:
        payload["id"] = job_id    # For single searches, use id parameter
    
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }
    print(f"Requesting results for job_id: {job_id}, is_bulk: {is_bulk}")
    print(f"Payload: {payload}")
    print(f"Headers: {headers}")
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()
        
        if not result.get("success"):
            return Response(
                data={"error": "Failed to retrieve results"},
                metadata={"status": "failed"}
            )
        
        items = result.get("items", [])
        
        if not items:
            return Response(
                data={"message": "No results found yet"},
                metadata={"status": "still processing"}
            )
        
        # Check if all items are processed
        all_processed = True
        results = []
        
        for item in items:
            status = item.get("status", "NONE")
            
            # If any item is still processing
            if status in ["NONE", "SCHEDULED", "IN_PROGRESS"]:
                all_processed = False
                continue
            
            # Extract the results
            item_result = {
                "status": status,
                "order": item.get("order", 0),
                "results": item.get("results", {}),
                "external_id": item.get("userData", {}).get("externalId", "")
            }
            results.append(item_result)
        
        if not all_processed:
            return Response(
                data={
                    "processed": len(results),
                    "total": len(items),
                    "partial_results": results
                },
                metadata={"status": "still processing"}
            )
        
        # All items processed
        return Response(
            data={
                "total": len(items),
                "results": results
            },
            metadata={"status": "complete"}
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
