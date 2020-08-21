# Trello to Newsletter (2.0, or the Mailchimp edition)

MuMaLab people write a newsletter once a week. That was done in a pad so far, and then sent out manually. Not very convinient. Let's automate.

This is the second iteration of https://github.com/munichmakerlab/trello-newsletter, which sent out a plaintext email. This uses Mailchimp instead to send out a somewhat nicer email with all the Mailchimp craziness on top, and allows us to do proper newsletter contact management. Ideally, one would port this over to another open source self-hosted solution like Mailtrain, but that's for another day.

## Mailchimp setup

We require a Mailchimp template that serves as the basis of the newsletter. Create a template, and in that create a normal Text block, with a ``%TITLE%`` and ``%CONTENT%`` placeholder. That text block will be replicated and the placeholders replaced with the texts from trello.

## Trello Setup

Create a board in trello that serves as your newsletter creation center. We send out out newsletter weekly, so the script searches for a list inside that matches the name "YEAR-CW", like 2020-34 for the 34th calendar week of 2020. Each card in that list is a single headline in the newsletter. Currently, only the title and the description of a card are taken into consideration.

## Setup on server
* Clone repo
```
git clone git@github.com:munichmakerlab/trello-newsletter-mc.git
cd trello-newsletter-mc
```

* Install python requirements into a virtual environment
```
python3 -mvenv env
. env/bin/activate
pip install -r requirements.txt
```

* Get Trello API key and secret from https://trello.com/app-key
* Do that OAuth dance
```
export TRELLO_API_KEY=<API_KEY>
export TRELLO_API_SECRET=<API_SECRET>
export TRELLO_EXPIRATION=never
```

* Get Mailchimp API key and server id

* Copy `config.py.sample` and edit it
```
cp config.py.sample config.py
vi config.py
```

* Run the whole thing
```
python newsletter.py preview
python newsletter.py final
```

## License
Licensed under MIT license. See [LICENSE](LICENSE) for details.
