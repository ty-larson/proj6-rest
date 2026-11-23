# Project 6: Brevet Time Calculator REST API Service

**Author:** Ty Larson  
**Email:** tyl@uoregon.edu  

## Overview
A multi-container Docker application for CIS 322 that calculates ACP brevet control times, stores them in MongoDB, exposes the stored times via a Flask-RESTful API service, and consumes the endpoints in a separate PHP web container.

## Services & Ports
- **Brevet Calculator (`brevets` — `http://localhost:5002`):** Flask web app to calculate control open/close times, save entries to MongoDB (`Submit`), and view stored records (`Display`).
- **REST API (`laptop-service` — `http://localhost:5001`):** Flask-RESTful service exposing stored control times in JSON and CSV formats with optional `?top=k` ascending chronological filtering:
  - `/listAll`, `/listAll/json`, `/listAll/csv`
  - `/listOpenOnly`, `/listOpenOnly/json`, `/listOpenOnly/csv`
  - `/listCloseOnly`, `/listCloseOnly/json`, `/listCloseOnly/csv`
- **Consumer Website (`website` — `http://localhost:5000`):** PHP/Apache container querying `http://laptop-service` to display JSON and CSV responses.
- **Database (`db`):** MongoDB (`mongo:5.0`) storing submitted control times.

## How to Run
```bash
cd DockerRestAPI
docker compose up --build