"""
Scenario-specific prompts for Moondream safety detection system
Adapted from VISIONAI-VIT for scenario-based processing
"""

scenario_prompts = {
    "smoke_detection": {
        "vision": {
            "prompt": {
                "description": "Detect smoke or smoke-like substances in the image",
                "prompt": "Analyze this image carefully. Do you see any smoke, steam, or smoke-like substances visible? Look for white, gray, or dark clouds of smoke, steam from machinery, or any other smoke-like emissions. Respond with a clear description of what you observe."
            }
        },
        "text": {
            "prompt": {
                "description": "Validate smoke detection based on vision analysis",
                "prompt": "Based on this vision analysis: '{vision_response}', answer with ONLY 'yes' or 'no': Is there smoke or smoke-like substance detected in the image?"
            }
        }
    },
    
    "fire_detection": {
        "vision": {
            "prompt": {
                "description": "Detect fire or flames in the image",
                "prompt": "Examine this image thoroughly. Do you see any fire, flames, or burning materials? Look for visible flames, glowing embers, or signs of combustion. Describe what you observe regarding fire or burning."
            }
        },
        "text": {
            "prompt": {
                "description": "Validate fire detection based on vision analysis",
                "prompt": "Based on this vision analysis: '{vision_response}', answer with ONLY 'yes' or 'no': Is there fire or flames detected in the image?"
            }
        }
    },
    
    "fall_detection": {
        "vision": {
            "prompt": {
                "description": "Detect if a person has fallen or is in a dangerous position",
                "prompt": "Carefully analyze this image. Do you see any person who appears to have fallen, is lying down, or is in an unusual position that might indicate they have fallen or are in distress? Look for people on the ground, in awkward positions, or showing signs of injury."
            }
        },
        "text": {
            "prompt": {
                "description": "Validate fall detection based on vision analysis",
                "prompt": "Based on this vision analysis: '{vision_response}', answer with ONLY 'yes' or 'no': Is there a person who has fallen or appears to be in a dangerous position?"
            }
        }
    },
    
    "debris_detection": {
        "vision": {
            "prompt": {
                "description": "Detect debris, obstacles, or hazardous materials on the ground",
                "prompt": "Examine this image for any debris, scattered objects, or hazardous materials on the ground or floor. Look for broken equipment, spilled materials, loose objects, or anything that could pose a safety hazard or obstruction."
            }
        },
        "text": {
            "prompt": {
                "description": "Validate debris detection based on vision analysis",
                "prompt": "Based on this vision analysis: '{vision_response}', answer with ONLY 'yes' or 'no': Is there debris, obstacles, or hazardous materials detected on the ground?"
            }
        }
    },
    
    "missing_fire_extinguisher": {
        "vision": {
            "prompt": {
                "description": "Check if fire extinguisher is present in designated location",
                "prompt": "Look at this image and check if there is a fire extinguisher present in its designated location. Fire extinguishers are typically red cylinders mounted on walls or in cabinets. Is the fire extinguisher visible in its expected location?"
            }
        },
        "text": {
            "prompt": {
                "description": "Validate fire extinguisher presence based on vision analysis",
                "prompt": "Based on this vision analysis: '{vision_response}', answer with ONLY 'yes' or 'no': Is the fire extinguisher present in its designated location?"
            }
        }
    },
    
    "unattended_object": {
        "vision": {
            "prompt": {
                "description": "Detect unattended objects or suspicious items",
                "prompt": "Analyze this image for any unattended objects, suspicious items, or objects that appear to be left behind. Look for bags, packages, tools, or other items that seem to be abandoned or left unattended in the area."
            }
        },
        "text": {
            "prompt": {
                "description": "Validate unattended object detection based on vision analysis",
                "prompt": "Based on this vision analysis: '{vision_response}', answer with ONLY 'yes' or 'no': Are there unattended objects or suspicious items detected in the image?"
            }
        }
    }
}

def get_scenario_prompt(scenario: str, prompt_type: str) -> str:
    """
    Get the appropriate prompt for a scenario and type
    
    Args:
        scenario: The scenario type (e.g., 'smoke_detection', 'fire_detection')
        prompt_type: The prompt type ('vision' or 'text')
        
    Returns:
        The formatted prompt string
    """
    if scenario not in scenario_prompts:
        raise ValueError(f"Unknown scenario: {scenario}")
    
    if prompt_type not in scenario_prompts[scenario]:
        raise ValueError(f"Unknown prompt type: {prompt_type}")
    
    return scenario_prompts[scenario][prompt_type]["prompt"]["prompt"]

def get_text_validation_prompt(scenario: str, vision_response: str) -> str:
    """
    Get the text validation prompt for a scenario
    
    Args:
        scenario: The scenario type
        vision_response: The response from the vision model
        
    Returns:
        The formatted text validation prompt
    """
    base_prompt = get_scenario_prompt(scenario, "text")
    return base_prompt.format(vision_response=vision_response)

def list_available_scenarios() -> List[str]:
    """
    Get list of available scenarios
    
    Returns:
        List of scenario names
    """
    return list(scenario_prompts.keys())

def get_scenario_description(scenario: str) -> str:
    """
    Get description of a scenario
    
    Args:
        scenario: The scenario type
        
    Returns:
        Description of the scenario
    """
    if scenario not in scenario_prompts:
        raise ValueError(f"Unknown scenario: {scenario}")
    
    return scenario_prompts[scenario]["vision"]["prompt"]["description"]
