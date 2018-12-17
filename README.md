# VyatSU schedule Viber bot

This application provides students that use Viber a convenient way to view group schedules.

What can this bot do:

- Schedule for today.

- URL link to full schedule.

- Rings schedule.

- Convenient way to choose group.

The link for starting conversation with bot can be found here: [vyatsuschedule.github.io](https://vyatsuschedule.github.io)

Designed for [Vyatka State University](https://www.vyatsu.ru)

## Running app

### Required environment variables

`MONGODB_URI=<uri>` - URI to MongoDB database of format `mongodb://<user>:<password>@<host>:<port>/<database>`. You have to specify the database name.

`PORT` - port on which listen requests, defaults `80`.

`TOKEN` - token for Viber bot.

`WEBHOOK_URL` - Webhook for Viber bot.

`API_URL` - URL to VyatSU schedule API server.

`WEBAPP_URL` - URL to VyatSU schedule web application.

### Optional environment variables

`DEBUG` - manage logging level. `0` - only errors and higher, `1` - info messages and higher.

### Server

`gunicorn -b 0.0.0.0:$PORT bot:app`

