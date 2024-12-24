# Voice Agent Discovery System

## Project Overview
An automated system for discovering and mapping conversation scenarios handled by AI Voice Agents for small businesses. The system makes synthetic calls to test various conversation paths and generates a visual representation of the discovered scenarios.

### Target Voice Agents
- AC and Plumbing Service: +14153580761
- Auto Dealership (New/Used Cars): +16508798564

## Features
- Automated call initiation and recording
- Speech-to-text transcription
- Conversation analysis and scenario generation
- Visual graph representation of conversation paths
- Real-time progress tracking
- Webhook handling for call status updates

## System Architecture
- **Voice Calls**: Hamming API for synthetic call generation
- **Transcription**: AssemblyAI for speech-to-text conversion
- **Analysis**: OpenAI GPT-4 for conversation understanding
- **Visualization**: NetworkX for scenario graph generation

## Setup and Configuration

### API Keys Required
```python
OPENAI_API_KEY = 'your-openai-key'
HAMMING_API_TOKEN = 'your-hamming-token'
ASSEMBLY_API_KEY = 'your-assembly-key'
```

### Running the System
Open 3 terminal tabs and run:

#### Terminal 1: Start Webhook Server
```bash
python run_webhook.py
```

#### Terminal 2: Start ngrok Tunnel
```bash
ngrok http 5000
```

#### Terminal 3: Execute Discovery
```bash
python execute_voice_agent_discovery.py
```

## System Components
1. **Voice Agent Discovery**: Main orchestrator
2. **Conversation Analyzer**: Processes transcripts and generates scenarios
3. **Scenario Tracker**: Builds and visualizes the conversation graph
4. **Hamming Client**: Handles API calls for synthetic conversations
5. **Assembly Transcriber**: Converts call recordings to text

## Output
- Real-time console progress updates
- Visual graph of discovered conversation paths
- JSON export of conversation scenarios
- Transcript logs of all calls

## Technical Requirements
- Python 3.8+
- Flask for webhook handling
- NetworkX for graph visualization
- AssemblyAI SDK
- OpenAI API
- Hamming API access

## Project Constraints
- Local execution (no cloud deployment)
- Monolithic architecture
- Maximum scenario exploration limit
- Webhook for async call status updates

## Error Handling
- Retry logic for failed calls
- Graceful handling of transcription errors
- Timeout management for long-running calls
- Logging of all system events

## Development Notes
- Production-quality code and documentation
- Extensible architecture for new features
- Real-time progress visualization
- Efficient scenario de-duplication
- Comprehensive error logging