---
title: "Usage statistics"
layout: "usage"
description: "Where and how often Lead-DBS is used: launches by country, month, hour of the day and tool."
# The charts (layouts/usage.html): a heading and one line each. The figures come from data/usage.json
# and the drawings from scripts/usage.mjs (README, "Usage figures").
charts:
  months: {title: "Eleven years of launches", text: "Launches per month."}
  countries: {title: "Where it runs", text: "A tile for each country, sized by its launches."}
  hours: {title: "Around the clock", text: "Launches by hour of the day, Central European Time."}
  tools: {title: "Which tool is started", text: "Lead-DBS is four tools; most sessions start in the main one."}
method: "A launch is one start of Lead-DBS; the same address counts once an hour. Countries are worked out from IP addresses, which are not published."
---
