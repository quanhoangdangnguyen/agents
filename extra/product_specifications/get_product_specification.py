from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from agents import Agent, WebSearchTool, trace, Runner, gen_trace_id, function_tool,AgentOutputSchema
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from agents.model_settings import ModelSettings
import asyncio
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime
import json

load_dotenv(override=True)

# ---------------------------------------------------------
# 1. THE HARDWARE DOMAIN (Immutable Physical Specs)
# ---------------------------------------------------------
class TVHardwareSpecs(BaseModel):
    # Display Hardware
    panel_technology: Optional[str] = Field(description="The core physical display technology. If not found on the website, output null.")

    resolution: Optional[str] = Field(description="Hardware pixel count, e.g., 3840x2160. If not found on the website, output null.")
    native_refresh_rate_hz: Optional[int] = Field(description="Maximum native panel refresh rate (e.g., 60, 120, 144). If not found on the website, output null.")
    
    # Internal Processing Hardware
    processor_chip: Optional[str] = Field(description="Physical SoC/Processor name (e.g., NQ4 AI Gen2, Cognitive Processor XR). If not found on the website, output null.")
    
    # Physical Audio Hardware
    speaker_channels: Optional[str] = Field(description="Physical speaker layout (e.g., 2.1.2, 4.2.2). If not found on the website, output null.")
    audio_output_watts: Optional[int] = Field(description="Total RMS wattage of the speakers, if found please get number only. If not found on the website, output null (without quotes).")
    
    # Physical I/O (Ports)
    total_hdmi_ports: Optional[int] = Field(description="Total physical HDMI inputs. If not found on the website, output null.")
    hdmi_2_1_ports: Optional[int] = Field(description="Number of full-bandwidth HDMI 2.1 ports. If not found on the website, output null.")
    usb_ports: Optional[int] = Field(description="Number of USD ports. If not found on the website, output null.")
    ethernet_port: Optional[bool] = Field(description="Number of ethernet ports. If not found on the website, output null.")
    optical_audio_out: Optional[bool] = Field(description="Does it has optical audio out. If not found on the website, output null.")

    # Logistics Hardware
    net_weight_kg: Optional[float]=Field(
        description="Weight in kg. If not found on the website, output null."
    )
    dimensions_no_stand_mm: Optional[dict] = Field(description="{'W': float, 'H': float, 'D': float}")
    vesa_mount_mm: Optional[str] = Field(description="Wall mount dimensions")

# ---------------------------------------------------------
# 2. THE SOFTWARE DOMAIN (Mutable Digital Ecosystem)
# ---------------------------------------------------------
class TVSoftwareSpecs(BaseModel):
    # Operating System
    smart_os: Optional[str] = Field(description="Core operating system (e.g., Tizen, Google TV, webOS). If not found on the website, output null.")
    os_version: Optional[str] = Field(None, description="Specific OS version if listed. If not found on the website, output null.")
    
    # Supported Formats (Decoded via Software)
    hdr_formats: Optional[List[str]] = Field(default_factory=list, description="Supported HDR standards (e.g., HDR10+, Dolby Vision). If not found on the website, output null.")
    audio_decoding: Optional[List[str]] = Field(default_factory=list, description="Supported audio formats (e.g., Dolby Atmos, DTS:X). If not found on the website, output null.")
    
    # Digital Smart Features
    voice_assistants: Optional[List[str]] = Field(default_factory=list, description="Built-in AI assistants (e.g., Bixby, Google Assistant, Alexa). If not found on the website, output null.")
    casting_protocols: Optional[List[str]] = Field(default_factory=list, description="e.g., Apple AirPlay 2, Chromecast built-in. If not found on the website, output null.")
    smart_home_integration: Optional[List[str]] = Field(default_factory=list, description="e.g., SmartThings, Apple HomeKit. If not found on the website, output null.")
    
    # Software-Driven Enhancements (Marketing Features)
    ai_enhancements: Optional[List[str]] = Field(default_factory=list, description="Software upscaling/color engines (e.g., AI Motion Enhancer, Color Booster Pro). If not found on the website, output null.")
    gaming_features: Optional[List[str]] = Field(default_factory=list, description="e.g., Game Bar, Auto Low Latency Mode (ALLM), VRR. If not found on the website, output null.")

# ---------------------------------------------------------
# 3. THE MASTER RECORD
# ---------------------------------------------------------
class TVProductRecord(BaseModel):
    brand: Optional[str]=Field(description="Brand name. If not found on the website, output null.")
    model_code:Optional[str]=Field(description="Model code. If not found on the website, output null.")
    model_name: Optional[str]=Field(description="Name of model. If not found on the website, output null.")
    year_released: Optional[int]=Field(description="Year of model realeased. If not found on the website, output null.")
    
    # The clean separation
    hardware: TVHardwareSpecs
    software: TVSoftwareSpecs
    
    source_urls: List[str]

INSTRUCTIONS = """You are an expert Data Engineer specializing in Consumer Electronics. Your task is to use the WebSearchTool to research a specific television model and extract its specifications into the provided JSON schema.

CRITICAL INSTRUCTION: You must strictly separate immutable physical hardware from the mutable digital software ecosystem.

1. HARDWARE DOMAIN (Immutable Physical Specs):
- Verbatim Marketing Terms: For display technology and processors, extract the EXACT proprietary marketing term used by the manufacturer (e.g., "Neo QLED", "OLED Evo", "Triluminos"). Do not translate or normalize these into generic terms.
- Refresh Rate: Find the TRUE native hardware panel refresh rate in Hz (e.g., 60, 120, 144).
- Logistics Strictness: Accuracy is critical. Convert all dimensions to millimeters (mm) and all weights to kilograms (kg). (1 inch = 25.4 mm; 1 lb = 0.453592 kg).
- Resolution & Ports: Format resolution strictly as [Width]x[Height] (e.g., "3840x2160"). Distinguish clearly between standard HDMI and high-bandwidth HDMI 2.1 ports.

2. SOFTWARE DOMAIN (Mutable Digital Ecosystem):
- Operating System: Identify the core Smart TV platform (e.g., Tizen, webOS, Google TV).
- Dynamic Features: Capture the exact branded names for software-driven features, including HDR formats (e.g., Dolby Vision, HDR10+), smart home integrations (e.g., Apple HomeKit, SmartThings), and AI enhancements (e.g., AI Motion Enhancer).

3. SOURCE AUTHORITY & VERIFICATION:
- Prioritize official manufacturer domains (e.g., samsung.com, lg.com, sony.com) and official PDF spec sheets.
- Include all exact URLs used for this extraction in the `source_urls` list.

4. ANTI-HALLUCINATION:
- If a specification is not explicitly mentioned after a thorough search of the manufacturer's site, output `null` (None) for strings/numbers or an empty array `[]` for lists. Do not guess, estimate, or assume."""

search_agent = Agent(
    name="Search agent",
    instructions=INSTRUCTIONS,
    tools=[WebSearchTool(search_context_size="low")],
    model="gpt-4o-mini",
    model_settings=ModelSettings(tool_choice="required"),
    output_type=AgentOutputSchema(TVProductRecord, strict_json_schema=False),
)

# 1. Define the asynchronous coroutine
async def execute_agent_search(search_agent, message: str):
    # 2. Your await keyword is now safely inside an async function
    with trace("Search"):
        result = await Runner.run(search_agent, message)
        return result.final_output

# 3. Standard synchronous entry point
async def main():
    agent = search_agent
    model_list=pd.read_excel(r"Model_list.xlsx")
    model_list_dict=model_list.to_dict(orient='records')
    tasks = [asyncio.create_task(execute_agent_search(agent,f"Find the latest specifications for {item['Brand']} model {item['Model name']}")) for item in model_list_dict]
    # 4. Trigger the event loop to run the async function
    results = await asyncio.gather(*tasks)
    save_json_file(results)

def save_json_file(raw_results):
    processed_results = []
    for item in raw_results:
        if hasattr(item, "model_dump"): # Check if it's a Pydantic V2 object
            processed_results.append(item.model_dump())
        elif hasattr(item, "dict"):     # Check if it's a Pydantic V1 object
            processed_results.append(item.dict())
        else:
            processed_results.append(item)

    # 4. Export to .json file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"tv_specifications_{timestamp}.json"
    
    with open(filename, "w", encoding="utf-8") as f:
        # indent=4 makes it readable; ensure_ascii=False preserves Vietnamese characters
        json.dump(processed_results, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    asyncio.run(main())