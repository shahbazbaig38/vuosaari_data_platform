from pathlib import Path
import toml

PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_FILE = PROJECT_ROOT / "config.toml"

with open(CONFIG_FILE, "r") as f:
    config = toml.load(f)

    API_CONFIG = {
        "url": config["BASE_URL"],
        "params": {
            "Record": config["Record"],
            "SearchString": config["SearchString"],
            "ReportingGroup": config["ReportingGroup"],
            "StartTime": config["StartTime"],
            "EndTime": config["EndTime"]
        },
    }

DB_CONFIG = config["postgresql"]