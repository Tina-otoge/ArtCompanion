# ArtCompanion
A discord bot that helps you liking pictures posted outside of Discord from Discord

Using ArtCompanion you can use Discord to engage with pictures from other websites.
For example, once you have linked your Twitter account, you can like and retweet tweets
posted on Discord simply by clicking on the :hearts: and :repeat: emoji reactions.

ArtCompanion is also able to link "feeds" to a Discord channel, so you can get your
Pixiv feed or a Twitter search periodically posted to a Discord channel.

![screenshot](https://i.imgur.com/lwmPeBq.png)

## Motivation

By browsing arts directly from Disocrd, I'm able to digest the massive influx of new
content I get easier. Scrolling a Discord channel is easier for me than using the Pixiv
or Twitter app.
By engaging with the content directly using reaction, I'm able to show my appreciation
to artists without the effort of opening the link in the app.

## Configuration

If you want to run the bot locally, you'll need to put your credentials in the
`config.json` file (should be created on launch with empty values) like so
```js
{
  "discord_token": "XXX.XXX.XXX",
  "twitter_key": "XXX",
  "twitter_secret": "XXX",
  "error_webhook": "https://discord.com/api/webhooks/XXX/XXX" // optional, to get error messages in a Discord channel
}
```

## Contributing
If you are not a dev and want to contribute you can report bugs or suggest new features by
opening new **issues**.

If you are a dev and want to contribute you can look at the opened issues, pick one and submit
a PR.
