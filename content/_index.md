---
# The home page. Every text and list on it is set here; the layout is layouts/home.html.
# Version, date, requirements and licence come from data/release.yaml, events from data/events.yaml.
# Pictures are file names in assets/images/renders/ (replace a file there, or change a name here).
# Sections take the height of their content: a longer text simply makes its section taller.
title: "Lead-DBS"
description: "Lead-DBS is an open-source toolbox that localizes deep brain stimulation electrodes on MRI and CT and maps their effects on brain networks."
date: "2014-06-17T12:22:42"
lastmod: "2026-11-10"
hero:
  title: "Open-source DBS imaging toolbox"
  # lead_more follows the lead (on a phone too: a visitor without MATLAB should learn it before downloading)
  lead: "Lead-DBS localizes deep brain stimulation electrodes on postoperative MRI or CT, simulates the stimulation and maps its effects on brain networks."
  lead_more: "Free and open source; runs in MATLAB."
  primary: {label: "Download Lead-DBS"}
  # the second action is for newcomers; the manual (another site, marked ↗) follows it as a third, quieter link
  secondary: {label: "First steps", url: "/helpsupport/first-steps/"}
  manual: {label: "Manual", url: "https://netstim.gitbook.io/leaddbs"}
  # The clip behind the words: files in static/media/, poster in assets/images/renders/.
  # One directional lead in the subthalamic nucleus, the camera swaying slowly (±18°, 32 s loop),
  # framed on a black 16:10 canvas with the render on the right (see README, "hero clip").
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
  # proof: one quiet line under the buttons, in the first screen, of things a visitor can check: who
  # coordinates it, the three papers that describe it, and how to cite them (the one link of the line).
  # Each part is Markdown and stays whole; a narrow screen breaks the line between parts. A number added
  # here needs its source and date.
  proof:
    - "Institute for Network Stimulation, Cologne"
    - "*NeuroImage* 2015, 2019, 2023"
    - "[How to cite](/about/citing_leaddbs/)"
  alt: "Close-up of one directional DBS electrode with segmented contacts in the subthalamic nucleus (orange), the red nucleus behind it, over a 7 tesla MRI slice"

# Electrode localization, with the scroll moment: the leads move into place as the section scrolls by.
# The frames are in static/media/insertion/ (see README, "The electrode insertion").
localize:
  title: "Electrode localization from MRI and CT"
  text: "Lead-DBS reconstructs the electrodes of each patient from postoperative imaging and shows the result in 2D and 3D, for one patient or a whole cohort."
  rows:
    - {name: "Input", value: "Postoperative MRI, or postoperative CT with preoperative MRI"}
    - {name: "Output", value: "Electrode trajectories and contacts in native and template space"}
  link: {label: "Watch the walkthrough videos", url: "/helpsupport/knowledge-base/walkthrough-videos/"}

# Three things it does besides localization: a compact row of three. Each card leads to its part of the
# overview of everything Lead-DBS does (anchor: an id on that page), "more" beside the heading to its top.
# "data": the slim band under the cards for the atlases and data hub (page): its render (image, cut to
# crop: x0, y0, x1, y1 in the file's pixels), one line (text), and counts: the number of entries in each
# catalogue page's atlases.yaml, counted at build time, with what they are (label).
features:
  title: "From the electrode to the brain’s networks"
  more: {label: "What Lead-DBS does", url: "/helpsupport/knowledge-base/lead-dbs-methods/"}
  data:
    page: "/helpsupport/knowledge-base/atlasesresources"
    text: "All in MNI space, many included with Lead-DBS."
    image: "head-data.jpg"
    crop: [1500, 150, 2950, 1250]
    counts:
      - {page: "/helpsupport/knowledge-base/atlasesresources/atlases-2", label: "subcortical atlases"}
      - {page: "/helpsupport/knowledge-base/atlasesresources/cortical-atlas-parcellations-mni-space", label: "cortical parcellations"}
      - {page: "/helpsupport/knowledge-base/atlasesresources/normative-connectomes", label: "normative connectomes"}
  cards:
    - title: "Simulates the stimulation"
      text: "Volume of tissue activated, electric fields and pathway activation, computed with OSS-DBS v2, the stimulation model built into Lead-DBS."
      anchor: "stimulation"
      image: "pathway-activation.jpg"
      alt: "Two electrodes with their stimulation volumes in blue and the fibre pathways they activate in red and white"
    - title: "Connects it to networks"
      text: "Connectivity from the stimulation volume to other brain regions, with the patient's own connectome or a normative one, an average wiring diagram of many human brains."
      anchor: "connectivity"
      image: "fiber-filtering.jpg"
      alt: "Fibre tracts around the electrodes, coloured from red to yellow by their association with outcome, over a 7 tesla MRI slice"
    - title: "Compares whole cohorts"
      text: "Group analysis of electrode placement and its relation to clinical outcomes, across all patients of a study."
      anchor: "groups-of-patients"
      image: "cohort-top.jpg"
      alt: "The electrodes of nine Lead Tutor patients seen from above, ending in the subthalamic nucleus (orange) between the internal pallidum (green) and red nucleus (red)"
  note: "Pictures: example analyses on the open Lead Tutor dataset, with example stimulation settings and simulated outcome scores. Illustrations, not findings."
  link: {label: "See renders and published figures", url: "/gallery/"}

# Lead-DBS 4.0: a text-only announcement (no date, features, pictures or links to it yet).
# points: three statements set large in three columns, each with one line under it. The home page says "first to try the
# pre-release" here only; the workshop card below it and the events text do not repeat it.
next:
  label: "Coming next"
  title: "Lead-DBS 4.0"
  points:
    - {title: "Completely in Python", text: "Lead-DBS is being rebuilt from the ground up in Python."}
    - {title: "No MATLAB required", text: "Version 4.0 will run without a MATLAB licence."}
    - {title: "First to try it", text: "Participants of the Hands-on Lead-DBS Workshop on 11–12 February 2027 will be among the first to try the pre-release."}
  link: {label: "The workshop", url: "/events/hands-on-workshop-2027/"}

# Events: the upcoming entries of data/events.yaml, in one band with the latest news.
events:
  title: "Upcoming events"
  link: {label: "All events and past workshops", url: "/events/"}

# The three latest news posts, beside the events.
news:
  title: "Latest news"
  link: {label: "All news", url: "/news/"}

# In published research, after the voices: figures from data/gallery.yaml (by file name), shown whole in
# one row and linking to their entry on /gallery/.
research:
  title: "Made with Lead-DBS"
  text: "Figures from peer-reviewed papers that used Lead-DBS."
  link_label: "All published figures"
  figures: ["edlow2019_fig7_panela.png", "hollunder2024_fig2_right.png", "rios2022_fig6_panela.png"]

# The voices: a render across the whole width (a file in assets/images/renders/ that the page shows
# nowhere else), the three quotes below over its dark lower part.
voices:
  title: "What researchers say about Lead-DBS"
  image: "cohort-hero.jpg"
  alt: "The electrodes of nine Lead Tutor patients converging on the subthalamic nucleus, seen from the right and above, with the internal pallidum and red nucleus over a 7 tesla MRI slice"
# Wording and spelling exactly as on the old site (www.lead-dbs.org); the role line of a paper is its journal and year.
# Three quotes are shown, in the voices band (three short ones, so the columns end together);
# quotes_more keeps the others for a page of all quotes (not shown now).
quotes:
  - text: "For me, Lead-DBS is one of the most important developments in the field of DBS research in recent years"
    name: "Andreas Nowacki"
    role: "Associate Professor and Senior Attending of Neurosurgery, Inselspital Bern"
  - text: "The spatial mapping approaches of Lead DBS have really accelerated the field."
    name: "Simon Little, MBBS MRCP PhD"
    role: "Assistant Professor of Neurology, UCSF"
  - text: "Lead-DBS is arguably the most established toolbox providing a semi-automatic framework for electrode localization"
    name: "Husch et al."
    role: "NeuroImage: Clinical 2018"
quotes_more:
  - text: "We use Lead-DBS daily at Mayo Clinic. I also am using it for my PhD based at Monash University. The software capabilities are very broad. Group analysis with dependent variables has streamlined the process of addressing my research questions significantly."
    name: "Fiona Permezel, MD, MBBS, BSc(Hons)(Psych), BSc(ScSchProg), FRACP"
    role: "Neurologist, Mayo Clinic"
  - text: "I really appreciate this brilliant toolbox and the support from Andreas Horn, Ningfei Li and colleagues that comes with it."
    name: "Vladimir Litvak"
    role: "Professor of Translational Neurophysiology, UCL London"
  - text: "Lead-DBS is a clinical research platform that continuously opens new horizons for brain research. It is critical for my ERC project that integrates invasive neurophysiology, brain stimulation and connectomics with Lead-DBS for BCI and neuroprosthetics in Parkinson’s."
    name: "Wolf-Julian Neumann, MD, PhD"
    role: "Associate Professor of Neurology, Charité Berlin"
  - text: "A commitment of the community to open science will also democratize and increase the speed of advances with high uptake of currently available initiatives such as Lead-DBS."
    name: "Latorre et al."
    role: "Frontiers in Neurology 2021"
  - text: "Lead DBS is a game changer in DBS research, this tool is allowing major steps in moving the DBS field forward 🙌🏽🙌🏽 excellent job!"
    name: "Josue Avecillas-Chasin, MD, PhD"
    role: "Assistant Professor of Neurosurgery, University of Nebraska Medical Center"
  - text: "Lead-DBS is an amazing tool and managed to popularize neuro-imaging studies and break the barriers of research community. I often use Lead-DBS for my research and I think that it has become a sine qua non for DBS studies. Looking for forward to future collaborations!"
    name: "Luigi Gianmaria Remore, MD"
    role: "Neurosurgeon, University of Milan"
  - text: "Two elegant examples were published by Horn et al. 2017 in which a method was described to warp DBS electrode coordinates and histological data to MNI-space (Ewert et al. 2017)."
    name: "Alkemade et al."
    role: "Frontiers in Neuroanatomy 2018"


# The last band, two halves: where to get help (help) and how to cite Lead-DBS (cite), the funders'
# logos in one row under both. help: a heading, one line, the actions as buttons (the first is the main
# one; the Slack link goes straight to its self-invite page) and the other ways as links. A link to
# another site is marked with ↗. Who develops Lead-DBS is told on /about/ (content/about/_index.md).
help:
  title: "Need help?"
  text: "Ask other users and the developers in the user Slack, or look it up in the manual."
  actions:
    - {label: "Join the user Slack", url: "https://inviter.co/lead-dbs"}
    - {label: "Manual", url: "https://netstim.gitbook.io/leaddbs"}
  # (bug reports and contact are in the footer, so this half ends in one row as the citation does)
  links: []

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
  link: {label: "Every paper to cite", url: "/about/citing_leaddbs/"}

---
