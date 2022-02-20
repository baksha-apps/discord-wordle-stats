# Wordle Ranking Discord Bot

Use this bot in your server to enrich your Wordle game play in Discord!

**Technical Notes**

- This project was primarily created to learn about Docker, GitHub Actions, Self-Hosting GH Runners, and testing in Python.
- It has many optimization points and areas of improvement before becoming a production ready Discord bot, but it works! 
- See [issues](https://github.com/baksha97/discord-wordle-stats/issues) to file a bug, optimization, or QoL enchancement!

## Features

### `$leaderboard`
Shows a ranking of the games played. 
- Ranked in order of priority: Average attempt won on, win percentage, and when you first started playing.  
![image](https://user-images.githubusercontent.com/15055008/153767740-c9b8b945-3d84-4f8c-92d9-6154e2cb9db4.png)


### `$today`
Shows a ranking of today's games played. 
- View today's solution by clicking on the spoiler tag!
- Ranked in order of priority: won on, and created date.
<img width="369" alt="image" src="https://user-images.githubusercontent.com/15055008/153735799-7415352a-1518-4f88-b026-021e334ae804.png">

### `$wordle <id>`
Shows a ranking of a played Wordle. 
`$wordle 230` = Wordle 230
- View that solution by clicking on the spoiler tag!
- Ranked in order of priority: won on, and created date.
<img width="403" alt="image" src="https://user-images.githubusercontent.com/15055008/153735776-def40efa-041c-47a1-b604-197ce5023f23.png">



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
