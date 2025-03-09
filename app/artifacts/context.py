from pydantic import BaseModel
from typing import List, Optional, Dict

class ContextArtifact(BaseModel):
    destination: Optional[str] = None
    duration: Optional[int] = None
    group_size: Optional[int] = None
    budget: Optional[str] = None
    preferences: List[str] = []
    additional_info: Dict[str, str] = {}
    
    def update(self, new_context: Dict):
        """Update context with new information"""
        for key, value in new_context.items():
            if hasattr(self, key) and value:
                setattr(self, key, value)
        
    def is_sufficient(self) -> bool:
        """Check if minimum context is available"""
        return self.destination is not None and self.duration is not None