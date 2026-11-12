---
title: "{{ replace .File.ContentBaseName "-" " " | title }}"
description: ""
# Page type: hub — a menu group's own page, full width, no sidebar: a paragraph, the group's pages, at most two short sections.
# The list of the group's pages is the shortcode below: set menu to the group's identifier in hugo.toml
# [menus.main] (the build stops until it names one).
layout: "hub"
---

One paragraph on what the group holds.

{{"{{"}}< resource-index menu="" >}}
