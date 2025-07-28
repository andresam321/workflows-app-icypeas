from workflows_cdk import Response, Request
from flask import request as flask_request
from main import router
import os
import requests
import json
from dotenv import load_dotenv
load_dotenv()

def extract_api_key(api_connection: dict) -> str:
    if not api_connection:
        return None
    return api_connection.get("connection_data", {}).get("value", {}).get("api_key_bearer")

@router.route("/execute", methods=["GET", "POST"])
def execute():
    request = Request(flask_request)
    data = request.data

    # api_key = data.get("api_connection", {}).get("connection_data", {}).get("value") or os.getenv("ICYPEAS_API_KEY")
    task = data.get("task", "email-search")
    name = data.get("name", "Bulk Search")
    data_raw = data.get("data", "[]")

    # Handle both stringified JSON and list input
    if isinstance(data_raw, str):
        try:
            bulk_data = json.loads(data_raw)
        except json.JSONDecodeError as e:
            return Response(
                data={"error": f"Invalid JSON in Task Search Data: {str(e)}"},
                metadata={"status": "failed"}
            )
    elif isinstance(data_raw, list):
        bulk_data = data_raw
    else:
        return Response(
            data={"error": "Invalid format: expected JSON string or list"},
            metadata={"status": "failed"}
        )

    # Validate bulk_data is a list of lists (nested)
    if not isinstance(bulk_data, list) or not all(isinstance(row, list) for row in bulk_data):
        return Response(
            data={"error": "Data must be a JSON array of arrays (e.g., [[\"example.com\"]])"},
            metadata={"status": "failed"}
        )

    # Prepare payload
    url = "https://app.icypeas.com/api/bulk-search"
    payload = {
        "task": task,
        "name": name,
        "data": bulk_data
    }

    headers = {
        "Authorization": extract_api_key(data.get("api_connection")),
        "Content-Type": "application/json"
    }

    # print(f"Payload: {json.dumps(payload, indent=2)}")
    # print(f"Headers: {headers}")

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")

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

@router.route("/content", methods=["GET", "POST"])
def content():
    request = Request(flask_request)
    data = request.data
    
    form_data = data.get("form_data", {})
    content_object_names = data.get("content_object_names", [])
    
    # Handle both list of strings and list of objects formats
    if isinstance(content_object_names, list) and content_object_names and isinstance(content_object_names[0], dict):
        content_object_names = [obj.get("id") for obj in content_object_names if "id" in obj]
    
    content_objects = []
    
    for content_object_name in content_object_names:
        print(f"Processing content object: {content_object_name}")
        if content_object_name == "data_example_dynamic":
            # Get the selected task from form data
            task = form_data.get("task")
            print(f"Selected task: {task}")
            # Define example JSON strings based on task
            if task == "email-search":
                example = '[["firstname", "lastname", "example.com"], ["Jane", "Smith", "test.org"], ["", "Johnson", "company.net"]]'
                label = "Ex: [Firstname, Lastname, Domain]"
            elif task == "email-verification":
                example = '[["john.doe@example.com"], ["jane.smith@test.org"], ["support@company.net"]]'
                label = "Ex: [Email Address]"
            elif task == "domain-search":
                example = '[["example.com"], ["test.org"], ["company.net"]]'
                label = "Ex: [Domain or Company Name]"
            else:
                # Default when no task is selected
                example = ''
                label = "Select a task to see example format"
            
            # Append the content object
            content_objects.append({
                "content_object_name": "example_data_dynamic",
                "data": [
                    {
                        "value": example
                    }
                ]
            })
    
    return Response(data={"content_objects": content_objects})