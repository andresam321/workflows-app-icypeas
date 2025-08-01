from workflows_cdk import Request, Response
from flask import request as flask_request
from main import router
import requests
import os

def extract_api_key(api_connection: dict) -> str:
    if not api_connection:
        return None
    return api_connection.get("connection_data", {}).get("value", {}).get("api_key_bearer")

@router.route("/execute", methods=["POST", "GET"])
def execute():
    """
    Scrape LinkedIn company page(s) to get company information using Icypeas API.
    Automatically detects whether to use single or bulk scraping based on input length.
    """
    request = Request(flask_request)
    data = request.data

    # Get API key from connection or environment
    api_key = extract_api_key(data.get("api_connection")) or os.getenv("ICYPEAS_API_KEY")
    if not api_key:
        return Response(
            data={"error": "API key not provided"},
            metadata={"status": "failed", "code": 401}
        )

    headers = {
        "Authorization": extract_api_key(data.get("api_connection")),
        "Content-Type": "application/json"
    }

    try:
        # Parse and clean company URL input
        raw_input = data.get("companies", "")
        url_list = [url.strip() for url in raw_input.replace("\n", ",").split(",") if url.strip()]

        if not url_list:
            return Response(
                data={"error": "No valid company URL(s) provided."},
                metadata={"status": "failed", "code": 400}
            )

        # Use single or bulk endpoint based on URL count
        if len(url_list) == 1:
            url = f"https://app.icypeas.com/api/scrape/company?url={url_list[0]}"
            response = requests.get(url, headers=headers)
        else:
            url = "https://app.icypeas.com/api/scrape"
            payload = {
                "type": "company",
                "data": url_list[:50]
            }
            response = requests.post(url, json=payload, headers=headers)

        response.raise_for_status()
        return Response(
            data=response.json(),
            metadata={"status": "success"}
        )

    except requests.exceptions.RequestException as e:
        return Response(
            data={"error": f"Request failed: {str(e)}"},
            metadata={"status": "failed", "code": getattr(e.response, 'status_code', 500)}
        )
    except Exception as e:
        return Response(
            data={"error": f"Unexpected error: {str(e)}"},
            metadata={"status": "failed", "code": 500}
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
