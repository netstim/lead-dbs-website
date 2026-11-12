---
title: "Usage statistics"
layout: "usage"
description: "Recorded Lead-DBS access requests by country, month, server-clock hour and tool. These are not counts of people or installations."
charts:
  months: {title: "Recorded activity over time", text: "Access requests per month, counting each address once per recorded clock hour. Hollow dots mark partial months; gaps mean no recorded observations, not verified zero activity."}
  countries: {title: "Where requests were recorded", text: "Country totals estimated from network addresses across the reporting period. A network location does not establish where a researcher works."}
  hours: {title: "Requests by recorded hour", text: "Server clock (timezone unverified), in the reporting year to date."}
  tools: {title: "Requests by tool", text: "Reporting year to date. Each address counts once per hour per tool, so this denominator differs from the overall request count. Unknown tools remain included."}
  all: {title: "Every country", text: "Program download requests and access requests since {since}, most program requests first. These are different metrics, not counts of users."}
method: "These are recorded access requests, not people, installations or sessions. Overall totals count each address once per recorded clock hour; shared networks can merge people and changing addresses can count one person more than once. Automated requests have not been excluded. Countries are estimated using an offline database; historical locations may differ. Only aggregate statistics are published. Observed date boundaries do not prove uninterrupted collection."
next:
  - {page: "/about/"}
  - {page: "/download/"}
---
