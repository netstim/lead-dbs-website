---
# The home page. Every text and list on it is set here; the layout is layouts/home.html.
# Version, date, requirements and licence come from data/release.yaml, events from data/events.yaml.
# Pictures are file names in assets/images/renders/ (replace a file there, or change a name here).
# Sections take the height of their content: a longer text simply makes its section taller.
title: "Lead-DBS"
description: "Lead-DBS is an open-source toolbox that localizes deep brain stimulation electrodes on MRI and CT and maps their effects on brain networks."
date: "2014-06-17T12:22:42"
lastmod: "2026-11-12"
hero:
  title: "Open-source DBS imaging toolbox"
  lead: "Localize electrodes, model stimulation and analyse connectivity."
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
  # proof: the end of the quiet line under the buttons (after the version, MATLAB and the licence, from
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
# crop: x0, y0, x1, y1 in the file's pixels), one line (text), and links to its catalogue pages.
features:
  title: "From the electrode to the brain’s networks"
  more: {label: "What Lead-DBS does", url: "/helpsupport/knowledge-base/lead-dbs-methods/"}
  data:
    page: "/helpsupport/knowledge-base/atlasesresources"
    text: "Most in MNI space, many shipped with Lead-DBS."
    image: "head-data.jpg"
    crop: [1500, 150, 2950, 1250]
    links:
      - {page: "/helpsupport/knowledge-base/atlasesresources/atlases-2", label: "Subcortical atlases"}
      - {page: "/helpsupport/knowledge-base/atlasesresources/cortical-atlas-parcellations-mni-space", label: "Cortical parcellations"}
      - {page: "/helpsupport/knowledge-base/atlasesresources/normative-connectomes", label: "Normative connectomes"}
  cards:
    - title: "Stimulation modelling"
      text: "Model electric fields, activated tissue and pathways."
      anchor: "stimulation"
      image: "pathway-activation.jpg"
      alt: "Two electrodes with their stimulation volumes in blue and the fibre pathways they activate in red and white"
    - title: "Connectivity analysis"
      text: "Map connections from stimulation sites to other brain regions."
      anchor: "connectivity"
      image: "fiber-filtering.jpg"
      alt: "Fibre tracts around the electrodes, coloured from red to yellow by their association with outcome, over a 7 tesla MRI slice"
    - title: "Group analysis"
      text: "Relate electrode placement to clinical outcomes across patients."
      anchor: "groups-of-patients"
      image: "cohort-top.jpg"
      alt: "The electrodes of nine Lead Tutor patients seen from above, ending in the subthalamic nucleus (orange) between the internal pallidum (green) and red nucleus (red)"

# Lead-DBS around the world (the globe; figures from data/downloads.json, see docs/home-and-media.md, "Download figures").
# {countries}, {downloads} and {year} (the year of the first download) are filled in from the data.
worldwide:
  title: "Downloaded in {countries} countries"
  text: "Lead-DBS has been downloaded {downloads} times since {year}."
  link_label: "Usage statistics"
  # the link to the table of every country on /usage/ (the globe itself can only be read with a mouse)
  table_label: "All countries"

# The forthcoming release: three points, with the workshop as the next step.
next:
  label: "Coming next"
  title: "Lead-DBS 4.0"
  points:
    - {title: "Lead-DBS 4.0", text: "We’re rewriting Lead-DBS in Python."}
    - {title: "No MATLAB required", text: "Version 4.0 will run without a MATLAB licence."}
    - {title: "First to try it", text: "Participants of the hands-on workshop will be among the first to try the pre-release."}
  link: {label: "Hands-on workshop", url: "/events/hands-on-workshop-2027/"}

# Events: the upcoming entries of data/events.yaml, in one band with the latest news.
events:
  title: "What’s happening"
  link: {label: "All events", url: "/events/"}

# The three latest news posts, beside the events.
news:
  title: "Latest news"
  link: {label: "All news", url: "/news/"}

# In published research, after the voices: figures from data/gallery.yaml (by file name), shown whole in
# one row and linking to their entry on /gallery/.
research:
  title: "Made with Lead-DBS"
  text: "Figures from peer-reviewed papers that used Lead-DBS."
  link_label: "Open the gallery"
  figures: ["edlow2019_fig7_panela.png", "hollunder2024_fig2_right.png", "rios2022_fig6_panela.png"]

# The voices: a render across the whole width (a file in assets/images/renders/ that the page shows
# nowhere else), the three quotes below over its dark lower part.
voices:
  title: "What researchers say"
  image: "cohort-hero.jpg"
  alt: "The electrodes of nine Lead Tutor patients converging on the subthalamic nucleus, seen from the right and above, with the internal pallidum and red nucleus over a 7 tesla MRI slice"
# The quotes themselves are in data/quotes.yaml (shared with the wall on Publications).


# The closing band, two halves built alike: where to get help (a heading, one line, a button to the Get
# help section of Docs and help) and how to cite Lead-DBS (cite); the funders in one row under both.
help:
  title: "Need help?"
  text: "Ask in the user Slack, look it up in the manual or report a bug."
  label: "Get help"
  url: "/helpsupport/#get-help"

# The funders, in one row under the last band. Logo files sit next to this file (content/). url only
# where the funder's page still exists.
funders:
  title: "Supported by"
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
