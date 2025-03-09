
# Travel Itinerary Generator

An intelligent travel planning system built with LlamaIndex, FastAPI, and Gradio that generates personalized travel itineraries through a pipeline of specialized AI agents.

## Features

- Dynamic itinerary generation based on user preferences
- Continuous conversation and itinerary refinement
- Hotel recommendations based on planned activities
- Quality evaluation of generated itineraries
- Interactive UI for real-time updates
- Comprehensive evaluation system

## Architecture

### Core Components

1. **LlamaIndex Workflow**
   - Orchestrates the sequential execution of specialized agents
   - Maintains context and itinerary artifacts throughout the process
   - Handles state management and agent communication

2. **FastAPI Backend**
   - RESTful API endpoints for itinerary generation
   - Async request handling
   - Error management and validation

3. **Gradio UI**
   - Interactive interface for user queries
   - Real-time itinerary updates
   - Visual presentation of travel plans

## Agent System

The project implements a sophisticated multi-agent system where each agent specializes in a specific aspect of travel planning:

### 1. Context Extraction Agent
- **Purpose**: Analyzes user queries to extract key travel parameters
- **Capabilities**:
  - Destination identification
  - Duration parsing
  - Group size determination
  - Budget classification
  - Preference extraction
- **Output**: Structured travel context for downstream agents

### 2. Daily Planner Agent
- **Purpose**: Generates detailed day-by-day itineraries
- **Capabilities**:
  - Activity scheduling
  - Meal recommendations
  - Transit planning
  - Time allocation
- **Considerations**:
  - Local operating hours
  - Travel distances
  - Activity pacing

### 3. Hotel Recommender Agent
- **Purpose**: Suggests accommodations based on itinerary
- **Capabilities**:
  - Location-based matching
  - Budget alignment
  - Amenity analysis
  - Group size accommodation
- **Features**:
  - Proximity analysis to planned activities
  - Price range optimization
  - Amenity relevance scoring

### 4. Itinerary Integrator Agent
- **Purpose**: Creates cohesive travel plans
- **Capabilities**:
  - Narrative generation
  - Schedule optimization
  - Practical tips integration
- **Output**:
  - Polished itinerary summary
  - Transportation logistics
  - Cultural considerations

### 5. Evaluator Agent
- **Purpose**: Assesses itinerary quality
- **Evaluation Criteria**:
  - Feasibility
  - Preference alignment
  - Timing optimization
  - Budget adherence
- **Features**:
  - Per-day scoring
  - Hotel recommendation assessment
  - Overall quality metrics

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

## Agent Communication Flow

1. **Query Processing**
   ```
   User Query → Context Extraction → Travel Parameters
   ```

2. **Itinerary Generation**
   ```
   Travel Parameters → Daily Planner → Activity Schedule
   ```

3. **Accommodation Planning**
   ```
   Activity Schedule → Hotel Recommender → Lodging Options
   ```

4. **Integration**
   ```
   Activities + Hotels → Integrator → Complete Itinerary
   ```

5. **Quality Assurance**
   ```
   Complete Itinerary → Evaluator → Quality Metrics
   ```

## Setup and Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/travel-itinerary-generator.git
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Usage

### Generate Itinerary
```python
POST /api/generate-itinerary
{
    "query": "Plan a 3-day trip to Tokyo for 2 people interested in food and culture"
}
```

### Update Itinerary
```python
PUT /api/update-itinerary
{
    "session_id": "...",
    "updates": "Add more food experiences to day 2"
}
```

## Development

### Adding New Agents

1. Create a new agent class in `app/agents/`
2. Inherit from `BaseAgent`
3. Implement the `process` method
4. Register the agent in the workflow

### Testing

```bash
pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Submit a pull request

## License

MIT License

## Acknowledgments

- LlamaIndex for the workflow framework
- OpenAI for LLM capabilities
- FastAPI for the web framework
- Gradio for the UI components