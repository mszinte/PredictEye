## To deploy a single page app

# With Heroku (adapted from [here](https://dash.plotly.com/deployment))
---
1. make an [heroku](https://signup.heroku.com/signup/dc) account
2. install git and [virtualenv](https://virtualenv.pypa.io/en/latest/installation.html)
3. create a new folder for your project and cd to it
4. initializes a git repo `git init` 
5. create a virtual environment `virtualenv venv`
6. initiate the virtual environement `source venv/bin/activate`
5. install your desired module `pip install` 
6. install gunicorn `pip install gunicorn`
`pip install numpy==1.19.5 matplotlib sklearn scipy==1.5.4 pandas==1.1.5 dash plotly h5py gunicorn`
7. create your app.py file with a special line `server = app.server` after the call of app
8. create a gitignore 
`venv
*.pyc
.DS_Store
.env`
9. create a Procfile with `web: gunicorn app:server`
10. create a requirement.txt with `pip freeze > requirements.txt`
11. login to heroku `heroku login`
12. create heroku repo `heroku create my-app`
13. add all files to git `git add .`
14. Commit the files `git commit -m "your message"`
15. deploy the app on heroku `git push heroku master`
16. run the app with a dyno `heroku ps:scale web=1`
17. view your app [https://my-app.herokuapp.com](https://my-app.herokuapp.com)
18. repeat steps 12->16 to upload your changes
