---
title: "Usage statistics"
layout: "usage"
description: "Where and how often Lead-DBS is downloaded and used: launches by country, month, hour of the day and tool."
# The charts (layouts/usage.html): a heading and one line each. The figures come from data/usage.json
# and the drawings from scripts/usage.mjs (docs/home-and-media.md, "Usage figures").
charts:
  months: {title: "Eleven years of launches", text: "Launches per month."}
  countries: {title: "Launches by country", text: "Tile area shows the number of launches in each country."}
  hours: {title: "Launches by hour", text: "Launches by hour of the day, Central European Time."}
  tools: {title: "Launches by tool", text: "Four tools are tracked: Lead-DBS, Lead Group, Lead Connectome and Lead Anatomy. Most launches are of Lead-DBS."}
  # the table of every country ({since}: the first year of the figures)
  all: {title: "Every country", text: "Downloads and launches since {since}, most downloads first."}
method: "A download is one download of Lead-DBS from one address on one day, without bots. A launch is a start of Lead-DBS, counted at most once per IP address per hour. Countries are inferred from IP addresses; the addresses are not published."
next:
  - {page: "/about/"}
  - {page: "/download/"}
---
