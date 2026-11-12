---
title: "Made with Lead-DBS"
linkTitle: "Made with Lead-DBS"
description: "Renders by the Lead-DBS team and figures from published papers that used Lead-DBS."
# The page shows the published figures first (data/gallery.yaml, images in static/gallery/), then
# the lab's own renders (files in assets/images/renders/).
renders_title: "Renders by the Lead-DBS team"
renders_text: "Rendered with BrainDeer from the open Lead Tutor dataset, with the DISTAL atlas and the 100 µm 7 tesla MRI of an ex vivo brain. The analysis pictures use example stimulation settings and simulated outcome scores: they are illustrations, not findings."
renders:
  # caption: printed under the picture. Say how many patients the picture shows (the BrainDeer
  # renders of 2026-11-10 show nine of the ten Lead Tutor patients; the older analysis pictures show all ten).
  - file: "cohort-hero.jpg"
    alt: "The electrodes of nine Lead Tutor patients converging on the subthalamic nucleus, seen from the right and above, with the internal pallidum and red nucleus over a 7 tesla MRI slice"
    caption: "Nine of the ten Lead Tutor patients: all 18 electrodes in MNI space, converging on the subthalamic nucleus (orange), with the internal pallidum (green) and red nucleus (red)."
  - file: "cohort-front.jpg"
    alt: "The same nine patients from the front: two fans of electrodes, one on each side, over a 7 tesla MRI slice"
    caption: "The same nine patients from the front: one fan of electrodes on each side."
  - file: "cohort-top.jpg"
    alt: "The nuclei and the nine patients' electrodes seen from above, front at the top, on a 7 tesla MRI slice"
    caption: "Seen from above, front at the top: the shapes of the nuclei on the 7 tesla anatomy, with the electrodes of the nine patients."
  - file: "lead-closeup.jpg"
    alt: "Close-up of one directional electrode with segmented contacts entering the subthalamic nucleus, the red nucleus behind it"
    caption: "One directional electrode of one of these patients, entering the subthalamic nucleus."
  - file: "cohort-black.jpg"
    alt: "The nuclei floating on black, with the electrodes of the nine patients descending into the subthalamic nucleus on both sides"
    caption: "The nine patients' electrodes and the nuclei without the MRI behind them."
  - file: "pathway-activation.jpg"
    alt: "Example analysis on the Lead Tutor dataset: two electrodes with their stimulation volumes in blue and the activated fibre pathways in red and white"
    caption: "Example analysis on the Lead Tutor dataset, with example stimulation settings: two electrodes, their stimulation volumes (blue) and the fibre pathways they activate."
  - file: "pathway-activation-2.jpg"
    alt: "Example analysis on the Lead Tutor dataset: the activated pathways seen from closer"
    caption: "The same example analysis, seen from closer."
  - file: "fiber-filtering.jpg"
    alt: "Example analysis on the Lead Tutor dataset: fibre tracts coloured by their association with simulated outcome scores"
    caption: "Example analysis on the ten Lead Tutor patients, with simulated outcome scores: fiber filtering finds the tracts whose stimulation goes together with better (or worse) improvement across the group, and colours them accordingly."
  - file: "fiber-filtering-wide.jpg"
    alt: "Example analysis on the Lead Tutor dataset: the fibre filtering result from a wider angle"
    caption: "The same fiber filtering example from the other side."
papers_title: "Figures from papers that used Lead-DBS or Lead-OR"
papers_text: "Figures from open-access papers whose authors used Lead-DBS, or its sister tool Lead-OR for surgery (marked under the figure), reproduced under their licences."
papers_empty: "The first figures are being collected. To suggest one from your paper, write to us through the [contact page](/contact/)."
aliases: ["/helpsupport/knowledge-base/screenshots/"]
keywords: ["gallery", "figures", "renders", "pictures", "images"]
# the picture shown when the page is shared (head.html)
share: "images/renders/lead-closeup.jpg"
# pages related to this one, in the sidebar (layouts/_partials/sidebar.html)
related:
  - "/about/publications/"
  - "/helpsupport/knowledge-base/atlasesresources/distal-atlas/"
  - "/download/"
# the cards at the end of the page (layouts/_partials/next-steps.html)
next:
  - {page: "/helpsupport/knowledge-base/lead-dbs-methods/", text: "What Lead-DBS does, with manual chapters and papers"}
  - {page: "/about/publications/", text: "The papers behind it"}
  - {page: "/contact/", name: "Show us your figure", text: "Made a figure with Lead-DBS? Tell us"}
---
