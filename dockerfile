FROM python:3.7
WORKDIR /app
EXPOSE 8501
COPY . .
RUN pip3 install -r requirements.txt
ENTRYPOINT ["streamlit", "run", "aat_project.py", "--server.port=8501", "--server.address=0.0.0.0"]
