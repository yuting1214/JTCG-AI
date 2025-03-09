import os
import httpx
from dotenv import load_dotenv
from typing import List, Optional
from datetime import datetime, timedelta
from llama_index.core.tools import FunctionTool
from llama_index.llms.openai import OpenAI
from app.config.constants import BASE_URL
from app.artifacts.itinerary import ItineraryArtifact
from app.workflow.models import VacancySearchParams, HotelSearchParams, HotelPlanParams, HotelRecommendation
from app.workflow.events import HotelRecommendationEvent

_ = load_dotenv('.env')

class HotelRecommenderAgent():
    def __init__(self, verbose: bool = False):
        self.api_base_url = f"{BASE_URL}/api/v3/tools/interview_test/taiwan_hotels"
        self.api_key = os.getenv("JTCG_API_KEY")
        if not self.api_key:
            raise ValueError("JTCG_API_KEY is not set")
        self.headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json"
        }
        self.tools = self._create_tools()
        self.tools_by_name = {tool.metadata.name: tool for tool in self.tools}

    async def _make_api_request(self, endpoint: str, params: dict = None) -> dict:
        """
        Make an authenticated API request.
        
        Args:
            endpoint (str): API endpoint path
            params (dict): Query parameters
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_base_url}/{endpoint}",
                params=params,
                headers=self.headers,
                timeout=30.0  # Add timeout for safety
            )
            
            if response.status_code == 401:
                raise ValueError("Invalid API key")
            elif response.status_code == 403:
                raise ValueError("Unauthorized access")
            elif response.status_code != 200:
                raise ValueError(f"API request failed with status {response.status_code}: {response.text}")
            
            return response.json()

    async def search_hotels_by_name(self, keyword: str) -> List[dict]:
        """
        Search hotels using fuzzy name matching.
        
        Args:
            hotel_name (str): Hotel name or keyword to search
        """
        return await self._make_api_request(
            "hotel/fuzzy_match",
            params={"hotel_name": keyword}
        )

    async def get_hotel_details(self, hotel_name: str) -> dict:
        """
        Get details of a specific hotel.
        
        Args:
            hotel_name (str): Name of the hotel
        """
        return await self._make_api_request(
            "hotel/details",
            params={"hotel_name": hotel_name}
        )
    
    async def check_hotel_vacancies(
        self,
        check_in_date: datetime,
        check_out_date: datetime,
        county_ids: List[str]
    ) -> List[dict]:
        """
        Check hotel vacancies for given dates and requirements.
        
        Args:
            check_in_date (datetime): Check-in date
            check_out_date (datetime): Check-out date
            county_ids (List[str]): List of county IDs
        """
        return await self._make_api_request(
            "hotel/vacancies",
            params={
                "check_in_date": check_in_date.strftime("%Y-%m-%d"),
                "check_out_date": check_out_date.strftime("%Y-%m-%d"),
                "county_ids": county_ids
            }
        )

    async def get_hotel_plans(
            self,
            hotel_keyword: str,
            plan_keyword: str,
            check_in_date: datetime,
            check_out_date: datetime,
    ) -> List[dict]:
        """
        Get available booking plans for a specific hotel.
        
        Args:
            hotel_keyword (str): Keyword to search for hotels
            plan_keyword (str): Keyword to search for plans
            check_in_date (datetime): Check-in date
            check_out_date (datetime): Check-out date
        """
        return await self._make_api_request(
            "plans",
            params={
                "hotel_keyword": hotel_keyword,
                "plan_keyword": plan_keyword,
                "check_in_date": check_in_date.strftime("%Y-%m-%d"),
                "check_out_date": check_out_date.strftime("%Y-%m-%d")
            }
        )

    def _create_tools(self) -> List[FunctionTool]:
        """Create function tools for the agent."""
        return [
            FunctionTool.from_defaults(
                fn=self.search_hotels_by_name,
                name="search_hotels",
                description="Search for hotels using name or keywords",
                fn_schema=HotelSearchParams
            ),
            FunctionTool.from_defaults(
                fn=self.check_hotel_vacancies,
                name="check_vacancies",
                description="Check hotel room availability for specific dates",
                fn_schema=VacancySearchParams
            ),
            FunctionTool.from_defaults(
                fn=self.get_hotel_plans,
                name="get_plans",
                description="Get available booking plans for a specific hotel",
                fn_schema=HotelPlanParams
            )
        ]
    
    async def execute_tool(self, tool_name: str, **kwargs) -> dict:
        """Execute a specific tool with given parameters."""
        tool = self.tools_by_name.get(tool_name)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found")
        
        try:
            result = await tool.acall(**kwargs)
            return result
        except httpx.HTTPStatusError as e:
            self._log_verbose(f"HTTP error executing tool '{tool_name}': {str(e)}")
            raise
        except httpx.RequestError as e:
            self._log_verbose(f"Request error executing tool '{tool_name}': {str(e)}")
            raise
        except Exception as e:
            self._log_verbose(f"Error executing tool '{tool_name}': {str(e)}")
            raise

    async def process(self, content: ItineraryArtifact) -> HotelRecommendationEvent:
        """Generate hotel recommendations based on itinerary content."""

        # Extract locations from daily plans
        locations = set()
        for plan in content.daily_plans:
            for activity in plan.activities:
                if 'location' in activity:
                    locations.add(activity['location'])

        # Search for hotels near activity locations
        hotel_recommendations = []
        for location in locations:
            try:

                # Check vacancies for each hotel
                hotels = await self.execute_tool(
                    "check_vacancies",
                    check_in_date=content.context.start_date,
                    check_out_date=content.context.start_date + timedelta(days=content.context.duration),
                    num_rooms=(content.context.group_size + 1) // 2,
                    num_guests=content.context.group_size
                )

                # Get plans for available hotels
                for hotel in hotels[:3]:  # Limit to top 3 hotels
                    if hotel["id"] in [v["hotel_id"] for v in vacancies]:
                        plans = await self.execute_tool(
                            "get_plans",
                            hotel_id=hotel["id"]
                        )

                        recommendation = HotelRecommendation(
                            name=hotel["name"],
                            location=hotel["address"],
                            price_range=f"{min(p['price'] for p in plans)} - {max(p['price'] for p in plans)}",
                            amenities=hotel.get("facilities", []),
                            description=hotel.get("description", ""),
                            available_plans=plans
                        )
                        hotel_recommendations.append(recommendation)

            except Exception as e:
                self._log_verbose(f"Error processing location {location}: {str(e)}")
                continue

        content.hotel_recommendations = hotel_recommendations
        self._log_verbose(f"Generated {len(hotel_recommendations)} hotel recommendations")
        
        return HotelRecommendationEvent(content=content)