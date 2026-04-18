from fastapi import FastAPI
from pydantic import BaseModel
from enum import Enum
from fastapi.middleware.cors import CORSMiddleware
from datetime import date
from datetime import datetime
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow everything (fine for development)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

job_id_counter = 0

class Status(str, Enum):
    applying = "not applied"
    applied = "applied"
    interviewing = "interviewing"
    rejected = "rejected"
    offer = "offer"
    all = "all"

class Field(str, Enum):
    date_newest = "date_newest"
    date_oldest = "date_oldest"

class Job(BaseModel):
    company: str
    position: str
    status: Status

def load_jobs():
    try: 
        with open("jobs.json", 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []
    
def save_jobs(jobs):
    with open("jobs.json", 'w') as f:
        json.dump(jobs, f, indent=4)

@app.get("/")
def home():
    return {"message": "Job Tracker API is running"}

@app.post("/jobs")
def add_job(job: Job):
    global job_id_counter

    jobs = load_jobs()
    job_dict = job.model_dump()
    job_dict["id"] = job_id_counter

    for key in job_dict:
        if key == "id":
            continue
        if job_dict[key] == "":
            return {"error": f"{key} not"}
        
        job_dict[key] = job_dict[key].title()

    job_id_counter += 1
    job_dict["date"] = datetime.now().isoformat()
    jobs.append(job_dict)
    save_jobs(jobs)

    return {"message": "Job added", "job": job_dict}

@app.put("/jobs/edit/{id}")
def update_job(id: int, updated_job: Job):
    jobs = load_jobs()

    for job in jobs:
        if job["id"] == id:
            updated_dict = updated_job.model_dump()

            for key, value in updated_dict.items():
                if key == "id":
                    continue
                if value is not None:
                    
                    if key in ["company", "role", "status"]:
                        job[key] = value.title()
                    else:
                        job[key] = value

            save_jobs(jobs)
            return {"message": "Job updated", "job": job}

    return {"error": "Job not found"}

@app.get("/jobs")
def get_jobs():
    jobs = load_jobs()
    return jobs


@app.delete("/jobs/delete/{id}")
def delete_job(id: int):
    jobs = load_jobs()
    for i, job in enumerate(jobs):
        if job["id"] == id:
            jobs.pop(i)
            save_jobs(jobs)
            return {"message": "Job deleted", "job": job}
    return {"error": "Job not found"}
    
@app.get("/jobs/{status}/{field}")
def filter_sort_jobs(status: Status, field: Field):
    jobs = load_jobs()
    if status.value != "all":
        filtered = [job for job in jobs if job["status"].lower() == status.value]
    else:
        filtered = jobs
    if field.value == "date_newest":
        ordered = sorted(filtered, key=lambda x: x["date"], reverse = True)
    elif field.value == "date_oldest":
        ordered = sorted(filtered, key=lambda x: x["date"], reverse = False)
    else:
        ordered = filtered
    return ordered

