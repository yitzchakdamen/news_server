#!/bin/bash

# התקנת כל הספריות
pip install -r requirements.txt

# הורדת דפדפנים עם כל התלויות
playwright install chromium
