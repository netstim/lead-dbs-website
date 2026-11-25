---
# /usage/ (the usage statistics) was taken off the site for now; it forwards here.
aliases: ["/usage/"]
# The home page. Every text and list on it is set here; the layout is layouts/home.html.
# Version, date, requirements and license come from data/release.yaml, events from data/events.yaml.
# Pictures are file names in assets/images/renders/ (replace a file there, or change a name here).
# Sections take the height of their content: a longer text simply makes its section taller.
title: "Lead-DBS"
description: "Lead-DBS is an open-source toolbox that localizes deep brain stimulation electrodes on MRI and CT and maps their effects on brain networks."
date: "2014-06-17T12:22:42"
lastmod: "2026-11-12"
# The scroll story: the opening, the localization and the three feature cards as steps beside one drawing
# that stays on the screen and changes with them (layouts/_partials/home-story.html, assets/js/story.js).
# Its words are `hero`, `localize` and `features.cards` below. `false` brings back the clip, the electrode
# insertion and the cards. story_note stands under the drawing: say what is data and what is not.
story: true
hero:
  title: "Open-source DBS imaging toolbox"
  lead: "For electrode localization, stimulation modeling, and connectivity analysis."
  primary: {label: "Download Lead-DBS"}
  # the second action is for newcomers; the manual (another site, marked ↗) follows it as a third, quieter link
  secondary: {label: "First steps", url: "/helpsupport/first-steps/"}
  manual: {label: "Manual", url: "/manual/"}
  # The clip behind the words: files in static/media/, poster in assets/images/renders/.
  # One directional lead in the subthalamic nucleus, the camera swaying slowly (±18°, 32 s loop),
  # framed on a black 16:10 canvas with the render on the right (see docs/home-and-media.md, "hero clip").
  # Each size comes as AV1 (the browser takes it when it can play it) and as H.264 (every other browser):
  # video_av1: 1600 px AV1, for windows from 1024 px; video_hevc: the same in HEVC, for desktop browsers
  # without AV1 (Safari on older Macs); video_medium_av1: 1280 px AV1, windows from 640 px;
  # video: 1280 px H.264, windows from 640 px without AV1; video_phone_av1 and video_phone: a square
  # crop around the render, for phones (loaded only when play is pressed).
  video_av1: "media/hero-lead-stn-av1.mp4"
  video_hevc: "media/hero-lead-stn-hevc.mp4"
  video_medium_av1: "media/hero-lead-stn-1280-av1.mp4"
  video: "media/hero-lead-stn-1280.mp4"
  video_phone_av1: "media/hero-lead-stn-phone-av1.mp4"
  video_phone: "media/hero-lead-stn-phone.mp4"
  poster: "hero-lead-stn-poster.jpg"
  # proof: the end of the quiet line under the buttons (after the version, MATLAB and the license, from
  # data/release.yaml): things a visitor can check, here the three papers that describe it.
  # Each part is Markdown and stays whole; a narrow screen breaks the line between parts. A number added
  # here needs its source and date.
  proof:
    - "*NeuroImage* 2015, 2019, 2023"
  alt: "Close-up of one directional DBS electrode with segmented contacts in the subthalamic nucleus (orange), the red nucleus behind it, over a 7 tesla MRI slice"

# Electrode localization, with the scroll moment: the leads move into place as the section scrolls by.
# The frames are in static/media/insertion/ (see docs/home-and-media.md, "The electrode insertion").
localize:
  title: "Electrode localization from MRI and CT"
  text: "Reconstruct electrode positions from postoperative imaging and view individual patients or cohorts in 2D and 3D."
  # the steps of the diagram (assets/diagrams/localize.mmd holds the same four words), read out as a list
  steps:
    - {name: "Coregister", value: "postoperative to preoperative imaging"}
    - {name: "Normalize", value: "to template space"}
    - {name: "Localize", value: "trajectories and contacts"}
    - {name: "Visualize", value: "in 2D and 3D"}
  link: {label: "Watch the walkthrough videos", url: "/helpsupport/knowledge-base/walkthrough-videos/"}

# Three things it does besides localization: a compact row of three. Each card leads to its part of the
# overview of everything Lead-DBS does (anchor: an id on that page), "more" beside the heading to its top.
# "data": the slim band under the cards for the atlases and data hub (page): its render (image, cut to
# crop: x0, y0, x1, y1 in the file's pixels), one line (text), and links to its catalog pages.
features:
  title: "What Lead-DBS does"
  more: {label: "All methods", url: "/helpsupport/knowledge-base/lead-dbs-methods/"}
  data:
    page: "/helpsupport/knowledge-base/atlasesresources"
    text: "Most are in MNI space and included with Lead-DBS."
    image: "head-data.jpg"
    crop: [1500, 150, 2950, 1250]
    links:
      - {page: "/helpsupport/knowledge-base/atlasesresources/atlases-2", label: "Subcortical atlases", text: "Atlases by structure and disease."}
      - {page: "/helpsupport/knowledge-base/atlasesresources/cortical-atlas-parcellations-mni-space", label: "Cortical parcellations", text: "Parcellations for connectivity analyses."}
      - {page: "/helpsupport/knowledge-base/atlasesresources/normative-connectomes", label: "Normative connectomes", text: "Structural and functional connectivity datasets."}
  cards:
    - title: "Stimulation modeling"
      text: "Model electric fields, activated tissue and pathways."
      anchor: "stimulation"
      image: "pathway-activation.jpg"
      alt: "Example Lead Tutor analysis: modeled stimulation volumes in blue and predicted fiber pathway activation in red and white."
    - title: "Connectivity analysis"
      text: "Map connections from stimulation sites to other brain regions."
      anchor: "connectivity"
      image: "fiber-filtering.jpg"
      alt: "Example Lead Tutor analysis: fiber tracts colored by their association with simulated outcome scores, over a 7 T MRI slice."
    - title: "Group analysis"
      text: "Relate electrode placement to clinical outcomes across patients."
      anchor: "groups-of-patients"
      image: "cohort-top.jpg"
      alt: "The electrodes of nine Lead Tutor patients seen from above, ending in the subthalamic nucleus (orange) between the internal pallidum (green) and red nucleus (red)"

# Lead-DBS around the world (the globe; figures from data/downloads.json, see docs/home-and-media.md, "Download figures").
# {countries}, {downloads} and {year} (the year of the first download) are filled in from the data.
worldwide:
  title: "Download requests from {countries} countries"
  text: "{downloads} Lead-DBS download requests recorded since {year}."

# The forthcoming release: one compact block, its heading and two plain sentences, with the workshop as the
# next step. Promise no release date and no access beyond the workshop.
next:
  label: "Coming next"
  title: "Lead-DBS 4.0"
  text: "We are rewriting Lead-DBS in Python so version 4.0 will run without MATLAB. Workshop participants in Cologne (February 2027) can try an early pre-release."
  link: {label: "Workshop details", url: "/events/hands-on-workshop-2027/"}

# Events: the upcoming entries of data/events.yaml, in one band with the latest news.
events:
  title: "What’s happening"
  link: {label: "All events", url: "/events/"}

# The three latest news posts, beside the events.
news:
  title: "Latest news"
  link: {label: "All news", url: "/news/"}

# In published research, after the voices: every figure of data/gallery.yaml in an endless grid that can be
# dragged (label: what a screen reader hears for it), beside the journal covers of data/covers.yaml in a fan.
research:
  title: "Made with Lead-DBS"
  label: "Figures from peer-reviewed papers that used Lead-DBS"
  link_label: "Open the gallery"

# The featured quote beside the globe: a researcher's name in data/quotes.yaml (the others are on Publications).
voices:
  quote: "Andreas Nowacki"
  link_label: "All quotes"


# The closing band, two halves built alike: where to get help (a heading, one line, a button to the Get
# help section of Docs) and how to cite Lead-DBS (cite); the funders in one row under both.
help:
  title: "Need help?"
  text: "Ask in the user Slack, look it up in the manual or report a bug."
  label: "Get help"
  url: "/helpsupport/#get-help"

# The funders, in one row under the last band. Logo files sit next to this file (content/). url only
# where the funder's page still exists.
funders:
  title: "Generously supported by"
  logos:
    # crop (optional): Hugo crop steps that cut a logo file's empty margin, applied in order
    # scale (optional): makes a logo that looks too heavy (below 1) or too light (above 1) match the others
    - {name: "Berlin Institute of Health", file: "BIH_BIG_en_400fullmargin.png", url: "https://www.bihealth.org/en/", crop: ["316x165 TopLeft", "266x115 BottomRight"], scale: 1.1}
    - {name: "KFO 247", file: "kfo247logo.png"}
    - {name: "German Research Foundation", file: "logo_dfg.png", url: "https://www.dfg.de", scale: 0.6}
    - {name: "Stiftung Charité", file: "stiftungcharitelogo.png"}
    - {name: "Prof. Dr. Klaus Thiemann Foundation", file: "thiemannfoundation.png", crop: ["558x311 TopLeft", "543x294 BottomRight"]}

cite:
  title: "Cite Lead-DBS in your paper"
  # the paper to cite now: its id in data/papers.yaml (the home page shows it as a reference and as BibTeX);
  # every paper to cite is on the page the link leads to
  paper: "neudorfer2023"
  link: {label: "Citation guidance", url: "/about/citing_leaddbs/"}

---
