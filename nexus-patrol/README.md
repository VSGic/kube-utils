Deletes images from nexus repo not deployed in defined namespace
Images are deployed in nexus docker repo in subfolder with name of namespace
Add variables in nexus-parol.py and Dockerfile


docker build -t nexus-patrol .
docker run --rm -it nexus-patrol
