# Twitch Monitor


### Functions
- display Live-Chat
- display Event-Stream in real time, showing
    - Whispers
    - Follows
    - Viewer Count changes
    - Subscriptions
    - Cheers
    - Donations (*future*, integrating tbd Thrid-Party)


### Flow Outline
1. [Authenticate](https://dev.twitch.tv/docs/authentication/) to Twitch according to OAuth
2. Subscribe to relevant Twitch [WebHook-Events](https://dev.twitch.tv/docs/api/webhooks-reference/)
    (needed for Follows, Viewer Count changes)
3. Start Web-Socket connection for Twitch [PubSub-Topics](https://dev.twitch.tv/docs/pubsub/)
    (needed for Whispers, Subscriptions, Cheers)
4. Redirect User to website
5. Start Web-Socket connection between website and server to push new
    data continuously


### Design Rationale
- Website should be as small as possible
- Server needs to combine different sources and types of communication
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
