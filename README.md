# Twitch Monitor

> The amount of control you have if you can monitor activity is amazing.


### Functions
- display Live-Chat
- display Event-Stream in real time, showing
    - Follows
    - Subscriptions
    - Cheers
    - Donations (*future*, integrating tbd Third-Party)
- maybe more, who knows?!


### First-Time Setup
1. make sure you have at least Python v3.6 installed (`python --version`)
1. install dependencies via `pip install -r requirements.txt`
1. copy `settings-example.yaml` to `settings.yaml` and fill in the
    placeholders inside the copied file


### How to Use
1. run server.py
1. open the address written in the console on the same machine as is
    running the application
1. authorize application to access your Twitch-Account
1. use the Web-Site (at this point you could also open the address on
    a different device)


### Flow Outline
1. [Authenticate](https://dev.twitch.tv/docs/authentication/) to Twitch
    according to OAuth
1. Redirect User to website
1. Start Web-Socket connection between website and server to push new
    data continuously
1. Start to continuously query relevant functions of the [Twitch-API](https://dev.twitch.tv/docs/api/reference/)
    to recognize changes and send them as an update in the activity-stream


### Design Rationale
- Website should be as small as possible
- Server combines different sources and types of communication
- Website gets uniform data in form or pre-rendered HTML which gets
    added to site dynamically


### Used Libraries
- [aiohttp 3](https://aiohttp.readthedocs.io/en/stable/index.html) for
    running the server which interfaces with the Twitch API and the
    website
- [aiohttp_jinja2](https://aiohttp-jinja2.readthedocs.io/en/stable/index.html)
    for rendering website elements on the server to HTML
- [Bulma](https://bulma.io/documentation/overview) to have a nice, easy
    to adapt design for the website


### Quick, Important Notes on the Code
- access runtime-data which needs to be shared between different parts /
    different calls to a method:
    ```py
    app.get(app_config_key.FOLLOWERS_STORE)
    ```
- render a HTML-template (stored in views/templates)
    ```py
    app[app_config_key.JINJA_ENV]
        .get_template('template-file-name.jinja2')
        .render(placeholder_key1=value1, placeholder_key2=value2)
    ```
- write to the Server's console
    ```py
    logging.info('Important info')
    logging.error('ALARM!')
    ```
