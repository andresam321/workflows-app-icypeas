from flask import Flask
from workflows_cdk import Router
from dotenv import load_dotenv
import os
load_dotenv(dotenv_path=".env")
print("LOADED KEY:", os.getenv("ICYPEAS_API_KEY"))
# Create Flask app
app = Flask(__name__)
router = Router(app)

if __name__ == "__main__":
    router.run_app(app)