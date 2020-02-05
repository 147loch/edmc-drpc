# EDMC-Discord-Presence

A plugin for [Elite Dangerous Market Connector](https://github.com/Marginal/EDMarketConnector) that enables [Discord Rich Presence](https://discordapp.com/rich-presence) for [Elite Dangerous](https://www.elitedangerous.com/)

Show your current location to your friends on Discord from your user profile.

![Presence Screenshot](EDMC_Discord_Presence_1.png?raw=true)

## Installation

1. [Install EDMC according to instructions](https://github.com/Marginal/EDMarketConnector)
2. Download the latest version of the plugin from [here](https://github.com/SayakMukhopadhyay/EDMC-Discord-Presence/releases). Make sure to download the release `.zip` and not the source code bundle.
3. Open Elite Dangerous Market Connector and go to File -> Settings. Then browse to the plugins tab:

![Plugin Installation](https://i.imgur.com/eogKt9n.png)

4. Click "Open" to open the plugins directory.
5. Open the Zip file we have downloaded and drag the folder from within into the plugins directory
6. Restart EDMC for the plugin to take effect.

To check if the plugin is loaded correctly, go File -> Settings. Then browse to the plugins tab. `DiscordPresence` must be listed under `Enabled Plugins`

![Plugin Installation Check](https://i.imgur.com/0rmD2I5.png)

## Options

You can set the plugin to not show your game data. Go to File -> Settings. Under the `DiscordPresence` tab, check `Disable Presence`

![Plugin Disable](https://i.imgur.com/B2Lsfg2.png)

## Contributing

If you find a bug, please create an issue in the issue tracker in Github, properly detailing the bug and reproduction steps.

If you are willing to contribute to the project, please work on a fork and create a pull request.

## Credits

For the CMDRs by a CMDR. Created by [CMDR Garud](https://forums.frontier.co.uk/member.php/136073-Garud) for an awesome gaming community. 
A big thanks to [Jonathan Harris (Marginal)](https://github.com/Marginal) for creating the Python boilerplate code for the Discord Rich Presence SDK. Without his input, the plugin would not have been done.

Translate to french, migrate from python2 to python3 by [Poneyy](https://github.com/Poneyy)

## License

Developed under [Apache License 2.0](https://choosealicense.com/licenses/apache-2.0/).
