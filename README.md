# 510_Lab_Final Project: Intelligent Rehab Assistant
### Overview
Revolutionizing rehabilitation with a platform that combines real-time wearable data and AI cahtbot to offer personalized guidance and clear visualizations, ensuring expert-level recovery insights for every patient.

### Technology Used
1. Firebase real-time database
2. LLM powered assistant
3. Data analytics and visualization

### Problems to solve
1. Reducing the high costs and time demands of physical therapy for long-term rehab patients by providing essential self-rehab data for better communication with therapists.
2. Simplifying complex rehabilitation data for patients, making it easier to understand and apply, thus enhancing the recovery experience.

### How to run
```
python -m venv venv
source env/bin/activate
pip install -r requirements.txt
```
### Reflections
##### What I learned
1. Developed skills in creating and managing a cloud database (e.g., Firebase real-time DB) and visualizing data on a website, including database credential management and data formatting.
2. Learned how to tailor LLM assistant answer. For example, I let the assistant serve as a professional physical therapist and provide answer in bullet points, with additional requirements of explaining data from three rehabilitation aspects.
##### What problems I faced
1. I tried hard adding the system prompt for an AI chatbot to let it has a default role on this website and answer the professional questions. (soleved)
2. Faced limitations with streamlit's data visualization customization options, particularly in adjusting colors and display preferences. (unsolved)

### Project Asset
- app.py: streamlit application for WebApp
- [Azure WebApp Link](https://peisyc-techin510-final.azurewebsites.net/)
