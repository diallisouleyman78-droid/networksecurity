import sys, os

import certifi

from networksecurity.constants.training_pipeline import DATA_INGESTION_COLLECTION_NAME, DATA_INGESTION_DATABASE_NAME
from networksecurity.utils.ml_utils.model.estimator import NetworkModel
from networksecurity.utils.ml_utils.model.estimator import NetworkModel 
ca = certifi.where() # use the certifi package to get the path to the certificate authority bundle which is used to verify the SSL certificates when making requests to external APIs. This is important because we want to ensure that our application is secure and that we are not making requests to malicious APIs that could potentially steal our data or compromise our application. By using the certifi package, we can ensure that we are only making requests to trusted APIs that have valid SSL certificates.

from dotenv import load_dotenv
load_dotenv()
mongo_db_url = os.getenv("MONGO_DB_URL")
print(mongo_db_url)
import pymongo

from networksecurity.exception import NetworkSecurityException
from networksecurity.logging import logging
from networksecurity.pipeline.training_pipeline import trainingPipeline

from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import run as app_run
from starlette.responses import RedirectResponse
import pandas as pd

from networksecurity.utils.main_utils.utils import load_object

from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory="./templates")


client = pymongo.MongoClient(mongo_db_url, tlsCAFile=ca)
db = client[DATA_INGESTION_DATABASE_NAME]
collection = db[DATA_INGESTION_COLLECTION_NAME]

app = FastAPI()
origins = ["*"]  # Allow all origins, you can specify your frontend URL here

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
) # used to allow cross-origin requests from the frontend to the backend. This is important because we want to be able to make requests from the frontend to the backend without any issues related to CORS (Cross-Origin Resource Sharing). By allowing all origins, we are essentially allowing any frontend to make requests to our backend, which is fine for development purposes but should be restricted in production.



@app.get("/", tags=["authentication"])
async def index():
    return RedirectResponse(url="/docs")

@app.get("/train")
async def train_route():
    try:
        training_pipeline = trainingPipeline()
        training_pipeline.run_pipeline()
        return Response(content="Training pipeline executed successfully.", media_type="text/plain")
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
    

@app.post("/predict")    
async def predict_route(request:Request, file: UploadFile = File(...)):
    try:
        df = pd.read_csv(file.file)
        preprocessor = load_object("final_model/preprocessor.pkl")
        final_model = load_object("final_model/model.pkl")
        network_model = NetworkModel(preprocessor=preprocessor, model=final_model)
        print(df.iloc[0])
        y_pred = network_model.predict(df)
        print(y_pred)
        df['predicted_column'] = y_pred

        df.to_csv("prediction_output/output.csv")
        table_html = df.to_html(classes='table table-striped')
        return templates.TemplateResponse("tables.html", {"request": request, "table_html": table_html})
        
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e




if __name__ == "__main__":
    app_run(app, host="0.0.0.0", port=8000)    