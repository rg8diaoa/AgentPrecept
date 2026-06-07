"""detect compass-mcp full path"""
import sys, shutil
from pathlib import Path

# Find compass-mcp.exe or compass-mcp script
scripts = Path(sys.prefix) / "Scripts"
for name in ["compass-mcp.exe", "compass-mcp-script.py", "compass-mcp"]:
    p = scripts / name
    if p.exists():
        print(f"FOUND: {p}")
    else:
        print(f"NOT: {p}")

print()
print("Recommended MCP config:")
print('"command": "python",')
print(f'"args": ["-m", "agent_compass.mcp_server"],')
print('"cwd": "C:\\\\Users\\\\Administrator\\\\agent-compass"')
