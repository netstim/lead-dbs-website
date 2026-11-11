---
# The home page. Every text and list on it is set here; the layout is layouts/home.html.
# Version, date, requirements and licence come from data/release.yaml, events from data/events.yaml.
# Pictures are file names in assets/images/renders/ (replace a file there, or change a name here).
# Sections take the height of their content: a longer text simply makes its section taller.
title: "Lead-DBS"
description: "Lead-DBS is an open-source MATLAB toolbox that localizes deep brain stimulation electrodes on MRI and CT and maps their effects on brain networks."
date: "2014-06-17T12:22:42"
lastmod: "2026-11-10"
hero:
  title: "Open-source DBS imaging toolbox"
  lead: "Lead-DBS localizes deep brain stimulation electrodes on postoperative MRI or CT, simulates the stimulation and maps its effects on brain networks. Free and open source; runs in MATLAB."
  primary: {label: "Download Lead-DBS"}
  secondary: {label: "Read the manual", url: "https://netstim.gitbook.io/leaddbs"}
  # The clip behind the words: files in static/media/, poster in assets/images/renders/.
  # One directional lead in the subthalamic nucleus, the camera swaying slowly (±18°, 32 s loop),
  # framed on a black 16:10 canvas with the render on the right (see README, "hero clip").
  video: "media/hero-lead-stn.mp4"
  video_phone: "media/hero-lead-stn-phone.mp4"
  poster: "hero-lead-stn-poster.jpg"
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

# Three things it does besides localization: a compact row of three.
features:
  title: "From the electrode to the brain's networks"
  cards:
    - title: "Simulates the stimulation"
      text: "Volume of tissue activated, electric fields and pathway activation, computed with the integrated OSS-DBS v2."
      image: "pathway-activation.jpg"
      alt: "Two electrodes with their stimulation volumes in blue and the fibre pathways they activate in red and white"
    - title: "Connects it to networks"
      text: "Connectivity from the stimulation volume to other brain regions, with normative or patient-specific connectomes."
      image: "fiber-filtering.jpg"
      alt: "Fibre tracts around the electrodes, coloured from red to yellow by their association with outcome, over a 7 tesla MRI slice"
    - title: "Compares whole cohorts"
      text: "Group analysis of electrode placement and its relation to clinical outcomes, across all patients of a study."
      image: "cohort-top.jpg"
      alt: "The electrodes of nine Lead Tutor patients seen from above, ending in the subthalamic nucleus (orange) between the internal pallidum (green) and red nucleus (red)"
  note: "Pictures: example analyses on the open Lead Tutor dataset, with example stimulation settings and simulated outcome scores. Illustrations, not findings."
  link: {label: "See renders and published figures", url: "/gallery/"}

# The current release and what it needs: the facts are in data/release.yaml.
release:
  requirements_title: "What you need"
  install: {label: "Read the installation guide", url: "https://netstim.gitbook.io/leaddbs/installation"}

# Lead-DBS 4.0: a text-only announcement (no date, features, pictures or links to it yet).
next:
  label: "Coming next"
  title: "Lead-DBS 4.0"
  text: "Lead-DBS is being rebuilt completely in Python, so version 4.0 will need no MATLAB. Participants of the Hands-on Lead-DBS Workshop on 11–12 February 2027 will be among the first to try the pre-release."
  link: {label: "About the workshop", url: "#events"}

# Events: the upcoming entries of data/events.yaml, beside the workshop's flyer.
events:
  title: "Workshop and developer meeting"
  text: "Be among the first to try the Lead-DBS 4.0 pre-release at the hands-on workshop in Cologne, or join the developer meeting online."
  image: "workshop-2027-flyer.png"
  alt: "Save the date: Hands-on Lead-DBS Workshop, 11–12 February 2027, Institute for Network Stimulation and Uniklinik Köln"
  link: {label: "All events and past workshops", url: "/events/"}

help:
  title: "Help, from the manual to the user Slack"
  text: "Most questions are answered in the manual and the videos. For the rest, ask other users and the developers on the user Slack."
  # icon: a line icon in static/images/icons/ (ui-*.svg, Lucide)
  cards:
    - {title: "The manual", text: "Installation, usage and self-tutoring with the Lead Tutor dataset.", url: "https://netstim.gitbook.io/leaddbs", icon: "ui-book-open"}
    - {title: "Walkthrough videos", text: "The pipeline step by step; for the current version the manual is the reference.", url: "/helpsupport/knowledge-base/walkthrough-videos/", icon: "ui-circle-play"}
    - {title: "User Slack", text: "Ask other users and the developers. Join through the self-invite link.", url: "https://inviter.co/lead-dbs", icon: "ui-messages-square"}
    - {title: "Bug reports", text: "Report a bug or ask for a feature in the GitHub issues.", url: "https://github.com/netstim/leaddbs/issues", icon: "ui-bug"}
    - {title: "Newsletter", text: "Release and workshop news by email, sent rarely.", url: "/subscribe-to-our-newsletter/", icon: "ui-mail"}
    - {title: "Contact", text: "Everything else, including the ways to reach the team.", url: "/contact/", icon: "ui-at-sign"}

quotes_title: "What researchers say about Lead-DBS"
# Wording and spelling exactly as on the old site (www.lead-dbs.org); the role line of a paper is its journal and year.
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
  - text: "We use Lead-DBS daily at Mayo Clinic. I also am using it for my PhD based at Monash University. The software capabilities are very broad. Group analysis with dependent variables has streamlined the process of addressing my research questions significantly."
    name: "Fiona Permezel, MD, MBBS, BSc(Hons)(Psych), BSc(ScSchProg), FRACP"
    role: "Neurologist, Mayo Clinic"
  - text: "Two elegant examples were published by Horn et al. 2017 in which a method was described to warp DBS electrode coordinates and histological data to MNI-space (Ewert et al. 2017)."
    name: "Alkemade et al."
    role: "Frontiers in Neuroanatomy 2018"

team:
  title: "Who develops Lead-DBS"
  history:
    - {year: "2015", text: "First paper, from the Movement Disorders Unit of Andrea Kühn at Charité – Universitätsmedizin Berlin."}
    - {year: "2016", text: "Researchers from several institutions join the development."}
    - {year: "2019", text: "The Network Stimulation Laboratory led by Andreas Horn coordinates it."}
    - {year: "2025", text: "The lab becomes the Institute for Network Stimulation at the University Hospital Cologne."}
  link: {label: "See the development team", url: "/about/"}
  tools_title: "More tools from the team"
  tools:
    - {name: "Lead-OR", text: "Research during DBS surgery, in 3D Slicer", url: "/about/lead-or/"}
    - {name: "Lead Connectome", text: "Connectome analysis: build and use connectomes with Lead-DBS", url: "/about/lead-connectome/"}
    - {name: "Lead Tutor", text: "An open dataset to train localization", url: "https://netstim.gitbook.io/leaddbs/lead-dbs/self-tutoring-with-lead-tutor"}
  funders_title: "Lead-DBS has been supported by"
  # Logo files sit next to this file (content/). url only where the funder's page still exists.
  funders:
    # crop (optional): Hugo crop steps that cut a logo file's empty margin, applied in order
    - {name: "Berlin Institute of Health", file: "BIH_BIG_en_400fullmargin.png", url: "https://www.bihealth.org/en/", crop: ["316x165 TopLeft", "266x115 BottomRight"]}
    - {name: "KFO 247", file: "kfo247logo.png"}
    - {name: "German Research Foundation", file: "logo_dfg.png", url: "https://www.dfg.de"}
    - {name: "Stiftung Charité", file: "stiftungcharitelogo.png"}
    - {name: "Prof. Dr. Klaus Thiemann Foundation", file: "thiemannfoundation.png"}

cite:
  title: "Cite Lead-DBS in your paper"
  reference: "Neudorfer C, Butenko K, Oxenford S, Rajamani N, Achtzehn J, Goede L, et al. (2023). Lead-DBS v3.0: Mapping deep brain stimulation effects to local anatomy and global networks. NeuroImage, 268, 119862."
  doi: "10.1016/j.neuroimage.2023.119862"
  link: {label: "Every paper to cite", url: "/about/citing_leaddbs/"}

# "From the lab", at the end: Stimulating Brains is a project of the institute, not part of Lead-DBS.
lab:
  label: "From the lab"
  title: "Stimulating Brains"
  text: "The podcast and talk series on brain stimulation from the Institute for Network Stimulation, the lab that coordinates Lead-DBS: interviews and recorded talks by researchers in the field. A project of the institute, not part of Lead-DBS."
  items:
    - {title: "The podcast", text: "Interviews with researchers in brain stimulation.", url: "https://stimulatingbrains.org/podcast/", icon: "ui-mic"}
    - {title: "The talk series", text: "Recorded talks by researchers in the field.", url: "https://stimulatingbrains.org/talk-series/", icon: "ui-presentation"}
  links_title: "The institute online"
  links:
    - {name: "netstim.org", url: "https://www.netstim.org"}
    - {name: "All its tools on GitHub", url: "https://github.com/netstim"}
    - {name: "LinkedIn", url: "https://www.linkedin.com/company/institute-for-network-stimulation/"}
    - {name: "Bluesky", url: "https://bsky.app/profile/netstim.org"}
---
