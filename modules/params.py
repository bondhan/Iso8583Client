import argparse

def get_parser():
    parser = argparse.ArgumentParser(description="Process a JSON file.")
    parser.add_argument("--file", type=str, required=True, help="Path to the JSON file")
    parser.add_argument("--host", type=str, required=False, help="Server IP Address")
    parser.add_argument("--port", type=str, required=False, help="Port")

    return parser
