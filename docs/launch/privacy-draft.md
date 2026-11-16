# Privacy policy and imprint: draft for the lab's review

**Not published and not legal advice.** The live privacy page (`content/privacy-policy/index.md`) is
WordPress's default text. It describes comments, Gravatar, user accounts and login cookies, none of which the
new site has, and leaves out what it does have. Below is a description of what the new site actually does,
checked against the code, written as a privacy policy so it can replace that page once the lab (and, if
needed, the institution's data-protection office) has reviewed it. Square brackets mark facts only Andy or
the lab can supply.

## Questions to settle first

1. **Who is the controller and provider?** The imprint names Andreas Horn with a private address in
   Brookline, MA. Should it be Andreas personally, the Institute for Network Stimulation / Uniklinik Köln,
   or another body? A German provider usually has to name a postal address where they can be served, an
   email address and a quick way to make contact (§ 5 DDG). Is a data-protection officer to be named?
2. **Server logs.** How long does STRATO keep access and error logs for this package, and does Andy keep
   other logs (`/release/` download logs)? [Andy]
3. **Download logs.** `/release/download.php` records each download with the IP address, and these logs
   feed the download statistics and the globe (`docs/download-analytics.md`). How long are the raw logs
   kept, and on what basis? [Andy, the lab]
4. **The Lead-DBS software's own requests.** The access statistics (`docs/analytics.md`) come from requests
   the software makes. That belongs in the software's documentation or here; decide where. [the lab]
5. **Newsletter.** Is double opt-in on in the WordPress Newsletter plugin? Who can see the list?
   [whoever has WordPress access]

## Draft

### Who is responsible

[Name, postal address, email of the controller, as on the imprint.] [Data-protection officer, if any.]

### Visiting the site

The website is hosted by STRATO AG, Pascalstraße 10, 10587 Berlin, Germany, on servers in Germany
[confirm]. When you open a page, the server records what every web server records: your IP address, the
date and time, the page requested, the referring page and your browser's identification. This is needed
to deliver the site and keep it secure (Art. 6(1)(f) GDPR). The logs are deleted after [n] days [Andy].
We have a data-processing agreement with STRATO [confirm].

The site uses **no cookies**, no tracking and no analytics in your browser, and loads no fonts or scripts
from other companies. If you choose a light or dark theme, your browser stores the choice locally
(`localStorage`, key `theme`). It never leaves your device.

### Downloads

When you download Lead-DBS through the download page, the server records the download with your IP
address and the time. We use these records to count downloads and to show, by country, where Lead-DBS
is used. The country is looked up on our own server. Published figures contain no IP addresses.
Legal basis: our legitimate interest in knowing how the software is used (Art. 6(1)(f) GDPR). The raw
records are kept for [n] [the lab, Andy].

### Videos

Videos from YouTube and Vimeo are **not loaded until you click** them. Until then nothing is sent to
those services. When you click, the video loads from YouTube (through its reduced-data domain
youtube-nocookie.com, operated by Google Ireland Ltd.) or from Vimeo (Vimeo.com, Inc., USA). They then
receive your IP address and may set cookies under their own privacy policies. Legal basis: your consent
by clicking (Art. 6(1)(a) GDPR).

### Contact form and FOCUS requests  *(only once the forms are switched on)*

When you send the contact form, we receive your name, email address and message by email at [recipient].
We use them only to answer you (Art. 6(1)(b) GDPR, or (f) for general questions) and delete them when
the matter is settled, unless we must keep them longer.

When you request the FOCUS atlas, we receive your name, institution and email address, and your
confirmation that you will use it for academic research only. We use them to send you the download link
and to keep a record of who received the atlas under these terms (Art. 6(1)(b) GDPR). [Retention.]

To keep out spam, the server counts submissions per connection for ten minutes. It stores only a
one-way coded form of the IP address that changes every day, never the address itself, and deletes
the count after two days.

Until the forms are switched on, the pages give an email address instead.

### Newsletter

The newsletter is sent with [the Newsletter plugin of our WordPress installation, on the same server].
If you subscribe, we store your email address and, if you give them, your name, together with the time
of subscription and confirmation [double opt-in: confirm]. Legal basis: your consent (Art. 6(1)(a)
GDPR). You can withdraw it at any time with the link in every newsletter. Requesting FOCUS does
**not** subscribe you; you can tick a separate box to also receive the newsletter.

### Links to other sites

Links to GitHub, Slack, publishers and other sites take you to services with their own privacy
policies. Nothing is sent to them until you follow a link.

### Your rights

You have the right to access, rectification, erasure, restriction of processing, data portability
and objection (Art. 15–21 GDPR), and to withdraw consent at any time with effect for the future. You
can complain to a data-protection supervisory authority, e.g. [the one responsible for the controller:
for Cologne, the Landesbeauftragte für Datenschutz und Informationsfreiheit Nordrhein-Westfalen].

Updated: [date of publication]
