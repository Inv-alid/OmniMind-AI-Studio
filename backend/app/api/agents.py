from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_agents():
    return {
        "agents": [
            {
                "id": "code_architect",
                "name": "CodeArchitect",
                "description": "Writes, tests and architects code",
            },
            {
                "id": "research",
                "name": "Research Agent",
                "description": "Web search, documentation, up-to-date knowledge",
            },
            {
                "id": "data_analyst",
                "name": "Data Analyst",
                "description": "CSV/JSON analysis, insights, charts",
            },
            {
                "id": "creative_vision",
                "name": "Creative & Vision",
                "description": "Image prompts, multimodal, creative tasks",
            },
        ]
    }
