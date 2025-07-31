from workflows_cdk import Request, Response
from flask import request as flask_request
from main import router
import requests
import os

@router.route("/execute", methods=["POST", "GET"])
def execute():
    """
    Search for people in the Icypeas Lead Database.
    Supports Include/Exclude filters such as firstname, lastname, currentJobTitle, etc.
    """
    request = Request(flask_request)
    data = request.data
    # data = flask_request.get_json(force=True)
    # Get API key from connection or environment
    api_key = data.get("api_connection", {}).get("connection_data", {}).get("value") or os.getenv("ICYPEAS_API_KEY")

    if not api_key:
        return Response(
            data={"error": "API key not provided"},
            metadata={"status": "failed", "code": 401}
        )

    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }
    print("Headers:", headers)
    try:
        # Build the query filters using all supported fields
        query_filters = {
            "firstname": data.get("firstname"),
            "lastname": data.get("lastname"),
            "currentJobTitle": data.get("currentJobTitle"),
            "pastJobTitle": data.get("pastJobTitle"),
            "currentCompanyName": data.get("currentCompanyName"),
            "pastCompanyName": data.get("pastCompanyName"),
            "currentCompanyUrn": data.get("currentCompanyUrn"),
            "pastCompanyUrn": data.get("pastCompanyUrn"),
            "school": data.get("school"),
            "languages": data.get("languages"),
            "skills": data.get("skills"),
            "location": data.get("location"),
            "keyword": data.get("keyword")
        }
        print("Query Filters:", query_filters)
        query = {k: v for k, v in query_filters.items() if v is not None}

        if not query:
            return Response(
                data={"error": "At least one query filter must be provided."},
                metadata={"status": "failed", "code": 400}
            )

        # Assemble final search payload
        search_params = {
            "query": query,
            "limit": data.get("limit", 100),
            "offset": data.get("offset", 0)
        }

        # Make the API request
        url = "https://app.icypeas.com/api/lead-database/find-people"
        response = requests.post(url, json=search_params, headers=headers, timeout=30)
        response.raise_for_status()

        result = response.json()
        print("API Response:", result)
        # Check if the response indicates success
        if result.get("success", False):
            if result.get("_id") or result.get("job_id"):
                return Response(
                    data={
                        "job_id": result.get("_id") or result.get("job_id"),
                        "message": "Search initiated. Use the job ID to retrieve results.",
                        "search_criteria": query
                    },
                    metadata={"status": "processing"}
                )
            else:
                people = result.get("results", [])
                return Response(
                    data={
                        "total_found": result.get("total", len(people)),
                        "limit": search_params["limit"],
                        "offset": search_params["offset"],
                        "people": people,
                        "search_criteria": query
                    },
                    metadata={"status": "success"}
                )
        else:
            return Response(
                data={"error": "Search failed", "details": result},
                metadata={"status": "failed"}
            )

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return Response(
                data={
                    "error": "Lead Database endpoint not found",
                    "message": "The Lead Database feature may require special access or API activation. Please contact Icypeas support.",
                    "attempted_url": url
                },
                metadata={"status": "failed", "code": 404}
            )
        else:
            return Response(
                data={
                    "error": f"HTTP error: {e.response.status_code}",
                    "details": e.response.text
                },
                metadata={"status": "failed", "code": e.response.status_code}
            )
    except requests.exceptions.RequestException as e:
        return Response(
            data={"error": f"Request failed: {str(e)}"},
            metadata={"status": "failed", "code": 500}
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
