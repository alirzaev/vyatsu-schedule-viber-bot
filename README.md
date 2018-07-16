# VyatSU schedule Viber bot

## Description

This app provides students that use Viber a convenient way to view group schedules.

What can this bot do:

- Schedule for today

- URL link to full schedule

- Rings schedule

- Convenient way to choose group

The link for starting converstion with bot can be found on [vyatsuschedule.ru](https://vyatsuschedule.ru)

## Running app

### Required environment variables

`MONGODB_URI=<uri>` - defines the uri for MongoDB cluster.

`PORT` - port on which listen requests.

`TOKEN` - token for Viber bot.

`WEB_HOOK_URL` - URL to which Viber will send requests.

`API_URL` - URL of VyatSU schedule API server.

### Optional environment variables

`DEBUG` - manage logging level. `0` - only errors and higher, `1` - info messages and higher.

### Server

`gunicorn -b 0.0.0.0:$PORT bot:app`

