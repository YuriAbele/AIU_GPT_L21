from typing import Dict, List, Any

# Структура: {user_id: {"tasks": [], "deals": []}}
# Task: {"name": str, "time": str}
# Deal: {"name": str, "amount": str, "status": str}
DATABASE: Dict[int, Dict[str, List[Dict[str, Any]]]] = {}

def get_user_db(user_id: int):
    if user_id not in DATABASE:
        DATABASE[user_id] = {"tasks": [], "deals": []}
    return DATABASE[user_id]