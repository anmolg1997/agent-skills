# Config Errors — 51 postmortems

## Canonical patterns

- **Single config push with global blast radius** — One bad rule, file, or generated artifact is propagated to the entire fleet at once (no canary, no staged rollout), so validation failure anywhere becomes failure everywhere. (`cloudflare`, `cloudflare-7`, `facebook`, `facebook-2`, `microsoft`, `google-3`, `google-5`, `etsy`, `stack-overflow`, `valve`, `pagerduty`)
- **Broken or bypassed guardrail** — The audit tool, staged-rollout policy, test environment, or IAM boundary that was supposed to stop the bad change was itself buggy, bypassed, or blind, so the safety net failed exactly when needed. (`facebook`, `microsoft`, `cloudflare-4`, `circleci-2`, `pagerduty`, `amazon`)
- **Rollback or recovery path fails or depends on the broken system** — Reverting the change makes things worse (mixed-format data, broken rollback tooling) or recovery tooling depends on the very system that is down, extending the outage well past detection. (`circleci`, `github`, `travisci-3`, `facebook`, `turso`)
- **Automated or generated config without semantic validation** — Machine-generated configs, automated cleanup jobs, and auto-applied policies run unchecked against invariants (size, prefix counts, match scope, in-use status), automating the outage instead of the operations. (`google-2`, `google-3`, `cloudflare-7`, `travisci-2`, `github-3`, `heroku`, `google`)
- **Config change activates a latent software bug or hard limit** — The change is benign in itself but trips a dormant bug, hidden state reset, or hard-coded limit in consuming software, so the failure appears far from the change that caused it. (`cloudflare-6`, `cloudflare-7`, `firefox`, `google-8`, `google-9`, `google-10`, `npm`)
- **Wrong-scope settings and credential bleed** — Configuration or credentials reach the wrong environment, tenant, or physical system — test hits prod, backups leak across tenants, durability settings are wrong, a control acts on the wrong target — yielding data loss, leaks, or safety incidents rather than downtime. (`travisci-4`, `sentry`, `turso`, `keepthescore`, `razorpay`, `owasa`, `tui`)

## Entries

Fetch any entry's full text: `python3 scripts/pm.py fetch <id>`

### Allegro (`allegro`)
- tags: config-change,capacity-overload | blast: partial-degradation
- E-commerce site went down after a sudden traffic spike caused by a marketing campaign. The outage was caused by a configuration error in cluster resource management which prevented more service instances from starting even though hardware resources were available.
- **Lesson:** Autoscaling limits in cluster config must be load-tested, or real traffic will find the ceiling before you do.
- <https://allegro.tech/2018/08/postmortem-why-allegro-went-down.html>

### Amazon (`amazon`)
- tags: config-change,process-gap | blast: regional-outage
- A configuration change in the Seoul region incorrectly removed the setting that specifies the minimum healthy hosts for the EC2 DNS resolver fleet, so the system fell back to a very low default. The fleet's healthy host count dropped and in-VPC DNS queries from EC2 instances failed for ~84 minutes until capacity was manually restored. AWS added semantic config validation and per-hour throttling on host removal as remediations.
- **Lesson:** Validate configs semantically (safe minimums, invariants), not just syntactically, and make fallback defaults fail-safe rather than minimal.
- <https://aws.amazon.com/message/74876-2/>

### CircleCI (`circleci`)
- tags: deploy-process,database | blast: partial-degradation,prolonged-recovery
- A deploy changed the type of a field in the PostgreSQL database used by the job-distribution service. Newly-written rows used the new type and old rows used the old type, so the distributor's strict schema validation failed on each scan and it stopped distributing work. Rolling back made the rows written between the two deploys unreadable, so distribution kept failing; recovery required hand-deploying a build that ignored the offending field, plus manual scaling.
- **Lesson:** Schema changes must be backwards- and forwards-compatible; once new-format rows exist, rollback is no longer a safe recovery path.
- <https://discuss.circleci.com/t/incident-report-november-8-2021-jobs-stuck-in-a-not-running-state/41890>

### CircleCI (`circleci-2`)
- tags: human-operational-error,process-gap,config-change | blast: partial-degradation
- An IAM-role gap permitted out-of-band changes to AWS WAF outside of CircleCI's Terraform pipeline; an operator performing what they believed were read-only investigation actions modified WAF in a way that began blocking legitimate traffic to the `api.circleci.com` and `circleci.com` CloudFront distributions. Because the change wasn't recorded in Terraform, responders deprioritized WAF as a suspect and chased CORS errors and recent deploys until automated drift detection surfaced the discrepancy.
- **Lesson:** Changes made outside infrastructure-as-code are invisible to responders and poison diagnosis — enforce least-privilege IAM and continuous drift detection.
- <https://discuss.circleci.com/t/post-incident-report-april-4-2025-circleci-ui-loading-build-triggering-issues/53208>

### Cloudflare (`cloudflare`)
- tags: config-change,cascading-failure | blast: global-outage
- A bad config (router rule) caused all of their edge routers to crash, taking down all of Cloudflare.
- **Lesson:** A config rule deployed everywhere simultaneously fails everywhere simultaneously — stage and validate router config like code.
- <https://web.archive.org/web/20211006135542/https://blog.cloudflare.com/todays-outage-post-mortem-82515/>

### Cloudflare (`cloudflare-2`)
- tags: config-change,human-operational-error,network | blast: regional-outage
- During a maintenance of their private backbone network, an engineer made a typo in the Atlanta datacenter network configuration, causing all traffic coming from America and Europe flowing to this only datacenter, crushing it.
- **Lesson:** Backbone routing changes need automated review and dry-run simulation, because a one-line typo can redirect a continent's traffic to one datacenter.
- <https://web.archive.org/web/20211016040522/https://blog.cloudflare.com/cloudflare-outage-on-july-17-2020/>

### Cloudflare (`cloudflare-3`)
- tags: config-change,dns-bgp,deploy-process | blast: partial-degradation
- An incorrect ordering of the disabled BGP advertised prefixes caused malfunction on 19 datacenters.
- **Lesson:** The order of operations in a network config rollout is itself a correctness property — model and verify sequences, not just end states.
- <https://web.archive.org/web/20220621124002/https://blog.cloudflare.com/cloudflare-outage-on-june-21-2022/>

### Cloudflare (`cloudflare-4`)
- tags: config-change,process-gap | blast: partial-degradation
- A change to our Tiered Cache system caused some requests to fail for users with status code 530. The impact lasted for almost six hours in total. We estimate that about 5% of all requests failed at peak. Because of the complexity of our system and a blind spot in our tests, we did not spot this when the change was released to our test environment.
- **Lesson:** Test environments must exercise production topology (tiered/cache paths); a change can pass every test and still fail 5% of live traffic for hours.
- <https://web.archive.org/web/20221112015610/https://blog.cloudflare.com/partial-cloudflare-outage-on-october-25-2022/>

### Cloudflare (`cloudflare-5`)
- tags: deploy-process,config-change | blast: partial-degradation
- Several Cloudflare services became unavailable for 121 minutes on January 24, 2023 due to an error releasing code that manages service tokens. The incident degraded a wide range of Cloudflare products including aspects of our Workers platform, our Zero Trust solution, and control plane functions in our content delivery network (CDN).
- **Lesson:** Shared auth/token infrastructure is a single point of failure across product lines — release changes to it with extra staging and instant rollback.
- <https://blog.cloudflare.com/cloudflare-incident-on-january-24th-2023/>

### Cloudflare (`cloudflare-6`)
- tags: software-bug,dns-bgp | blast: partial-degradation
- On 4 October 2023, Cloudflare experienced DNS resolution problems starting at 07:00 UTC and ending at 11:00 UTC. Some users of 1.1.1.1 or products like WARP, Zero Trust, or third party DNS resolvers which use 1.1.1.1 may have received SERVFAIL DNS responses to valid queries. We’re very sorry for this outage. This outage was an internal software error and not the result of an attack. In this blog, we’re going to talk about what the failure was, why it occurred, and what we’re doing to make sure this doesn’t happen again.
- **Lesson:** External data feeds (like the DNS root zone) are untrusted input to your parsers — bound-check and fuzz them before a growth or format change does it for you.
- <https://blog.cloudflare.com/1-1-1-1-lookup-failures-on-october-4th-2023/>

### Cloudflare (`cloudflare-7`)
- tags: config-change,software-bug,cascading-failure | blast: global-outage
- On 18 Nov. 2025, a change in permissions in a database in Cloudflare's bot-detection systems caused a file to be output that exceeded the limits of the software that runs that system. That file was propagated througout Cloudflare's network, causing a systemwide outage.
- **Lesson:** Treat internally generated config artifacts as untrusted input: validate size and shape before global propagation, and make consumers fail open on limit breaches.
- <https://blog.cloudflare.com/18-november-2025-outage/>

### Datadog (`datadog`)
- tags: config-change,cascading-failure,dependency-failure | blast: partial-degradation
- A bad service discovery config in one of the clients brought down service discovery globally when a dependent client went down.
- **Lesson:** A config error in a shared discovery layer converts one component's failure into a global one — partition blast domains in foundational services.
- <https://www.datadoghq.com/blog/2020-09-25-infrastructure-connectivity-issue/>

### Enom (`enom`)
- tags: deploy-process,process-gap | blast: prolonged-recovery,partial-degradation
- On January 15, 2022, at 9:00 AM ET, Tucows’ engineering team began planned maintenance work to migrate the Enom platform to a new cloud infrastructure. Due to the complexity of the cutover, the team encountered many issues resulting in continuous delays. The maintenance window was extended multiple times to address issues related to data replication, network routing, and DNS resolution issues impacting website accessibility and email delivery.
- **Lesson:** Rehearse complex cutovers end-to-end with explicit go/no-go rollback criteria; extending a maintenance window repeatedly is a sign the abort path was never designed.
- <https://enomstatus.com/incidents/03q064h6rb7x>

### Etsy (`etsy`)
- tags: config-change,network | blast: global-outage
- Sending multicast traffic without properly configuring switches caused an Etsy global outage.
- **Lesson:** Verify the network fabric's configuration supports a new traffic pattern before shipping it — switches are part of your deployment surface.
- <https://web.archive.org/web/20211201033341/https://codeascraft.com/2012/01/23/solr-bittorrent-index-replication/>

### Facebook (`facebook`)
- tags: config-change,dns-bgp,cascading-failure | blast: global-outage,prolonged-recovery
- Configuration changes to Facebook's backbone routers caused a global outage of all Facebook properties and internal tools.
- **Lesson:** The safety tooling that audits dangerous commands is itself critical-path code, and recovery access (badges, tools, consoles) must not depend on the network being repaired.
- <https://engineering.fb.com/2021/10/05/networking-traffic/outage-details/>

### Facebook (`facebook-2`) ⚠dead-link
- tags: config-change | blast: global-outage
- A bad config took down both Facebook and Instagram.
- **Lesson:** Properties sharing one config plane share one fate — canary globally-shared configuration and keep independent failure domains per product.
- <https://blog.thousandeyes.com/facebook-outage-deep-dive/>

### Firefox (`firefox`)
- tags: software-bug,dependency-failure | blast: global-outage
- On January 13th, 2022, a specific code path in Firefox's network stack triggered a problem in the HTTP/3 protocol implementation. This blocked network communication and made Firefox unresponsive, unable to load web content for nearly two hours.
- **Lesson:** A client monoculture means one latent protocol bug plus one server-side change can brick every install at once — ship remote kill switches for risky subsystems.
- <https://web.archive.org/web/20250314111052/https://hacks.mozilla.org/2022/02/retrospective-and-technical-details-on-the-recent-firefox-outage/>

### GitHub (`github`)
- tags: config-change,dns-bgp,automation-gone-wrong | blast: partial-degradation,prolonged-recovery
- A Puppet manifest bug restarted only the authoritative nameserver (not the caching one) after an IP change, causing query timeouts. The deploy run during incident response then rebuilt the zone file from an internal provisioning API call that itself depended on DNS, producing a corrupt zone with `NXDOMAIN` for many records. Memory exhaustion from spawned processes on the fileservers extended impact to 1h35m of partial downtime.
- **Lesson:** Recovery and rebuild tooling must not depend on the system being recovered — a zone rebuild that needs working DNS will corrupt the zone during a DNS outage.
- <https://github.blog/news-insights/the-library/dns-outage-post-mortem/>

### GitHub (`github-2`)
- tags: config-change | blast: global-outage
- A configuration change rolled out to GitHub.com databases broke the way hosts answered routing-service health-check pings, so the production read-only endpoint was marked unhealthy and inaccessible. With reads broken, the entire site was down for read operations for 36 minutes until the change was reverted.
- **Lesson:** Health checks are coupled to config — validate that a change keeps hosts answering the exact probes that gate production traffic before rolling it out.
- <https://github.blog/news-insights/company-news/github-availability-report-august-2024/>

### GitHub (`github-3`)
- tags: automation-gone-wrong,dependency-failure,config-change | blast: partial-degradation,prolonged-recovery
- A telemetry gap caused security policies to be auto-applied to backend storage accounts in GitHub's underlying compute provider, blocking access to critical VM metadata. All VM create/delete/reimage operations failed, taking out Actions hosted runners in every region, Codespaces, Copilot coding agent, CodeQL, Dependabot, GitHub Enterprise Importer, and Pages for ~5h53m.
- **Lesson:** Automated policy enforcement needs a pre-flight impact assessment and a fast human override; your cloud provider's automation can be the root cause of your outage.
- <https://github.blog/news-insights/company-news/github-availability-report-february-2026/>

### GoCardless (`gocardless`)
- tags: config-change,database,cascading-failure | blast: partial-degradation
- A bad config combined with an uncommon set of failures led to an outage of a database cluster, taking the API and Dashboard offline.
- **Lesson:** Failover configuration must be exercised under realistic combined failure modes — single-fault testing leaves the deadly combinations unproven.
- <https://gocardless.com/blog/incident-review-api-and-dashboard-outage-on-10th-october/>

### Google (`google`)
- tags: config-change,automation-gone-wrong,process-gap | blast: data-loss
- Initial GCVE provisioning was performed with a legacy option, which lead to a 'fixed term' contract with automatic deletion at the end of that period.
- **Lesson:** Deprecated options with destructive end-of-life behavior must be removed or loudly flagged — silent automatic deletion should never be a default anywhere.
- <https://cloud.google.com/blog/products/infrastructure/details-of-google-cloud-gcve-incident>

### Google (`google-2`)
- tags: config-change,dns-bgp,automation-gone-wrong | blast: regional-outage
- A bad config (autogenerated) removed all Google Compute Engine IP blocks from BGP announcements.
- **Lesson:** Generated network configs need invariant checks like 'never announce dramatically fewer prefixes than yesterday' before they reach routers.
- <https://status.cloud.google.com/incident/compute/16007>

### Google (`google-3`)
- tags: config-change,automation-gone-wrong,cascading-failure | blast: global-outage
- A bad config (autogenerated) took down most Google services.
- **Lesson:** Automated config generation without semantic validation just automates the outage — diff against invariants and canary before fleet-wide rollout.
- <https://googleblog.blogspot.com/2014/01/todays-outage-for-several-google.html>

### Google (`google-4`)
- tags: config-change,cascading-failure,dependency-failure | blast: partial-degradation
- A bad config caused a quota service to fail, which caused multiple services to fail (including gmail).
- **Lesson:** Shared internal services like quota fan failure out to every consumer — dependents should degrade open (fail permissive) when a policy service is down.
- <https://web.archive.org/web/20151008061104/http://code.google.com/p/chromium/issues/detail?id=165171>

### Google (`google-5`)
- tags: config-change,human-operational-error | blast: global-outage
- `/` was checked into the URL blacklist, causing every URL to show a warning.
- **Lesson:** Validate config entries against absurd-match invariants — an entry that matches everything is almost never intended and should be rejected automatically.
- <https://googleblog.blogspot.com/2009/01/this-site-may-harm-your-computer-on.html>

### Google (`google-6`)
- tags: deploy-process,config-change | blast: partial-degradation
- A bug in configuration roll-out to a load balancer lead to increased error rates for 22 minutes.
- **Lesson:** Canary LB config rollouts with automatic rollback on error-rate rise turn what could be an outage into a 22-minute blip.
- <https://status.cloud.google.com/incident/compute/17007#5659118702428160>

### Google (`google-7`)
- tags: config-change,capacity-overload,cascading-failure | blast: partial-degradation
- A configuration change intended to address an uptick in demand for metadata storage, which overloaded part of the blob lookup system, which caused a cascading failure with user-visible service impact to Gmail, Google Photos, Google Drive, and other GCP services dependent on blob storage.
- **Lesson:** A capacity-mitigation change needs its own capacity model — under overload, retries amplify the problem and cascade to every dependent service.
- <https://status.cloud.google.com/incident/storage/19002>

### Google (`google-8`)
- tags: config-change,software-bug,cascading-failure | blast: regional-outage,prolonged-recovery
- Two misconfigurations, plus a software bug, caused a massive Google Cloud Network failure on the US East Coast.
- **Lesson:** Individually-benign misconfigurations combine catastrophically; control-plane jobs must survive maintenance events and emergency tooling must work over a congested network.
- <https://status.cloud.google.com/incident/cloud-networking/19009>

### Google (`google-9`)
- tags: software-bug,deploy-process | blast: regional-outage
- Google’s Front End load balancing service experienced failures resulting in impact to several downstream Google Cloud services in Europe. From preliminary analysis, the root cause of the issue was caused by a new infrastructure feature triggering a latent issue within internal network load balancer code.
- **Lesson:** Enabling a new feature is a deploy of every latent bug it activates — stage feature enablement per region with automated rollback.
- <https://status.cloud.google.com/incidents/1xkAB1KmLrh5g3v9ZEZ7>

### Google (`google-10`)
- tags: software-bug,config-change | blast: partial-degradation
- Google Cloud Networking experienced issues with Google Cloud Load Balancing (GCLB) service resulting in impact to several downstream Google Cloud services. Impacted customers observed Google 404 errors on their websites. From preliminary analysis, the root cause of the issue was a latent bug in a network configuration service which was triggered during routine system operation.
- **Lesson:** Config-generation services are production-critical code paths — routine operations must not be able to emit unvalidated states to global load balancers.
- <https://status.cloud.google.com/incidents/6PM5mNd43NbMqjCZ5REh>

### Google (`google-11`)
- tags: deploy-process,capacity-overload,network | blast: partial-degradation
- Google Cloud Networking experienced reduced capacity for lower priority traffic such as batch, streaming and transfer operations from 19:30 US/Pacific on Thursday, 14 July 2022, through 15:02 US/Pacific on Friday, 15 July 2022. High-priority user-facing traffic was not affected. This service disruption resulted from an issue encountered during a combination of repair work and a routine network software upgrade rollout. Due to the nature of the disruption and resilience capabilities of Google Cloud products, the impacted regions and individual impact windows varied substantially.
- **Lesson:** Serialize risky upgrades away from concurrent repair work, and design QoS tiers so inevitable capacity loss lands on batch traffic instead of users.
- <https://status.cloud.google.com/incidents/vLsxuKoRvykNHW3nnhsJ>

### Heroku (`heroku`)
- tags: automation-gone-wrong,config-change | blast: partial-degradation
- An automated remote configuration change did not propagate fully. Web dynos could not be started.
- **Lesson:** Config distribution must verify converged state on every node, not fire-and-forget — partial propagation is worse than no propagation.
- <https://status.heroku.com/incidents/1091>

### Heroku (`heroku-2`)
- tags: deploy-process,config-change | blast: partial-degradation
- An incorrect deployment process caused new config variables not to be used when the code required them.
- **Lesson:** Ship code and the config it requires atomically, or make code tolerate the config's absence — deploy ordering is an API contract.
- <https://blog.heroku.com/how-i-broke-git-push-heroku-main>

### Keepthescore (`keepthescore`)
- tags: human-operational-error,process-gap | blast: data-loss
- Engineers deleted the production database by accident. Database is a managed database from DigitalOcean with backups once a day. 30 minutes after the disaster, it went back online, however 7 hours of scoreboard data was gone forever.
- **Lesson:** Backup frequency must match your data-loss tolerance, and destructive commands need environment-distinct credentials so 'wrong terminal' cannot reach production.
- <https://web.archive.org/web/20201101133510/https://keepthescore.co/blog/posts/deleting_the_production_database/>

### Microsoft (`microsoft`)
- tags: config-change,deploy-process | blast: global-outage
- A bad config took down Azure storage.
- **Lesson:** Staged-rollout policy only protects you if it is technically enforced — 'small, low-risk' changes are exactly the ones that get exempted and then take everything down.
- <https://azure.microsoft.com/en-us/blog/update-on-azure-storage-service-interruption/>

### NPM (`npm`)
- tags: config-change,dependency-failure | blast: partial-degradation
- Fastly configuration change caused backend routing issue. To be exact, the issue is that we were setting the req.backend in a vcl_fetch function, and then calling restart to re-parse the rules. However, calling restart will reset the req.backend to the first backed in the list, which in this case happened to be Manta, rather than the load balanced CouchDB servers.
- **Lesson:** Learn the evaluation semantics of your CDN/proxy config language — hidden state resets (like restart reverting req.backend) must be covered by routing tests.
- <https://blog.npmjs.org/post/74949623024/2014-01-28-outage-postmortem.html>

### OWASA (`owasa`)
- tags: human-operational-error,process-gap | blast: safety-incident
- The wrong push of a button lead to a water treatment plant shutting down due to too high levels of fluoride.
- **Lesson:** Safety-critical controls need interlocks, confirmations, and physically distinct affordances — a single unguarded button should never cause an irreversible hazardous action.
- <https://web.archive.org/web/20210226170650/https://indyweek.com/news/archives/human-error-caused-owasa-fluoride-overdose-owasa-sorry/>

### PagerDuty (`pagerduty`)
- tags: config-change,dns-bgp,process-gap | blast: partial-degradation
- On December 15th, 2021 at 00:17 UTC, we deployed a DNS configuration change in PagerDuty’s infrastructure that impacted our container orchestration cluster. The change contained a defect, that we did not detect in our testing environments, which immediately caused all services running in the container orchestration cluster to be unable to resolve DNS.
- **Lesson:** Infrastructure-level DNS changes must be tested in an environment that mirrors production topology and rolled out cluster-by-cluster, since everything fails at once when resolution breaks.
- <https://status.pagerduty.com/incidents/vbp7ht2647l8>

### Razorpay (`razorpay`)
- tags: hardware-failure,config-change,database | blast: data-loss,financial-loss
- A RDS hardware failure highlighted an incorrect MySQL configuration which resulted in major data loss in a financial system.
- **Lesson:** Durability and replication settings must be proven in failover drills — an actual hardware failure is the worst possible moment to discover the config was wrong.
- <https://web.archive.org/web/20250207075402/https://razorpay.com/blog/day-of-rds-multi-az-failover/>

### rust-lang (`rust-lang`)
- tags: deploy-process,dns-bgp | blast: partial-degradation
- On Wednesday, 2023-01-25 at 09:15 UTC, we deployed changes to the production infrastructure for crates.io. During the deployment, the DNS record for static.crates.io failed to resolve for an estimated time of 10-15 minutes. It was due to the fact that both certificates and DNS records were re-created during the downtime.
- **Lesson:** Make critical DNS and certificate resources immutable-by-default in infrastructure-as-code so a deploy updates them in place instead of deleting and re-creating.
- <https://blog.rust-lang.org/inside-rust/2023/02/08/dns-outage-portmortem.html>

### rust-lang (`rust-lang-2`)
- tags: software-bug,deploy-process | blast: partial-degradation
- On 2023-07-20 between 12:17 and 12:30 UTC all crate downloads from crates.io were broken due to a deployment that contained a bug in the download URL generation. During this time we had an average of 4.71K requests per second to crates.io, resulting in about 3.7M failed requests, including the retry attempts from cargo.
- **Lesson:** Smoke-test the single highest-volume request path immediately after every deploy — fast detection is what kept a total download break to 13 minutes.
- <https://blog.rust-lang.org/inside-rust/2023/07/21/crates-io-postmortem.html>

### Stack Overflow (`stack-overflow`)
- tags: config-change,network | blast: global-outage
- A bad firewall config blocked stackexchange/stackoverflow.
- **Lesson:** Firewall changes deserve the same review and staged application as code — one rule can silently block all production traffic.
- <https://web.archive.org/web/20201020103424/https://stackstatus.net/post/96025967369/outage-post-mortem-august-25th-2014>

### Sentry (`sentry`)
- tags: config-change,security | blast: data-leak
- Wrong Amazon S3 settings on backups lead to data leak.
- **Lesson:** Backups inherit the full sensitivity of the primary data — continuously audit storage ACLs rather than trusting the setting made at creation time.
- <https://blog.sentry.io/2016/06/14/security-incident-june-12-2016>

### TravisCI (`travisci`)
- tags: config-change,human-operational-error,process-gap | blast: partial-degradation
- A configuration issue (incomplete password rotation) led to "leaking" VMs, leading to elevated build queue times.
- **Lesson:** A credential rotation is only done when every consumer is verified updated — partial rotation creates silent resource leaks that surface as capacity mysteries.
- <https://www.traviscistatus.com/incidents/khzk8bg4p9sy>

### TravisCI (`travisci-2`)
- tags: automation-gone-wrong,config-change,data-corruption-loss | blast: data-loss,prolonged-recovery
- A configuration issue (automated age-based Google Compute Engine VM image cleanup job) caused stable base VM images to be deleted.
- **Lesson:** Cleanup automation needs protection tags or allowlists for artifacts still in use, plus a dry-run mode — 'old' is not the same as 'unused'.
- <https://web.archive.org/web/20221220114914/https://blog.travis-ci.com/2016-09-30-the-day-we-deleted-our-vm-images/>

### TravisCI (`travisci-3`)
- tags: config-change,deploy-process | blast: partial-degradation,prolonged-recovery
- A configuration change made builds start to fail. Manual rollback broke.
- **Lesson:** Rollback procedures are code: test them regularly, because discovering a broken rollback path mid-incident doubles the outage.
- <https://www.traviscistatus.com/incidents/sxrh0l46czqn>

### TravisCI (`travisci-4`)
- tags: human-operational-error,config-change,data-corruption-loss | blast: data-loss
- Accidental environment variable made tests truncate production database.
- **Lesson:** Test contexts must be physically unable to reach production data — separate credentials and network paths per environment, not just different env-var values.
- <https://www.traviscistatus.com/incidents/z2b3lz2kwcfp>

### TUI (`tui`)
- tags: software-bug,data-corruption-loss | blast: safety-incident
- Prior to the incident flight the reservation system from which the load sheet was produced had been upgraded. A fault in the system caused female passengers checked in with title ‘Miss’ to be counted as children. The system allocated them a child’s standard weight of 35 kg as opposed to the correct female standard weight of 69 kg. Consequently, with 38 females checked in incorrectly and misidentified as children, the G-TAWG takeoff mass from the load sheet was 1,244 kg below the actual mass of the aircraft.
- **Lesson:** Cross-check derived safety-critical values against independent estimates — a data-mapping bug in back-office software can become a physical aviation risk.
- <https://assets.publishing.service.gov.uk/media/604f423be90e077fdf88493f/Boeing_737-8K5_G-TAWG_04-21.pdf>

### Turso (`turso`)
- tags: config-change,security,data-corruption-loss | blast: data-leak,data-loss
- Incorrectly configured DB backup identifiers led to data leaks for free tier customers, and the subsequent fix resulted in possible data loss.
- **Lesson:** Multi-tenant identifiers must be provably collision-free, and a remediation for a leak must itself be verified non-destructive before it runs.
- <https://blog.turso.tech/incident-2023-12-04-data-leak-and-loss-in-some-free-tier-databases-7cba5bc7>

### Valve (`valve`) ⚠dead-link
- tags: config-change,dns-bgp,network | blast: global-outage
- Although there's no official postmortem, it looks like a bad BGP config severed Valve's connection to Level 3, Telia, and Abovenet/Zayo, which resulted in a global Steam outage.
- **Lesson:** BGP and transit changes need per-peer staged rollout and out-of-band external monitoring, because when routing breaks your own telemetry may vanish with it.
- <https://blog.thousandeyes.com/steam-outage-monitor-data-center-connectivity/>

