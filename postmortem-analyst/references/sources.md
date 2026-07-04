# Where More Postmortems Live (vetted source catalog)

Surveyed and URL-verified 2026-07-04. The bundled corpus = danluu/post-mortems (243) + AWS Post-Event Summaries (18, in `data/extra_incidents.json`). When the corpus lacks coverage for a question, these are the places to look, in order of value:

## High-value, integrable

- **The VOID**: https://www.thevoid.community/database, ~10,000 incident reports across 600+ orgs with impact-category metadata (cascading failure, near miss, data loss…). Looks blank to plain fetchers (JS-rendered Softr/Airtable app): use a browser tool. Newest entries late 2025; stewardship now Prowler (void@prowler.com). No official export; scraping is ToS-gated, ask before bulk use. **The single most valuable complement to this corpus** for long-tail and near-miss incidents.
- **AWS Post-Event Summaries**: https://aws.amazon.com/premiumsupport/technology/pes/, already bundled; re-check the index occasionally (1-2 new/year, always major).
- **Cloudflare outage tag**: https://blog.cloudflare.com/tag/outage/, the deepest recurring public postmortems in the industry; active (posts through 2026); RSS available. Check here first for any network/edge/config-pipeline question newer than the corpus.
- **GitHub Availability Reports**: https://github.blog/tag/github-availability-report/, monthly cadence since 2020, current; RSS. Reliable drip of fresh incidents with RCAs.
- **Azure Status History / PIRs**: https://azure.status.microsoft/en-us/status/history/, dozens of detailed cloud RCAs/year, 5-year rolling retention (snapshot-or-lose-it); filterable UI, no feed.
- **Wikimedia incident documentation**: https://wikitech.wikimedia.org/wiki/Incident_documentation, the only openly licensed (CC BY-SA) corpus of genuinely internal-style postmortems; queryable via MediaWiki API; still updated.

## Useful, static

- **k8s.af** (Kubernetes failure stories): https://k8s.af/, ~70-80 deep Kubernetes-domain stories; dormant since 2023 but stable; source repo moved to https://codeberg.org/hjacobs/kubernetes-failure-stories.
- **Google Cloud incidents feed**: https://status.cloud.google.com/incidents.json, first-class JSON schema but ~1-year retention and few deep RCAs; major-incident reports published separately.

## Discovery feeds

- **SRE Weekly**: https://sreweekly.com/ (RSS): weekly newsletter that reliably links new public postmortems; the best signal for incidents outside the sources above.

## Dead / skip

- learningfromincidents.io, TLS broken since ~2023; cite via Wayback only.
- The various `awesome-postmortems` GitHub lists, all small, stale subsets of danluu; nothing to add.
- upstream danluu "Other lists of postmortems" section, already indexed in this corpus (`other-lists-of-postmortems` category), several entries dead.
