# Wordle Ranking Discord Bot
![integrity_workflow](https://github.com/baksha97/discord-wordle-bot/actions/workflows/integrity_workflow.yml/badge.svg)

Use this bot in your server to enrich your Wordle game play in Discord!

**Technical Notes**

- This project samples Docker, GitHub Actions, Self-Hosting GH Runners, and testing in Python.
- It has many optimization points and areas of improvement before becoming a "production" ready Discord bot, but it works super well! 
- See [issues](https://github.com/baksha97/discord-wordle-stats/issues) to file a bug, optimization, or QoL enchancement!

## Features

### `$today`
Shows a ranking of today's games played. 
- View today's solution by clicking on the spoiler tag!
- Ranked in order of priority: won on, and created date.
<img width="369" alt="image" src="https://user-images.githubusercontent.com/15055008/153735799-7415352a-1518-4f88-b026-021e334ae804.png">

### `$leaderboard`
Shows a ranking of the games played this month. 
- Ranked in order of priority: Average attempt won on, total games, win percentage, and when you first started playing.
<img width="474" alt="166006509-7aea71fc-f60c-4957-ae6d-01bb58720de0" src="https://user-images.githubusercontent.com/15055008/166008649-3ef53489-d184-4b63-a1e9-989261493c18.png">

### `$all-time-leaderboard`
Shows a ranking of all the games played. 
- Ranked in order of priority: Average attempt won on, total games, win percentage, and when you first started playing.
<img width="474" alt="image" src="https://user-images.githubusercontent.com/15055008/153767740-c9b8b945-3d84-4f8c-92d9-6154e2cb9db4.png">

### `$wordle <id>`
Shows a ranking of a played Wordle. 
`$wordle 230` = Wordle 230
- View that solution by clicking on the spoiler tag!
- Ranked in order of priority: won on, and created date.
<img width="403" alt="image" src="https://user-images.githubusercontent.com/15055008/153735776-def40efa-041c-47a1-b604-197ce5023f23.png">

### `$activity`
Shows player activity over time. 

<img width="406" alt="image" src="https://user-images.githubusercontent.com/15055008/166006788-2806ba3f-42ac-4c0f-86dd-911ac369b780.png">

## Contributing 
```mermaid
  journey
    title Contributing
    section Feature
      Branch feature/short-desc: 5: You
      Pull Request into patching: 5: You
      Review Pull Request: 4: Me, You
    section Patching
      Pull Request into develop: 5: Me
      Review: 5: Me
      Merge: 5: Me
    section Public Release
      Pull request into main: 5: Me
      Review: 5: Me
      Adjust Documentation: 5: Me
```

## Github Workflows
- Intergrity Workflow
  - Runs Tests
  - Linting (TBD)
- Deployment Workflows (deploys Docker images)
  - Google Compute Engine
   - Deploys to the GCP/GCR/GCE container project specified in the Repository secrets.    
  - Self Hosted
   - Deploys to the same machine running the GitHub action instead! Still using Docker.

## Credit
Thank you [@shawnfelix](https://github.com/shawnfelix) for starting it off.
