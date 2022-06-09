# spam-ham classifier. 
This project is in development phase 

# to install this project 
- conda crate -n ai_api python=3.9 -y

# to run this project write this in root directory 

uvicorn app.main:app --reload 

# it will be running on port 8000 

# Run this with docker 

docker build -t spam-sms -f DockerFile .

docker run -p 8000:8000 spam-sms

# another way is just run 
docker compose up --build

# to push this image 
docker compose push 

# to run image download from docker 
docker run -p 8000:8000 sanjeev49/spam_ham_classifier_lstm