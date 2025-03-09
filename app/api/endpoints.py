from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from uuid import UUID
from typing import Dict, Any, Optional

from app.api.models import ConversationRequest, ConversationResponse
from app.api.session_manager import session_manager
from app.workflow.travel_itinerary import TravelItineraryWorkflow

router = APIRouter()

@router.post("/conversation", response_model=ConversationResponse)
async def handle_conversation(request: ConversationRequest) -> ConversationResponse:
    """
    Handle a conversation message, either starting a new conversation or continuing an existing one.
    
    Args:
        request: The conversation request containing the message and optional session ID
        
    Returns:
        A response containing the session ID, response message, and itinerary if available
    """
    try:
        # Check if this is a new or existing conversation
        if request.session_id is None:
            # New conversation
            session = session_manager.create_session()
            session_id = session.session_id
            
            # Create a new workflow
            workflow = TravelItineraryWorkflow(verbose=True)
            
            # Add message to history
            session_manager.add_message_to_history(session_id, "user", request.message)
            
            # Process the message
            result = await workflow.process_message(request.message)
            
            # Add response to history
            session_manager.add_message_to_history(session_id, "assistant", result.get("message", ""))
            
            # Update session with context and itinerary
            if "context" in result:
                session_manager.update_session(
                    session_id=session_id,
                    context=result["context"],
                    current_step="extract_context"
                )
            
            if "itinerary" in result:
                session_manager.update_session(
                    session_id=session_id,
                    itinerary=result["itinerary"],
                    current_step="integrate_itinerary"
                )
            
            return ConversationResponse(
                session_id=session_id,
                message=result.get("message", ""),
                itinerary=result.get("itinerary"),
                status="complete" if "itinerary" in result else "in_progress"
            )
        else:
            # Existing conversation
            session_id = request.session_id
            session = session_manager.get_session(session_id)
            
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
            
            # Add message to history
            session_manager.add_message_to_history(session_id, "user", request.message)
            
            # Create workflow with existing context and itinerary
            workflow = TravelItineraryWorkflow(
                verbose=True,
                existing_context=session.context,
                existing_itinerary=session.itinerary
            )
            
            # Process the message
            result = await workflow.process_message(request.message)
            
            # Add response to history
            session_manager.add_message_to_history(session_id, "assistant", result.get("message", ""))
            
            # Update session with new context and itinerary
            if "context" in result:
                session_manager.update_session(
                    session_id=session_id,
                    context=result["context"],
                    current_step="extract_context"
                )
            
            if "itinerary" in result:
                session_manager.update_session(
                    session_id=session_id,
                    itinerary=result["itinerary"],
                    current_step="integrate_itinerary"
                )
            
            return ConversationResponse(
                session_id=session_id,
                message=result.get("message", ""),
                itinerary=result.get("itinerary"),
                status="complete" if "itinerary" in result else "in_progress"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing conversation: {str(e)}")

# WebSocket endpoint for real-time conversation
@router.websocket("/ws/conversation/{session_id}")
async def websocket_conversation(websocket: WebSocket, session_id: Optional[UUID] = None):
    await websocket.accept()
    
    try:
        # Initialize session if needed
        if not session_id:
            session = session_manager.create_session()
            session_id = session.session_id
            await websocket.send_json({"type": "session_created", "session_id": str(session_id)})
        else:
            session = session_manager.get_session(session_id)
            if not session:
                # Create a new session with the provided ID
                session = session_manager.create_session()
                session_id = session.session_id
                await websocket.send_json({"type": "session_created", "session_id": str(session_id)})
        
        # Main WebSocket loop
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            message = data.get("message", "")
            
            # Add message to history
            session_manager.add_message_to_history(session_id, "user", message)
            
            # Create workflow with existing context and itinerary if available
            workflow = TravelItineraryWorkflow(
                verbose=True,
                existing_context=session.context,
                existing_itinerary=session.itinerary
            )
            
            # Process the message
            result = await workflow.process_message(message)
            
            # Add response to history
            session_manager.add_message_to_history(session_id, "assistant", result.get("message", ""))
            
            # Update session with new context and itinerary
            if "context" in result:
                session_manager.update_session(
                    session_id=session_id,
                    context=result["context"],
                    current_step="extract_context"
                )
            
            if "itinerary" in result:
                session_manager.update_session(
                    session_id=session_id,
                    itinerary=result["itinerary"],
                    current_step="integrate_itinerary"
                )
            
            # Send response to client
            await websocket.send_json({
                "type": "response",
                "message": result.get("message", ""),
                "itinerary": result.get("itinerary"),
                "status": "complete" if "itinerary" in result else "in_progress"
            })
            
    except WebSocketDisconnect:
        # Handle client disconnect
        pass
    except Exception as e:
        # Send error to client
        await websocket.send_json({
            "type": "error",
            "message": f"Error: {str(e)}"
        })
        # Close the connection
        await websocket.close() 