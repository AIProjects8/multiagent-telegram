# Multiagent Telegram Bot
Welcome in the Multiagent Telegram Bot!

If you want to run multiple agents in single telegram bot - this is the right place. You can check existing agents (Weather, Clock, YouTube) and then create your own. Let's get to work!

### Prerequisites

Make sure you've installed Python 3.12+ and latest docker.

### Configuration

Copy `.env.example` to `.env` and fill API keys.

### Local debugging

Run the database:
```
docker compose up -d postgres
```

Debug the application by using configuration from the `./vscode/launch.json` file.

### Run on remote host

```
cd multiagent-telegram
./deploy.sh
```

Make sure to run `./deploy.sh` each time you pull a new version.

### Usage

#### Switch between agents

Write `agent` + agent name to switch to specific agent, for example:

`agent weather` - switches to weather agent
`agent weather what is the weather in Paris` - switch to weather agent and check the weather in Paris

#### Available agents

- `default` - default agent connected with ChatGPT model form the configuration
- `weather` - weather agent describing weather for the next 24 hours for specific city inserted explicitly or taken from the configuration
- `clock` - check time for specific city or retrieved from the configuration. It can also check the time of sunset and sunrise
- `youtube` - generated summary from transcription for pasted youtube link. The user can also ask questions to the transcription or generated summary.
- (in progress) `calendar` - get information for meetings located in multiple calendars: Google or Microsoft

### License

Licensed under CC BY-NC 4.0.
