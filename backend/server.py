from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
from enum import Enum

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="Emergency Response API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Enums for better type safety
class EmergencyType(str, Enum):
    CHOKING = "choking"
    BLEEDING = "bleeding"
    ALLERGIC_REACTION = "allergic_reaction"

class HelpRequestStatus(str, Enum):
    ACTIVE = "active"
    RESPONDED = "responded"
    RESOLVED = "resolved"

class SeverityLevel(str, Enum):
    MINOR = "minor"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"

# Models
class EmergencyInstruction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: EmergencyType
    title: str
    description: str
    steps: List[str]
    voice_instructions: List[str]  # Optimized for speech synthesis
    severity: SeverityLevel
    duration_estimate: str  # e.g., "2-3 minutes"
    when_to_call_911: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class HelpRequest(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    emergency_type: EmergencyType
    location_description: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    contact_phone: Optional[str] = None
    additional_info: Optional[str] = None
    status: HelpRequestStatus = HelpRequestStatus.ACTIVE
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class HelpRequestCreate(BaseModel):
    emergency_type: EmergencyType
    location_description: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    contact_phone: Optional[str] = None
    additional_info: Optional[str] = None

class HelpRequestUpdate(BaseModel):
    status: HelpRequestStatus

# Initialize emergency instructions data
async def initialize_emergency_data():
    """Initialize the database with emergency instruction data"""
    existing_count = await db.emergency_instructions.count_documents({})
    if existing_count > 0:
        return  # Data already exists
    
    instructions = [
        # Choking Instructions
        EmergencyInstruction(
            type=EmergencyType.CHOKING,
            title="Adult Choking (Conscious)",
            description="For conscious adults who cannot cough, speak, or breathe",
            severity=SeverityLevel.CRITICAL,
            duration_estimate="1-2 minutes",
            when_to_call_911="If person becomes unconscious or obstruction doesn't clear",
            steps=[
                "Stand behind the person",
                "Place arms around their waist",
                "Make a fist with one hand, place thumb side against abdomen above navel",
                "Grasp fist with other hand, press hard into abdomen with quick upward thrust",
                "Repeat until object is expelled or person becomes unconscious"
            ],
            voice_instructions=[
                "Stand behind the choking person",
                "Wrap your arms around their waist", 
                "Make a fist and place it above their belly button",
                "Grab your fist with your other hand",
                "Push hard and quick upward into their abdomen",
                "Keep doing this until the object comes out"
            ]
        ),
        EmergencyInstruction(
            type=EmergencyType.CHOKING,
            title="Child Choking (1-8 years)",
            description="For conscious children who cannot cough, speak, or breathe",
            severity=SeverityLevel.CRITICAL,
            duration_estimate="1-2 minutes",
            when_to_call_911="Immediately, even if obstruction clears",
            steps=[
                "Kneel behind child or stand if child is small",
                "Place arms around child's waist",
                "Make fist, place thumb side against abdomen above navel, below breastbone",
                "Press hard into abdomen with quick upward thrusts",
                "Be gentler than with adults",
                "Continue until object is expelled"
            ],
            voice_instructions=[
                "Get behind the child at their level",
                "Put your arms around their waist",
                "Make a fist above their belly button, below the chest",
                "Push gently but firmly upward",
                "Keep doing this until the object comes out",
                "Call nine one one immediately"
            ]
        ),
        # Bleeding Instructions  
        EmergencyInstruction(
            type=EmergencyType.BLEEDING,
            title="Severe Bleeding Control",
            description="For heavy bleeding from cuts or wounds",
            severity=SeverityLevel.SEVERE,
            duration_estimate="Until medical help arrives",
            when_to_call_911="For any severe bleeding that won't stop",
            steps=[
                "Apply direct pressure with clean cloth or bandage",
                "Press firmly on the wound",
                "If blood soaks through, add more layers without removing original",
                "Raise injured area above heart level if possible",
                "Continue pressure until bleeding stops or help arrives"
            ],
            voice_instructions=[
                "Put a clean cloth directly on the wound",
                "Press down firmly with your hands",
                "If blood soaks through, add more cloth on top",
                "Keep pressing without stopping",
                "Lift the injured part higher than the heart if you can",
                "Don't stop pressing until help arrives"
            ]
        ),
        EmergencyInstruction(
            type=EmergencyType.BLEEDING,
            title="Minor Cut Treatment",
            description="For small cuts and scrapes",
            severity=SeverityLevel.MINOR,
            duration_estimate="5-10 minutes",
            when_to_call_911="If bleeding won't stop after 10 minutes of pressure",
            steps=[
                "Clean hands before treating wound",
                "Apply gentle pressure with clean cloth",
                "Clean wound gently with water",
                "Apply antibiotic ointment if available",
                "Cover with sterile bandage",
                "Change bandage daily and keep wound clean"
            ],
            voice_instructions=[
                "First, wash your hands",
                "Put gentle pressure on the cut with a clean cloth",
                "When bleeding stops, clean the cut with water",
                "Put on antibiotic cream if you have it",
                "Cover with a clean bandage",
                "Change the bandage every day"
            ]
        ),
        # Allergic Reaction Instructions
        EmergencyInstruction(
            type=EmergencyType.ALLERGIC_REACTION,
            title="Severe Allergic Reaction (Anaphylaxis)",
            description="Life-threatening allergic reaction with breathing problems",
            severity=SeverityLevel.CRITICAL,
            duration_estimate="Immediate action required",
            when_to_call_911="Immediately for severe allergic reactions",
            steps=[
                "Call 911 immediately",
                "Use epinephrine auto-injector (EpiPen) if available",
                "Help person lie down with legs elevated",
                "Remove or avoid allergen if known",
                "Monitor breathing and pulse",
                "Be prepared to perform CPR if needed"
            ],
            voice_instructions=[
                "Call nine one one right now",
                "If there's an EpiPen, use it on the outer thigh",
                "Help the person lie down",
                "Lift their legs up",
                "Stay with them and watch their breathing",
                "Be ready to do CPR if they stop breathing"
            ]
        ),
        EmergencyInstruction(
            type=EmergencyType.ALLERGIC_REACTION,
            title="Mild Allergic Reaction",
            description="Minor allergic reactions with skin or mild symptoms",
            severity=SeverityLevel.MINOR,
            duration_estimate="Monitor for 30 minutes",
            when_to_call_911="If symptoms worsen or breathing becomes difficult",
            steps=[
                "Remove or avoid the allergen",
                "Give antihistamine if available (Benadryl)",
                "Apply cool compress to affected skin",
                "Monitor for worsening symptoms",
                "Seek medical attention if symptoms persist or worsen"
            ],
            voice_instructions=[
                "Stay away from whatever caused the reaction",
                "Take an antihistamine like Benadryl if you have it",
                "Put a cool cloth on itchy skin",
                "Watch carefully for any worsening",
                "Get medical help if it gets worse"
            ]
        )
    ]
    
    # Insert instructions into database
    for instruction in instructions:
        await db.emergency_instructions.insert_one(instruction.dict())

# API Routes
@api_router.get("/")
async def root():
    return {"message": "Emergency Response API", "status": "active"}

@api_router.get("/emergency-instructions", response_model=List[EmergencyInstruction])
async def get_all_instructions():
    """Get all emergency instructions for offline caching"""
    instructions = await db.emergency_instructions.find().to_list(1000)
    return [EmergencyInstruction(**instruction) for instruction in instructions]

@api_router.get("/emergency-instructions/{emergency_type}", response_model=List[EmergencyInstruction])
async def get_instructions_by_type(emergency_type: EmergencyType):
    """Get emergency instructions by type"""
    instructions = await db.emergency_instructions.find({"type": emergency_type}).to_list(1000)
    if not instructions:
        raise HTTPException(status_code=404, detail=f"No instructions found for {emergency_type}")
    return [EmergencyInstruction(**instruction) for instruction in instructions]

@api_router.post("/help-requests", response_model=HelpRequest)
async def create_help_request(help_request: HelpRequestCreate):
    """Create a new help request"""
    help_obj = HelpRequest(**help_request.dict())
    await db.help_requests.insert_one(help_obj.dict())
    return help_obj

@api_router.get("/help-requests", response_model=List[HelpRequest])
async def get_help_requests():
    """Get all active help requests"""
    requests = await db.help_requests.find({"status": "active"}).to_list(1000)
    return [HelpRequest(**request) for request in requests]

@api_router.put("/help-requests/{request_id}", response_model=HelpRequest)
async def update_help_request(request_id: str, update_data: HelpRequestUpdate):
    """Update help request status"""
    update_dict = update_data.dict()
    update_dict["updated_at"] = datetime.utcnow()
    
    result = await db.help_requests.find_one_and_update(
        {"id": request_id},
        {"$set": update_dict},
        return_document=True
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="Help request not found")
    
    return HelpRequest(**result)

@api_router.get("/help-requests/{request_id}", response_model=HelpRequest)
async def get_help_request(request_id: str):
    """Get specific help request"""
    request = await db.help_requests.find_one({"id": request_id})
    if not request:
        raise HTTPException(status_code=404, detail="Help request not found")
    return HelpRequest(**request)

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_db():
    """Initialize database with emergency instructions"""
    await initialize_emergency_data()
    logger.info("Emergency instructions initialized")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()