# An asynchronous python quart_application
# Quart_monolith_app
A quart application to fetch data from reddit with OAuth2 permissions. Uses celery for background tasks and Prometheus for monitoring health.<br/>
The code be easily extended to serve several use cases eg a reddit post schduling site;<br/>
To Run the code ensure you have python installed and pipenv package then simply run the following commands in the terminal while in the base directory of the pipfile;<br/><br/>
    **pipenv shell**<br/>
    **pipenv install**<br/><br/>
Then run the  app.py file, with this setup the code will run on htttp:localhost:5000<br/>
To run the background tasks run<br/><br/>
    **celery -A background worker --loglevel=INFO**<br/>
    **celery -A background beat --loglevel=INFO**<br/>


