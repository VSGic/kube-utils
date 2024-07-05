FROM python:3.11-slim
ENV PATROL_TOKEN=<your kubernetes token>
ENV PATROL_HOST=https://<your control node>:6443
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY ./app .
CMD ["python", "nexus-patrol.py"]
