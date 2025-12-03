import httpx
from typing import Optional
from mcp.server import FastMCP



FASTAPI_BASE_URL = "http://localhost:8080"

mcp = FastMCP("todo-mcp-server")

async def make_api_request(method: str, endpoint: str, json_data: dict | None = None, params: dict | None = None):
    """Helper function to make HTTP requests to FastAPI"""
    async with httpx.AsyncClient() as client:
        url = f"{FASTAPI_BASE_URL}{endpoint}"
        print("Making requst to")
        print(url)
        try:
            if method == "GET":
                response = await client.get(url, params=params)
            elif method == "POST":
                response = await client.post(url, json=json_data)
            elif method == "PATCH":
                response = await client.patch(url, json=json_data)
            elif method == "DELETE":
                response = await client.delete(url)
            
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise Exception(f"API Error: {str(e)}")

@mcp.tool()
async def create_task(
    title: str,
    description: str,
    priority: str,
    due_by: Optional[str] = None
) -> str:
    """
    Create a new todo task.
    
    Args:
        title: The title of the task (max 64 characters)
        description: Detailed description of the task (max 255 characters)
        priority: Priority level - must be one of: urgent, high, medium, low
        due_by: Due date and time in ISO format (e.g., '2025-12-02T20:00:00'). Optional.
    
    Returns:
        A success message with the created task details
    """
    task_data = {
        "title": title,
        "description": description,
        "priority": priority
    }
    if due_by:
        task_data["due_by"] = due_by
    
    result = await make_api_request("POST", "/task", json_data=task_data)
    
    return (
        f">>> Task created successfully!\n\n"
        f"ID: {result['id']}\n"
        f"Title: {result['title']}\n"
        f"Status: {result['status']}\n"
        f"Priority: {result['priority']}\n"
        f"Due by: {result.get('due_by', 'Not set')}\n"
        f"Created at: {result['created_at']}"
    )

@mcp.tool()
async def get_tasks(
    search: Optional[str] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    due_date_from: Optional[str] = None,
    due_date_to: Optional[str] = None,
    sort_by: Optional[str] = "created_at",
    sort_order: Optional[str] = "desc",
    limit: Optional[int] = None
) -> str:
    """
    Search and filter todo tasks. Returns all matching tasks.
    
    Args:
        search: Search text across title and description
        title: Filter by title (partial match)
        description: Filter by description (partial match)
        status: Filter by task status - must be one of: pending, inprogress, completed
        priority: Filter by priority - must be one of: urgent, high, medium, low
        due_date_from: Filter tasks due after this date (ISO format)
        due_date_to: Filter tasks due before this date (ISO format)
        sort_by: Field to sort by - options: created_at, due_by, priority, title, status
        sort_order: Sort order - asc or desc
        limit: Maximum number of tasks to return
    
    Returns:
        A formatted list of matching tasks
    """
    params = {}
    for key, value in {
        "search": search,
        "title": title,
        "description": description,
        "status": status,
        "priority": priority,
        "due_by_from": due_date_from,
        "due_by_to": due_date_to,
        "sort_by": sort_by,
        "sort_order": sort_order,
        "limit": limit
    }.items():
        if value is not None:
            params[key] = value
    
    result = await make_api_request("GET", "/task", params=params)
    
    if not result:
        return "No tasks found matching your criteria."
    
    task_list = []
    for i, task in enumerate(result, 1):
        task_info = (
            f"{i}. [{task['status'].upper()}] {task['title']}\n"
            f"   ID: {task['id']}\n"
            f"   Description: {task['description']}\n"
            f"   Priority: {task['priority']}\n"
            f"   Due by: {task.get('due_by', 'Not set')}\n"
            f"   Created: {task['created_at']}"
        )
        task_list.append(task_info)
    
    return f">>> Found {len(result)} task(s):\n\n" + "\n\n".join(task_list)

@mcp.tool()
async def get_task_by_id(task_id: str) -> str:
    """
    Get a specific task by its ID.
    
    Args:
        task_id: The unique ID of the task
    
    Returns:
        Full details of the requested task
    """
    result = await make_api_request("GET", f"/task/{task_id}")
    
    return (
        f">>> Task Details:\n\n"
        f"ID: {result['id']}\n"
        f"Title: {result['title']}\n"
        f"Description: {result['description']}\n"
        f"Status: {result['status']}\n"
        f"Priority: {result['priority']}\n"
        f"Due by: {result.get('due_by', 'Not set')}\n"
        f"Created: {result['created_at']}\n"
        f"Updated: {result['updated_at']}\n"
        f"Deleted: {result['is_deleted']}"
    )

@mcp.tool()
async def update_task(
    task_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    due_by: Optional[str] = None
) -> str:
    """
    Update an existing task. You can update one or multiple fields at once.
    
    Args:
        task_id: The unique ID of the task to update
        title: New title (optional)
        description: New description (optional)
        status: New status - must be one of: pending, inprogress, completed (optional)
        priority: New priority - must be one of: urgent, high, medium, low (optional)
        due_by: New due date in ISO format (optional)
    
    Returns:
        A success message with the updated task details
    """
    update_data = {}
    for key, value in {
        "title": title,
        "description": description,
        "status": status,
        "priority": priority,
        "due_by": due_by
    }.items():
        if value is not None:
            update_data[key] = value
    
    if not update_data:
        return " No fields provided to update."
    
    result = await make_api_request("PATCH", f"/task/{task_id}", json_data=update_data)
    
    return (
        f">>> Task updated successfully!\n\n"
        f"ID: {result['id']}\n"
        f"Title: {result['title']}\n"
        f"Status: {result['status']}\n"
        f"Priority: {result['priority']}\n"
        f"Due by: {result.get('due_by', 'Not set')}\n"
        f"Updated at: {result['updated_at']}"
    )

@mcp.tool()
async def delete_task(task_id: str) -> str:
    """
    Delete a task (soft delete - marks as deleted but keeps in database).
    
    Args:
        task_id: The unique ID of the task to delete
    
    Returns:
        A success message confirming deletion
    """
    await make_api_request("DELETE", f"/task/{task_id}")
    return f">>> Task {task_id} deleted successfully."

if __name__ == "__main__":
    print("Starting MCP Calculator Server on http://localhost:8000")
    mcp.run(transport="streamable-http")