#!/bin/sh
# This script generates a ssh key for a single repository
# and adds a custom configuration to the users (not global) ssh config file,
# and outputs the public key for you to copy and paste as the repo deploy key
# and outputs the url for you to clone the repo on the machine.
# Github docs ref:
# https://docs.github.com/en/developers/overview/managing-deploy-keys#using-multiple-repositories-on-one-server
#
# 1. Add the script to the user account of the machine. The home directory is fine.
# 2. Make the script executable by running the following command as the user:
# chmod u+x generateDeployKey.sh
# 3. Run script like `./generateDeployKey.sh REPO_OWNER_NAME REPO_NAME` Note the space between owner and repo name. Example:
# ./generateDeployKey.sh yourname hello_world
# If you make a mistake with what you pass in, you can remove change from your ~/.ssh/config file
# by deleting the most recent "New Key Generated on...." and deleting the related .pub and private keys


# Check if user passed in both parameters
if [ -z "$1" ] || [ -z "$2" ]
then
  echo "Make sure to pass in both parameters REPO_OWNER_NAME and REPO_NAME. Example:"
  echo "./generateDeployKey.sh yourname hello_world"
else
  REPO_OWNER_NAME=$1
  REPO_NAME=$2
  KEY_PATH=~/.ssh/id_rsa.$REPO_NAME
  echo "Generating ssh key At ${KEY_PATH}"
  ssh-keygen -t rsa -N "" -f ~/.ssh/id_rsa.${REPO_NAME}
  echo "Your ssh deploy key is:"
  PUB_KEY_PATH=$KEY_PATH".pub"
  cat $PUB_KEY_PATH

  echo "Here is your hostname's alias to interact with the repository using SSH:"
  echo "git clone git@github.com-$REPO_NAME:$REPO_OWNER_NAME/$REPO_NAME.git"
fi
