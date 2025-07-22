import streamlit as st
import requests
import random
import urllib.parse
from datetime import datetime
import os
from pathlib import Path
import platform
import pandas 
import streamlit.web.cli as stcli
import os, sys


def resolve_path(path):
    resolved_path = os.path.abspath(os.path.join(os.getcwd(), path))
    return resolved_path


if __name__ == "__main__":
    sys.argv = [
        "streamlit",
        "run",
        resolve_path("get_image.py"),
        "--global.developmentMode=false",
    ]
    sys.exit(stcli.main())