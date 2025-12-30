#!/bin/bash

UPLOAD=10 # How my GB to buy
BUFFER=4000 # How many points need to be retained after spending.

echo Collecing current points.
SPEND_JSON=$(mktemp)
curl -s -b mam_id=$MAM_COOKIE https://www.myanonamouse.net/jsonLoad.php?id=${MAM_USERID} > $SPEND_JSON

# Make sure we have a non-zero number of points to spend.
cat $SPEND_JSON 2>/dev/null| jq '.seedbonus' | grep '^[0-9][0-9]*\.\?[0-9]*$' > /dev/null

if [ $? -ne 0 ]
then
  echo Failed to get number of bonus points - aborting.
  cat $SPEND_JSON
  exit 1
fi

POINTS=`cat $SPEND_JSON 2>/dev/null| jq '.seedbonus'`
echo " => $POINTS"

UPLOADPOINTS=`expr $UPLOAD \* 500 + ${BUFFER}`
if [ $POINTS -gt $UPLOADPOINTS ]
then
  echo More than $UPLOADPOINTS points - buying ${UPLOAD}G of upload
  if [ $(date +%w) -eq 0 ]; then
      curl -s -b mam_id=$MAM_COOKIE "https://www.myanonamouse.net/json/bonusBuy.php/?spendtype=VIP&duration=max&_=$(date +%s)"
  fi
  curl -s -b mam_id=$MAM_COOKIE 'https://www.myanonamouse.net/json/bonusBuy.php/?spendtype=upload&amount=Max%20Affordable%20&_='$(date +%s) -H 'Referer: https://www.myanonamouse.net/store.php'
else
  echo " => Not enough points to buy ${UPLOAD}G of upload ($UPLOADPOINTS required)"
fi

rm $SPEND_JSON
