

## File Structure

```
travel-itinerary-generator/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── endpoints.py        # FastAPI endpoints
│   │   └── models.py           # Pydantic models for API
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── orchestrator.py     # Orchestrator agent
│   │   ├── clarification.py    # Clarification agent
│   │   ├── trip_planner.py     # Trip planner agent
│   │   ├── hotel_recommender.py # Hotel recommendation agent
│   │   ├── integrator.py       # Integrator agent
│   │   └── evaluator.py        # LLM evaluator module
│   ├── workflows/             # LlamaIndex Workflows
│   │   ├── travel_workflow.py # Defines agent execution pipeline
│   │
│   ├── artifacts/
│   │   ├── __init__.py
│   │   ├── context.py          # Context artifact management
│   │   └── itinerary.py        # Itinerary artifact management
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── llm.py              # LLM utilities
│   │   └── prompts.py          # Prompt templates
│   ├── ui/
│   │   ├── __init__.py
│   │   └── gradio_interface.py # Gradio UI
│   ├── __init__.py
│   └── main.py                 # Application entry point
├── tests/
│   ├── __init__.py
│   ├── test_agents/
│   ├── test_artifacts/
│   └── test_api/
├── .env                        # Environment variables
├── requirements.txt            # Project dependencies
├── README.md                   # Project documentation
└── docker-compose.yml          # Docker configuration
```