# Wekan import GitKraken Boards

Shitty script to import your GitKraken boards into your own Wekan instance.
It uses the API because Wekan's actual official CSV importer doesn't work.
In some places I guessed the API endpoints because the documentation sucks donkey ass.

**This script ONLY works when the user is an admin user. Not sure why.**

## Usage

```
pip3 install -r requirements.txt
python src/cli.py --url https://wekan.example.com -u admin -p hunter2 -b "My Board" -f MyBoard.csv
```

## Features

- Columns (Wekan calls these Lists)
- Cards (description/labels)

Yeah, that's it. Empty columns won't be imported, this is a GitKraken Boards limitation.

## Rant

GitKraken Boards doesn't even export the comments on a card. They do export the milestones, but I can't be bothered to implement those. I guess I could parse the GitKraken Boards checklists and add those as a 'native' checklist to Wekan, but, once again, I don't care that much about it because they at least show up as markdown checklists in the description.

This script is the result of me trying to move my GitKraken boards to Wekan, and getting increasingly frustrated by both GitKraken Boards and Wekan dropping the ball with their import/export features. Wekan can't even import their own example CSV! Wekan is an open-source project though, so I guess I can't be too hard on them. That said, I would've expected better from a project with almost 18k stars. (Then again, the installation was a massive pain too.)

GitKraken Boards on the other hand is just sad. They discontinue their product just when it was about to actually be pretty good. Shit, they could've just kept it on life-support and not anything and I would've been happy. Their exporter is missing a lot of features, so a lot of history will be lost with them shutting it down. I never paid them a dime though, and I am glad that I didn't.
