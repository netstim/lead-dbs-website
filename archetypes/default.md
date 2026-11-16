---
title: "{{ replace .File.ContentBaseName "-" " " | strings.FirstUpper }}"
description: ""
date: "{{ .Date }}"
# Page type: doc (README, Page types). Optional "Related" links at the end:
# next:
#   - {page: "/path/"}
---
