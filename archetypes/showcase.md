---
title: "{{ replace .File.ContentBaseName "-" " " | strings.FirstUpper }}"
description: ""
date: "{{ .Date }}"
# Page type: showcase — one tool or atlas, full width, no rail. Sections: What it is, How to get it
# (#download), What to cite, How it was built. Model: the DISTAL atlas page.
layout: "showcase"
---
