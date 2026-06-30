import sys
from pathlib import Path

# Add parent directory to Python path so src module can be found
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.app.server.server_main import main

# Add server directory to Python path
server_dir = Path(__file__).parent / "server"
sys.path.insert(0, str(server_dir))


if __name__ == "__main__":

    main()
