## TwitterAPI/dash/plotly, A simple example

This is a simple example of TwitterAPI/dash/plotly deployment on server using flask, gunicorn and docker

Twitter API Credentials: Get credentials from https://developer.twitter.com and put them in 'config.ini' file

### Commands
```
1. `git clone https://github.com/mazqoty/Dashboard-Twitter-Analytics.git`
2. Create Environment: 'python -m venv <environment_name>'
3. Activate Environment: `source <environment_name>/bin/activate` or `source <environment_name>/Scripts/activate.bat`
4. Install Dependencies: `pip install -r requirements.txt`
5. Run: `python appTabs.py
Then, If you built it localy visit: 127.0.0.1:8050
```
For deployment on server use gunicorn and docker:
```
Build via docker compose: `docker-compose up`
To Rebuild: `docker-compose down && docker-compose up --build`
If you built it via docker-compose visit: http://127.0.0.1:5000/
visit: http://127.0.0.1:5000/
```

### See it on [Render](https://dashboard-twitter-analytics.onrender.com/)

<table style="width:100%">
  <tr>
    <td><img src="https://i.imgur.com/ZT3g72N.jpg" width="400px" height=225px/></td>
    <td><img src="https://i.imgur.com/M6FcMEz.jpg" width="400px" height=225px/></td>
    <td><img src="https://i.imgur.com/I6SdTYe.jpg" width="400px" height=225px/></td>
    <td><img src="https://i.imgur.com/XA5lU1F.jpg" width="400px" height=225px/></td>
  </tr>

</table>

