# HowLongToBeat Service

This is the backend microservice for HowLongToBeat.  
The service runs on port <code>8102</code> by default.

## 🌐 Endpoints

| Method | Endpoint               | Description                                        |
| ------ | ---------------------- | -------------------------------------------------- |
| GET    | /options?name=\<NAME\> | Get a list of game options matching the given name |
| GET    | /info?id=\<ID\>        | Get detailed information about a game by ID        |

