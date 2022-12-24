# Generate IRR filtering for Mikrotik Routing

## Install

### Requirements

`pip install -r requirements.txt`

On Ubuntu:

`apt-get install bgpq3 bgpq4`

### Setup

passwordless ssh connection to your router (see https://wiki.mikrotik.com/wiki/Use_SSH_to_execute_commands_(public/private_key_login) )


In places where you want the input rule create a rule with `input-rule` as the comment
Similarily for output rule `output-rule`


The script will then update these rules each time it is run.


Note: there is a potential for a race condition if you are re-ordering rules while this script is running, so if your otherwise changing your route filters don't run this script at the same time.
