# Claude Code Template - Bedrock Backend

Template capsule for executing AI-assisted coding tasks with Claude Code using AWS Bedrock backend.

## Quick Start

```bash
./run "Create a Python script that processes CSV files"
```

Claude Code will execute your command and save outputs to `/results`.

## Configuration

This capsule is pre-configured to use AWS Bedrock:
- `CLAUDE_CODE_USE_BEDROCK=1` - Uses AWS Bedrock instead of Anthropic API
- `AWS_REGION=us-east-1` - Bedrock region
- Code Ocean managed IAM credentials (no manual setup needed)
- Claude Code automatically selects the best available Sonnet model

## Usage Examples

```bash
# Create code
./run "Write a function to calculate prime numbers"

# Analyze data  
./run "Create a data analysis script for genomics data in /data"

# Debug code
./run "Fix the bug in /code/analysis.py"

# Generate documentation
./run "Add docstrings to all functions in /code"
```

## For Hackathon Participants

1. **Duplicate this capsule** for your challenge
2. **Add your data assets** to `/data`
3. **Run commands** to let Claude Code build your solution
4. **Results** saved automatically to `/results`

## File Structure

```
/code/
  └── run          # Passes commands to Claude Code

/results/
  └── claude_output.txt   # Claude's response
```

## Notes

- Runs headlessly (no interactive prompts)
- Uses Code Ocean managed AWS credentials
- Works in reproducible runs and Cloud Workstations
- All code generation is done by Claude Code via Bedrock
