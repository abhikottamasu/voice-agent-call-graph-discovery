from voice_agent_discovery import VoiceAgentDiscovery

HVAC_PLUMBING_AGENT = '+14153580761'
AUTO_DEALERSHIP_AGENT = '+16508798564'

discovery = VoiceAgentDiscovery()
phone_numbers = [
    HVAC_PLUMBING_AGENT,
    AUTO_DEALERSHIP_AGENT
]

# for phone in phone_numbers:
#     discovery.discover_scenarios(
#         phone,
#         "Initial customer inquiry"
#     )

# Example usage
discovery = VoiceAgentDiscovery()

# Track different scenarios
# discovery.track_scenario(
#     path=["greeting", "service inquiry", "AC repair", "schedule appointment"],
#     outcome="appointment_scheduled"
# )

# discovery.track_scenario(
#     path=["greeting", "service inquiry", "plumbing", "emergency"],
#     outcome="immediate_dispatch"
# )

# # Export as JSON
# json_output = discovery.export_graph('json')
# print(json_output)

# # Create visual graph
# discovery.export_graph('visual')
