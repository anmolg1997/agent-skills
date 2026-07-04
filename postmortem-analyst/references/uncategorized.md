# Uncategorized — 134 postmortems

## Canonical patterns

- **Latent bug triggered by first-time conditions** — A defect lies dormant for months until an unprecedented condition (scale threshold, rare packet signature, elapsed time, dependency loss) activates it, often simultaneously across a homogeneous fleet. Staging never reproduced the trigger because it lacked production's scale or soak time. (`amazon-11`, `amazon-17`, `amazon-18`, `appnexus`, `at-t`, `ccp-games-3`, `amazon-14`)
- **Retry storm / thundering herd cascade** — A transient failure or recovery event unleashes synchronized reconnects and retries that overload a shared component (queue, database, network layer, lock service), making the overload self-sustaining and turning a blip into an hours-long outage. (`amazon-13`, `amazon-15`, `discord`, `circleci-5`, `bbc-online`, `duo`, `amazon-19`)
- **Operator action with over-broad blast radius** — A human runs a legitimate command or script whose scope is wider than intended — a typo'd argument, wrong ID list, or maintenance job pointed at production — and tooling lacks guardrails (rate limits, soft delete, minimum-capacity floors) to contain it. (`amazon-8`, `amazon-10`, `amazon-12`, `atlassian`)
- **Upgrade or auto-update silently changes behavior** — A routine dependency, OS, or platform upgrade changes defaults or creates version skew (JVM pool sizing, RabbitMQ ack timeout, kube-proxy iptables format, wiped network rules), and the change is undocumented or mis-documented, so it manifests only in production. (`circleci-8`, `circleci-9`, `circleci-10`, `datadog-2`, `dropbox`, `ccp-games-2`)
- **Credential exposure and supply-chain compromise** — Secrets living where they should not (source repos, forgotten hosts, vendor databases) or unverified third-party artifacts give attackers a path in; the breach surface is an asset or vendor outside the primary security perimeter. (`bitly`, `browserstack`, `circleci-6`, `circleci-7`, `bintray`)
- **Operator error on production data/fleets** — Fat-fingered or mis-scoped manual actions (wrong host, missing flag, wrong directory, wrong filesystem) during maintenance or incident response destroy or disable production, amplified by lax tooling validation and untested backups. (`gitlab`, `gitlab-2`, `joyent-2`, `mailgun`, `heroku-4`)
- **Latent bug armed by config/policy data** — Code ships with a dormant defect that QA never exercises; a later, individually valid configuration or policy change becomes the trigger, often replicating globally faster than any rollback. (`fastly`, `google-20`, `github-16`, `heroku-5`)
- **Credential and supply-chain compromise** — Leaked or stolen tokens and account credentials (npm, GitHub org, Jenkins, OAuth integrations) give attackers publish or push rights, turning one credential into an ecosystem-wide attack. (`eslint`, `gentoo`, `homebrew`, `heroku-7`)
- **Database maintenance debt and hidden limits** — Known-but-deferred database ceilings — XID/ID wraparound, 32-bit id overflow, memory working sets, managed-service size caps — eventually arrive on their own schedule and fail catastrophically rather than gracefully. (`mandrill`, `joyent`, `etsy-2`, `instapaper`, `foursquare`)
- **Upstream dependency cascade and recovery-induced storms** — Third-party or shared-cloud failures propagate through transitive dependencies, and the recovery phase itself (cold caches, client retries, thundering-herd restarts) triggers a second, often longer outage. (`incident-io-6`, `launchdarkly-2`, `github-18`, `google-20`, `heroku-6`)
- **Retry/reconnect storms turn a blip into a cascading outage —** — Retry/reconnect storms turn a blip into a cascading outage — clients without backoff or admission control amplify the initial failure (`slack`, `slack-2`, `spotify`, `square`, `twilio`, `stackdriver`)
- **Observability that depends on the failing system blinds resp** — Observability that depends on the failing system blinds responders and multiplies time-to-recover (`roblox`, `slack-2`, `north-american-electric-power-system`, `yeller`)
- **Redundancy defeated by hidden shared coupling — 'independent** — Redundancy defeated by hidden shared coupling — 'independent' paths share a peering point, cluster, or vendor (`pagerduty-2`, `pagerduty-3`, `salesforce`, `zerodha-2`, `roblox`)
- **Slow-burning resource/limit exhaustion (integer keys, Postgr** — Slow-burning resource/limit exhaustion (integer keys, Postgres XIDs, disk from unbounded logs, memory leaks) with a computable failure date nobody monitored (`strava`, `sentry-2`, `tarsnap`, `skyliner`, `platform-sh`)
- **Routine manual operations on production without guardrails —** — Routine manual operations on production without guardrails — a repetitive task or ad-hoc DB op done wrong once takes everything down (`stripe`, `trivago`, `reddit`, `salesforce-2`)

## Entries

Fetch any entry's full text: `python3 scripts/pm.py fetch <id>`

### Allegro (`allegro-2`)
- tags: software-bug,dependency-failure | blast: partial-degradation
- The [Allegro](https://web.archive.org/web/20211204232004/https://allegro.pl/) platform suffered a failure of a subsystem responsible for asynchronous distributed task processing. The problem affected many areas, e.g. features such as purchasing numerous offers via cart and bulk offer editing (including price list editing) did not work at all. Moreover, it partially failed to send daily newsletter with new offers. Also some parts of internal administration panel were affected.
- **Lesson:** Features that all funnel through one shared async task pipeline share its fate; isolate critical flows from bulk/background work.
- <https://allegro.tech/2015/01/allegro-cast-post-mortem.html>

### Amazon (`amazon-8`)
- tags: human-operational-error,cascading-failure | blast: regional-outage
- Human error. On February 28th 2017 9:37AM PST, the Amazon S3 team was debugging a minor issue. Despite using an established playbook, one of the commands intending to remove a small number of servers was issued with a typo, inadvertently causing a larger set of servers to be removed. These servers supported critical S3 systems. As a result, dependent systems required a full restart to correctly operate, and the system underwent widespread outages for US-EAST-1 (Northern Virginia) until final resolution at 1:54PM PST. Since Amazon's own services such as EC2 and EBS rely on S3 as well, it caused a vast cascading failure which affected hundreds of companies.
- **Lesson:** Operational tools must enforce rate limits and minimum-capacity guardrails so a single mistyped argument cannot take out a critical fleet.
- <https://aws.amazon.com/message/41926/>

### Amazon (`amazon-9`)
- tags: data-corruption-loss,software-bug,cascading-failure | blast: regional-outage
- Message corruption caused the distributed server state function to overwhelm resources on the S3 request processing fleet.
- **Lesson:** Internal state-propagation protocols need checksums and corruption containment, or one bad message can consume the whole fleet.
- <https://web.archive.org/web/20220403060108/https://status.aws.amazon.com/s3-20080720.html>

### Amazon (`amazon-10`)
- tags: human-operational-error,software-bug,cascading-failure | blast: regional-outage,data-loss
- Human error during a routine networking upgrade led to a resource crunch, exacerbated by software bugs, that ultimately resulted in an outage across all US East Availability Zones as well as a loss of 0.07% of volumes.
- **Lesson:** Routine maintenance needs verified traffic-shift plans, because capacity crunches turn recovery mechanisms (re-mirroring) into the attack on the system.
- <https://aws.amazon.com/message/65648/>

### Amazon (`amazon-11`)
- tags: software-bug,process-gap,dependency-failure | blast: regional-outage
- Inability to contact a data collection server triggered a latent memory leak bug in the reporting agent on the storage servers. And there is no graceful degradation handling, thus the reporting agent continuously contacted the collection server in a way that slowly consumed system memory. Also the monitoring system failed to alarm this EBS server's memory leak, also EBS servers generally make very dynamic use of all memory. By Monday morning, the rate of memory loss became quite high and confused enough memory on the affected storage servers which cannot keep with the request handling process. This error got further severed by the inability to do the failover, which resulted in the outage.
- **Lesson:** Auxiliary agents (reporting, telemetry) must degrade gracefully and be monitored, or their failure mode becomes the primary outage.
- <https://aws.amazon.com/message/680342/>

### Amazon (`amazon-12`)
- tags: human-operational-error,data-corruption-loss | blast: regional-outage
- Elastic Load Balancer ran into problems when "a maintenance process that was inadvertently run against the production ELB state data".
- **Lesson:** Maintenance jobs need hard environment scoping so a process meant for non-production can never touch production state.
- <https://aws.amazon.com/message/680587/>

### Amazon (`amazon-13`)
- tags: network,cascading-failure,capacity-overload | blast: regional-outage
- A "network disruption" caused metadata services to experience load that caused response times to exceed timeout values, causing storage nodes to take themselves down. Nodes that took themselves down continued to retry, ensuring that load on metadata services couldn't decrease.
- **Lesson:** Self-protective node removal plus aggressive retries creates a lock-in cascade; back off and cap retry pressure on shared control planes.
- <https://aws.amazon.com/message/5467D2/>

### Amazon (`amazon-14`)
- tags: capacity-overload,config-change,cascading-failure | blast: regional-outage
- Scaling the front-end cache fleet for Kinesis caused all of the servers in the fleet to exceed the maximum number of threads allowed by an operating system configuration. Multiple critical downstream services affected, from Cognito to Lambda to CloudWatch.
- **Lesson:** Know and monitor every hard OS/resource ceiling in the scaling path before growth silently crosses it.
- <https://aws.amazon.com/message/11201/>

### Amazon (`amazon-15`)
- tags: automation-gone-wrong,capacity-overload,cascading-failure | blast: regional-outage
- At 7:30 AM PST, an automated activity to scale capacity of one of the AWS services hosted in the main AWS network triggered an unexpected behavior from a large number of clients inside the internal network. This resulted in a large surge of connection activity that overwhelmed the networking devices between the internal network and the main AWS network, resulting in delays for communication between these networks. These delays increased latency and errors for services communicating between these networks, resulting in even more connection attempts and retries. This led to persistent congestion and performance issues on the devices connecting the two networks.
- **Lesson:** Automated scaling events can themselves generate a thundering herd; client retry behavior must be latency-aware or congestion becomes self-sustaining.
- <https://aws.amazon.com/message/12721/>

### Amazon (`amazon-16`)
- tags: hardware-failure,software-bug,cascading-failure | blast: regional-outage,prolonged-recovery
- Multiple SimpleDB storage nodes lost power simultaneously in one US-East data center. The lock service de-registered them rapidly, which spiked load and pushed handshake latencies above SimpleDB's too-aggressive handshake timeout. Healthy storage and metadata nodes failed their handshakes, removed themselves from the cluster, and couldn't rejoin because the metadata nodes that would authorize them had also taken themselves out. Recovery required manually raising the handshake timeout and restarting metadata nodes.
- **Lesson:** Failure-detection timeouts tuned for steady state can eject healthy nodes during correlated failures; recovery paths must not depend on the quorum they are rebuilding.
- <https://aws.amazon.com/message/65649/>

### Amazon (`amazon-17`)
- tags: software-bug,network | blast: regional-outage
- A new failover-optimization protocol had been enabled in network device OS for 8 months without issue. A customer traffic pattern produced packets matching a very specific signature that triggered a latent defect in the OS, causing devices in one Direct Connect network layer to fail. Failed devices weren't automatically removed from service, so engineers manually drained them, only for additional devices to fail with the same bug. Disabling the new protocol restored Direct Connect to Tokyo after ~6 hours.
- **Lesson:** A feature running cleanly for months proves nothing about rare-input paths; ensure failed devices are auto-removed so a latent bug does not require manual draining.
- <https://aws.amazon.com/message/17908/>

### Amazon (`amazon-18`)
- tags: software-bug,capacity-overload,cascading-failure | blast: regional-outage
- As the Lambda Frontend fleet scaled in response to normal daily traffic growth, it crossed a capacity threshold within a single cell that had never been reached before, triggering a latent software defect that caused Execution Environments to be successfully allocated but never fully utilized. Lambda invocations failed in the affected cell, cascading into STS, EKS, EventBridge, Connect, and the AWS Management Console for several hours.
- **Lesson:** Cells only bound blast radius if dependent services do not all share the affected cell; test beyond historical peak capacity.
- <https://aws.amazon.com/message/061323/>

### Amazon (`amazon-19`)
- tags: software-bug,cascading-failure,capacity-overload | blast: partial-degradation,prolonged-recovery
- A Kinesis cell newly migrated to a new architecture had an unusually high number of very low-throughput shards. The cell management system distributed the shards unevenly, so a few hosts ended up handling huge numbers of shards and produced abnormally large status messages. The system misinterpreted slow status messages as host failures, kicked off a redistribution storm, and overloaded the secure-connection provisioning subsystem. CloudWatch Logs, S3 event notifications, Firehose, ECS, Lambda, Redshift, MWAA, and Glue all degraded for ~7 hours.
- **Lesson:** Health checks that misread slowness as death convert overload into churn; migrations need workload-shape validation, not just functional validation.
- <https://aws.amazon.com/message/073024/>

### AppNexus (`appnexus`)
- tags: software-bug,process-gap | blast: global-outage
- A double free revealed by a database update caused all "impression bus" servers to crash simultaneously. This wasn't caught in staging and made it into production because a time delay is required to trigger the bug, and the staging period didn't have a built-in delay.
- **Lesson:** Staging must reproduce production's temporal conditions (soak time), or time-delayed bugs will pass every gate and fire simultaneously fleet-wide.
- <https://web.archive.org/web/20250505112812/https://medium.com/xandr-tech/2013-09-17-outage-postmortem-586b19ae4307>

### AT&T (`at-t`)
- tags: software-bug,cascading-failure | blast: global-outage,prolonged-recovery
- A bad line of C code introduced a race hazard which in due course collapsed the phone network. After a planned outage, the quickfire resumption messages triggered the race, causing more reboots which retriggered the problem. "The problem repeated iteratively throughout the 114 switches in the network, blocking over 50 million calls in the nine hours it took to stabilize the system." From 1990.
- **Lesson:** Recovery traffic is a distinct load pattern that can retrigger the original fault; homogeneous fleets running the same bug fail together.
- <https://users.csc.calpoly.edu/~jdalbey/SWE/Papers/att_collapse.html>

### Atlassian (`atlassian`)
- tags: human-operational-error,process-gap,data-corruption-loss | blast: data-loss,prolonged-recovery
- On Tuesday, April 5th, 2022, starting at 7:38 UTC, 775 Atlassian customers lost access to their Atlassian products. The outage spanned up to 14 days for a subset of these customers, with the first set of customers being restored on April 8th and all customer sites progressively restored by April 18th.
- **Lesson:** Destructive scripts need soft-delete, staged rollout, and independent verification of the ID list, and disaster recovery must be rehearsed at multi-site scale.
- <https://www.atlassian.com/engineering/post-incident-review-april-2022-outage>

### Basecamp (`basecamp`)
- tags: security,network | blast: global-outage
- Basecamp's network was under a DDoS attack during a 100-minute window on March 24, 2014. Same-day announcement that the attack was in progress: [signalvnoise.com](https://signalvnoise.com/posts/3728-basecamp-was-under-network-attack-this-morning).
- **Lesson:** Communicate during an attack, not after; same-day transparency preserved trust through a 100-minute outage.
- <https://signalvnoise.com/posts/3729-basecamp-network-attack-postmortem>

### Basecamp (`basecamp-2`)
- tags: database,software-bug | blast: partial-degradation
- In November 2018 a database hit the integer limit, leaving the service in read-only mode. Same-day status update during the incident: [signalvnoise.com](https://web.archive.org/web/20220530044506/https://m.signalvnoise.com/update-on-basecamp-3-being-stuck-in-read-only-as-of-nov-8-922am-cst/).
- **Lesson:** Monitor identifier and sequence headroom like disk space; integer exhaustion is a predictable, schedulable failure.
- <https://web.archive.org/web/20220529044310/https://m.signalvnoise.com/postmortem-on-the-read-only-outage-of-basecamp-on-november-9th-2018/>

### BBC Online (`bbc-online`)
- tags: database,capacity-overload,cascading-failure | blast: partial-degradation,prolonged-recovery
- In July 2014, BBC Online experienced a very long outage of several of its popular online services including the BBC iPlayer. When the database backend was overloaded, it had started to throttle requests from various services. Services that hadn't cached the database responses locally began timing out and eventually failed completely.
- **Lesson:** Every consumer of a shared datastore needs local caching and timeout handling so backend throttling degrades rather than kills them.
- <https://www.bbc.co.uk/blogs/internet/entries/a37b0470-47d4-3991-82bb-a7d5b8803771>

### Bintray (`bintray`)
- tags: security,process-gap | blast: data-leak
- In July 2017 several malicious Maven packages were included in JCenter with an impersonation attack. Those packages lived in JCenter for over a year and supposedly affected several Android apps that resulted in having malware code injected by those dependencies from JCenter.
- **Lesson:** Package repositories need namespace/identity verification, because impersonation attacks compromise every downstream build silently.
- <https://web.archive.org/web/20210421222929/https://status.bintray.com/incidents/w4dfr0rpznkt>

### Bitly (`bitly`) ⚠dead-link
- tags: security,human-operational-error | blast: data-leak
- Hosted source code repo contained credentials granting access to bitly backups, including hashed passwords.
- **Lesson:** Secrets in source control are a standing breach waiting for repo access; keep credentials out of repos and scan continuously.
- <https://blog.bitly.com/post/85260908544/more-detail>

### BrowserStack (`browserstack`)
- tags: security,process-gap | blast: data-leak
- An old prototype machine with the [Shellshock](https://en.wikipedia.org/wiki/Shellshock_(software_bug)) vulnerability still active had secret keys on it which ultimately led to a security breach of the Production system.
- **Lesson:** Decommission or inventory every legacy host; an unpatched machine with live keys makes your oldest asset your attack surface.
- <https://www.browserstack.com/attack-and-downtime-on-9-November>

### Buildkite (`buildkite`)
- tags: config-change,capacity-overload,cascading-failure | blast: global-outage,prolonged-recovery
- Database capacity downgrade in an attempt to minimise AWS spend resulted in lack of capacity to support Buildkite customers at peak, leading to cascading collapse of dependent servers.
- **Lesson:** Cost-driven capacity reductions must be validated against peak load, not average load, before they hit production.
- <https://building.buildkite.com/outage-post-mortem-for-august-23rd-82b619a3679b>

### Bungie (`bungie`)
- tags: software-bug,config-change,data-corruption-loss | blast: data-loss
- Side effects of a bug fix for wrong timestamps causes data loss; server misconfiguration for the hotfix causes the data loss to reappear in several servers in a following update.
- **Lesson:** A fix is a change with its own blast radius; verify hotfix configuration on every server or the incident replays itself.
- <https://web.archive.org/web/20230504222953/https://www.bungie.net/en/News/Article/48723>

### CCP Games (`ccp-games-2`)
- tags: software-bug,deploy-process | blast: global-outage,prolonged-recovery
- A problematic logging channel caused cluster nodes dying off during the cluster start sequence after rolling out a new game patch.
- **Lesson:** Cluster cold-start is its own critical path; exercise the full start sequence with new code before depending on it after a patch.
- <https://community.eveonline.com/news/dev-blogs/behind-the-scenes-of-a-long-eve-online-downtime/>

### CCP Games (`ccp-games-3`)
- tags: software-bug | blast: partial-degradation
- Documents a Stackless Python memory reuse bug that took years to track down.
- **Lesson:** Rare memory-corruption bugs demand systematic instrumentation and capture tooling, because they will not reproduce on demand.
- <https://community.eveonline.com/news/dev-blogs/sleeping-beauty/>

### Chef.io (`chef-io`)
- tags: config-change,capacity-overload | blast: partial-degradation
- The recipe community site Supermarket crashed two hours after launch due to intermittent unresponsiveness and increased latency. One of the main reasons for failure identified in the post mortem was very low health check timeouts.
- **Lesson:** Health-check timeouts tuned too tight convert transient latency into a self-inflicted outage under launch load.
- <https://www.chef.io/blog/2014/07/10/supermarket-intermittent-unresponsiveness-postmortem/>

### CircleCI (`circleci-5`)
- tags: dependency-failure,capacity-overload,cascading-failure | blast: partial-degradation
- A GitHub outage and recovery caused an unexpectedly large incoming load. For reasons that aren't specified, a large load causes CircleCI's queue system to slow down, in this case to handling one transaction per minute.
- **Lesson:** Plan for the recovery spike of your upstream dependencies, not just their downtime; backlog drains are a load test you did not schedule.
- <https://circleci.statuspage.io/incidents/hr0mm9xmm3x6>

### CircleCI (`circleci-6`)
- tags: security | blast: data-leak
- By January 4, 2023, our internal investigation had determined the scope of the intrusion by the unauthorized third party and the entry path of the attack. To date, we have learned that an unauthorized third party leveraged malware deployed to a CircleCI engineer’s laptop in order to steal a valid, 2FA-backed SSO session. This machine was compromised on December 16, 2022. The malware was not detected by our antivirus software. Our investigation indicates that the malware was able to execute session cookie theft, enabling them to impersonate the targeted employee in a remote location and then escalate access to a subset of our production systems.
- **Lesson:** Session tokens defeat MFA once stolen; short-lived sessions and endpoint detection are as critical as the second factor.
- <https://circleci.com/blog/jan-4-2023-incident-report/>

### CircleCI (`circleci-7`)
- tags: security,dependency-failure | blast: data-leak
- CircleCI's database provider, MongoHQ, was breached on October 27, 2013, and CircleCI's MongoDB was among the databases accessed; CircleCI was holding GitHub OAuth tokens, Heroku API tokens, AWS IAM keys, and SSH deploy/user keys for customers in that database. On notification, CircleCI shut down the site and all builds, then worked with GitHub, Heroku, and AWS to revoke every OAuth token, API token, IAM key, and SSH key it had handed out, and cycled all of its own keys and caches.
- **Lesson:** Secrets you store inherit the security posture of your vendor; assume provider breach and be able to revoke every credential fast.
- <https://web.archive.org/web/20180121023549/http://circleci.com/blog/mongohq-security-incident-response/>

### CircleCI (`circleci-8`)
- tags: database,software-bug,capacity-overload | blast: partial-degradation,prolonged-recovery
- Slow queries on the MongoDB replica sets backing the build queue caused workflows to back up over a two-week run of incidents. A roughly concurrent minor-version JVM upgrade enabled Docker-awareness by default, which silently shrank thread and connection pools across most JVM services and constrained throughput, masking the underlying MongoDB capacity problem. Tuning thread/connection pools and upsizing MongoDB stabilized the platform after multiple cascading outages on March 26, April 2, April 3, and April 10.
- **Lesson:** Minor-version runtime upgrades can silently change resource defaults, masking the real bottleneck and stretching one incident into weeks.
- <https://discuss.circleci.com/t/postmortem-march-26-april-10-workflow-delay-incidents/30060>

### CircleCI (`circleci-9`)
- tags: dependency-failure,config-change | blast: partial-degradation,prolonged-recovery
- A routine RabbitMQ upgrade from 3.8.9 to 3.8.16 introduced a 15-minute consumer ack timeout that the changelog described as scoped to quorum queues but actually applied to all queue types. Consumers on the VM-destroyer queue gradually got their channels closed until the queue had zero consumers, so VMs in one region stopped being deleted; this eventually backed up VM creation and blocked Docker, machine, Windows, Mac, Arm, GPU, and remote-Docker jobs for ~12 hours.
- **Lesson:** Changelogs lie about scope; verify new defaults against your own workload after every dependency upgrade.
- <https://discuss.circleci.com/t/postmortem-may-21-2021-delay-in-starting-docker-jobs-machine-remote-docker-environments-blocked/40274>

### CircleCI (`circleci-10`)
- tags: deploy-process,software-bug | blast: global-outage,prolonged-recovery
- A staged Kubernetes upgrade of CircleCI's main production cluster left `kube-proxy` and `kubelet` at incompatible versions. The change between versions altered the format of `kube-proxy`'s `iptables` rulesets, so as pods churned and `Endpoints` objects changed, `kube-proxy`'s `Proxier.syncProxyRules()` (an `iptables-save` / `iptables-restore` read-modify-write) repeatedly hit "Sync failed" errors, leaving the per-node iptables in a corrupted state and silently breaking service-to-service routing across the cluster. Recovery required a full node-by-node cluster restart and triggered two follow-on incidents.
- **Lesson:** Partial platform upgrades create version-skew windows; validate cross-component compatibility and watch sync-error metrics during the rollout.
- <https://status.circleci.com/incidents/dcqb3fykhgvg>

### Cloudflare (`cloudflare-11`)
- tags: software-bug,security | blast: data-leak
- A parser bug caused Cloudflare edge servers to return memory that contained private information such as HTTP cookies, authentication tokens, HTTP POST bodies, and other sensitive data.
- **Lesson:** Memory-unsafe parsing at a multi-tenant edge turns one bug into everyone's data leak; fuzz parsers and isolate tenant memory.
- <https://web.archive.org/web/20211029020126/https://blog.cloudflare.com/incident-report-on-memory-leak-caused-by-cloudflare-parser-bug/>

### Cloudflare (`cloudflare-12`)
- tags: software-bug,deploy-process,capacity-overload | blast: global-outage
- A CPU exhaustion was caused by a single WAF rule that contained a poorly written regular expression that ended up creating excessive backtracking. This rule was deployed quickly to production and a series of events lead to a global 27 minutes downtime of the Cloudflare services.
- **Lesson:** Rules and config deserve the same staged rollout and resource-limit sandboxing as code; a regex can be a global kill switch.
- <https://web.archive.org/web/20211006055154/https://blog.cloudflare.com/details-of-the-cloudflare-outage-on-july-2-2019/>

### CrowdStrike (`crowdstrike`)
- tags: deploy-process,software-bug,process-gap | blast: global-outage
- A Content update containing undetected errors was deployed due to a bug in the Content Validator in the deployment stage. This problematic content caused an out-of-bounds memory read, resulting in a Windows operating system crash (BSOD) on 8.5 million Windows machines. The update was reverted within 78 minutes, but the incident highlighted the need for improved validation and testing processes.
- **Lesson:** Content channels that execute in the kernel are code deploys; they need canarying and staged rollout, not trust in a single validator.
- <https://www.crowdstrike.com/falcon-content-update-remediation-and-guidance-hub/>

### Datadog (`datadog-2`)
- tags: automation-gone-wrong,config-change,network | blast: global-outage,prolonged-recovery
- After an automatic upgrade, all network rules were removed and caused a 24h duration outage of all their Cilium protected Kubernetes clusters in all their regions and cloud providers.
- **Lesson:** Unattended auto-updates applied fleet-wide at once erase the isolation your multi-region architecture was supposed to buy.
- <https://www.datadoghq.com/blog/2023-03-08-multiregion-infrastructure-connectivity-issue/>

### Discord (`discord`)
- tags: cascading-failure,capacity-overload,software-bug | blast: partial-degradation
- A flapping service lead to a thundering herd reconnecting to it once it came up. This lead to a cascading error where frontend services ran out of memory due to internal queues filling up.
- **Lesson:** Reconnect storms need jittered backoff and bounded queues, or the recovery of one service becomes the death of its callers.
- <https://status.discordapp.com/incidents/dj3l6lw926kl>

### Discord (`discord-2`)
- tags: dependency-failure,software-bug,cascading-failure | blast: global-outage
- "At approximately 14:01, a Redis instance acting as the primary for a highly-available cluster used by Discord's API services was migrated automatically by Google’s Cloud Platform. This migration caused the node to incorrectly drop offline, forcing the cluster to rebalance and trigger known issues with the way Discord API instances handle Redis failover. After resolving this partial outage, unnoticed issues on other services caused a cascading failure through Discord’s real time system. These issues caused enough critical impact that Discord’s engineering team was forced to fully restart the service, reconnecting millions of clients over a period of 20 minutes."
- **Lesson:** Known issues in failover handling are outage debt; cloud providers will exercise your failover path at a time of their choosing.
- <https://status.discordapp.com/incidents/qk9cdgnqnhcn>

### Dropbox (`dropbox`)
- tags: automation-gone-wrong,deploy-process,database | blast: global-outage,prolonged-recovery
- This postmortem is pretty thin and I'm not sure what happened. It sounds like, maybe, a scheduled OS upgrade somehow caused some machines to get wiped out, which took out some databases.
- **Lesson:** Upgrade automation must positively verify a machine is out of service before reimaging it; targeting bugs destroy live data.
- <https://blogs.dropbox.com/tech/2014/01/outage-post-mortem/>

### Duo (`duo`)
- tags: capacity-overload,database,process-gap | blast: partial-degradation
- Cascading failure due to a request queue overloading the existing, insufficient database capacity. Inadequate capacity planning and monitoring could be attributed as well.
- **Lesson:** Capacity planning and saturation monitoring on the database tier must lead traffic growth, because queues amplify rather than absorb overload.
- <https://status.duo.com/incidents/4w07bmvnt359>

### Epic Games (`epic-games`)
- tags: capacity-overload | blast: partial-degradation
- Extreme load (a new peak of 3.4 million concurrent users) resulted in a mix of partial and total service disruptions.
- **Lesson:** Viral growth turns every untested scaling ceiling into an incident; load-test beyond the current record, not up to it.
- <https://web.archive.org/web/20220430011642/https://www.epicgames.com/fortnite/en-US/news/postmortem-of-service-outage-at-3-4m-ccu>

### European Space Agency (`european-space-agency`)
- tags: software-bug,process-gap | blast: safety-incident,financial-loss
- An overflow occurred when converting a 16-bit number to a 64-bit numer in the Ariane 5 intertial guidance system, causing the rocket to crash. The actual overflow occurred in code that wasn't necessary for operation but was running anyway. According to [one account](https://web.archive.org/web/20120829114850/https://www.around.com/ariane.html), this caused a diagnostic error message to get printed out, and the diagnostic error message was somehow interpreted as actual valid data. According to [another account](https://en.wikipedia.org/wiki/Cluster_%28spacecraft%29?oldid=217305667), no trap handler was installed for the overflow.
- **Lesson:** Reused code carries the assumptions of its original environment; disable what you do not need and handle every overflow path.
- <https://en.wikipedia.org/wiki/Cluster_%28spacecraft%29?oldid=217305667>

### Elastic (`elastic`)
- tags: capacity-overload,cascading-failure,dependency-failure | blast: regional-outage
- Elastic Cloud customers with deployments in the AWS eu-west-1 (Ireland) region experienced severely degraded access to their clusters for roughly 3 hours. During this same timeframe, there was an approximately 20 minute period during which all deployments in this region were completely unavailable.
- **Lesson:** A shared regional control plane is a single point of failure for every customer cluster it coordinates; isolate and capacity-protect it.
- <https://www.elastic.co/blog/elastic-cloud-january-18-2019-incident-report>

### Elastic (`elastic-2`)
- tags: capacity-overload,cascading-failure | blast: regional-outage
- Elastic Cloud customers with deployments in the AWS us-east-1 region experienced degraded access to their clusters.
- **Lesson:** A repeat of a recent incident pattern in another region means the systemic fix, not the regional symptom, was the real action item.
- <https://www.elastic.co/blog/elastic-cloud-incident-report-feburary-4-2019>

### ESLint (`eslint`)
- tags: security | blast: data-leak
- On July 12th, 2018, an attacker compromised the npm account of an ESLint maintainer and published malicious packages to the npm registry.
- **Lesson:** Package-registry maintainer accounts are production credentials: enforce 2FA and unique passwords, and treat publish rights as part of your attack surface.
- <https://eslint.org/blog/2018/07/postmortem-for-malicious-package-publishes>

### Etsy (`etsy-2`) ⚠dead-link
- tags: deploy-process,software-bug,database | blast: global-outage
- First, a deploy that was supposed to be a small bugfix deploy also caused live databases to get upgraded on running production machines. To make sure that this didn't cause any corruption, Etsy stopped serving traffic to run integrity checks. Second, an overflow in ids (signed 32-bit ints) caused some database operations to fail. Etsy didn't trust that this wouldn't result in data corruption and took down the site while the upgrade got pushed.
- **Lesson:** Deploys must do exactly and only what they claim, and integer id capacity is a time bomb you should size and monitor before it overflows.
- <https://blog.etsy.com/news/2012/demystifying-site-outages/>

### Fastly (`fastly`)
- tags: software-bug,config-change | blast: global-outage
- Global outage due to an undiscovered software bug that surfaced on June 8 when it was triggered by a valid customer configuration change.
- **Lesson:** A bug that lies dormant through QA can be armed by any valid customer input, so test config paths against production-shaped configs and design for fast global rollback.
- <https://www.fastly.com/blog/summary-of-june-8-outage>

### Flowdock (`flowdock`)
- tags: capacity-overload,database,data-corruption-loss | blast: global-outage,data-loss
- Flowdock instant messaging was unavailable for approx 24 hrs between April 21-22 2020. The COVID-19 pandemic caused a sudden and drastic increase in working from home, which caused a higher usage of Flowdock, which caused high CPU usage, which caused the application database to hang. Some user data was permanently lost.
- **Lesson:** External demand shocks arrive without warning; capacity headroom and tested database recovery are the only defenses against load-driven data loss.
- <https://web.archive.org/web/20220704223244/https://flowdock-resources.s3.amazonaws.com/legal/Flowdock-RCA-For-Incident-On-2020-04-21.pdf>

### Foursquare (`foursquare`)
- tags: capacity-overload,database,process-gap | blast: global-outage,prolonged-recovery
- MongoDB fell over under load when it ran out of memory. The failure was catastrophic and not graceful due to a a query pattern that involved a read-load with low levels of locality (each user check-in caused a read of all check-ins for the user's history, and records were 300 bytes with no spatial locality, meaning that most of the data pulled in from each page was unnecessary). A lack of monitoring on the MongoDB instances caused the high load to go undetected until the load became catastrophic, causing 17 hours of downtime spanning two incidents in two days.
- **Lesson:** Databases fail catastrophically rather than gracefully at memory limits, so monitor working-set growth and shard before locality-hostile queries hit the wall.
- <https://web.archive.org/web/20230602082218/https://news.ycombinator.com/item?id=1769761>

### Gentoo (`gentoo`)
- tags: security | blast: partial-degradation,data-leak
- An entity gained access to the Gentoo GitHub organization, removed access to all developers and started adding commits in various repositories.
- **Lesson:** Mirror-hosting orgs need hardened admin credentials and a way to declare a hosted copy untrusted, because a compromised org account becomes a supply-chain attack on every downstream user.
- <https://wiki.gentoo.org/wiki/Github/2018-06-28>

### GitHub (`github-15`)
- tags: security,network | blast: global-outage
- On February 28th 2018, GitHub experienced a DDoS attack, hitting the website with 1.35Tbps of traffic.
- **Lesson:** Amplification attacks scale beyond any single victim's capacity; pre-arranged scrubbing-provider failover is what turns a record DDoS into minutes of downtime.
- <https://githubengineering.com/ddos-incident-report/>

### GitHub (`github-16`)
- tags: config-change,software-bug,network | blast: global-outage
- A misconfigured "partial link failure" detection feature on access switches caused redundant links to be wrongly disabled during testing, producing 18 minutes of hard downtime. The underlying day-long degradation turned out to be a vendor bug that prevented the new aggregation switches from learning a large fraction of MAC addresses, so most traffic was being flooded out every port and saturating uplinks.
- **Lesson:** Redundancy features can themselves take down both paths; validate failure-detection settings against vendor bugs before trusting them in production networks.
- <https://github.blog/news-insights/the-library/network-problems-last-friday/>

### GitHub (`github-17`)
- tags: security,network,process-gap | blast: global-outage
- Several thousand HTTP requests/second from thousands of IPs hit a crafted URL on port 80 that 301'd to HTTPS, followed by an SSL connection-exhaustion vector. Because GitHub's monitoring keyed on bandwidth rather than packets-per-second, the attack wasn't detected as a DDoS for a while; configuring countermeasures took ~2 hours of downtime.
- **Lesson:** Detection tuned to one attack signal (bandwidth) is blind to others (packets or connections per second); monitor every resource an attacker can exhaust.
- <https://github.blog/news-insights/the-library/denial-of-service-attacks/>

### GitHub (`github-18`)
- tags: automation-gone-wrong,dependency-failure | blast: partial-degradation,prolonged-recovery
- A scheduled resource-cleanup job at a partner service mistakenly targeted a resource group containing essential Copilot infrastructure, removing it. Copilot Chat error rate peaked at 63%; rerouting Chat traffic mitigated most impact while resources were progressively restored over 19h26m.
- **Lesson:** Automated cleanup jobs need deny-lists and deletion guards on production resource groups, especially when they run in someone else's cloud.
- <https://github.blog/news-insights/company-news/github-availability-report-july-2024/>

### GitHub (`github-19`)
- tags: database,dns-bgp,cascading-failure | blast: partial-degradation,prolonged-recovery
- A database migration broke DNS resolution at one of GitHub's three sites, and recovery attempts cascaded to take down the rest of that site's DNS infrastructure. Repointing to a different site restored that site but broke cross-site connectivity from healthy sites; full recovery required deploying temporary DNS resolvers into the degraded site. Code search was 100% down for ~4 hours; total impact 19h12m.
- **Lesson:** When infrastructure services like DNS depend on a database, a migration is a network-wide change; rehearse recovery paths that don't assume cross-site connectivity.
- <https://github.blog/news-insights/company-news/github-availability-report-october-2024/>

### Gitlab (`gitlab`)
- tags: human-operational-error,database | blast: global-outage
- After the primary locked up and was restarted, it was brought back up with the wrong filesystem, causing a global outage. See also [HN discussion](https://web.archive.org/web/20220127094354/https://news.ycombinator.com/item?id=8003601).
- **Lesson:** Emergency restarts are when mistakes happen; checklist and verify storage mounts before returning a recovered primary to service.
- <https://docs.google.com/document/d/1ScqXAdb6BjhsDzCo3qdPYbt1uULzgZqPO8zHeHHarS0/preview?sle=true&hl=en&forcehl=1#heading=h.dfbilqgnc5sf>

### Gitlab (`gitlab-2`)
- tags: human-operational-error,database,process-gap | blast: data-loss,prolonged-recovery
- Influx of requests overloaded the database, caused replication to lag, tired admin deleted the wrong directory, six hours of data lost. See also [earlier report](https://about.gitlab.com/2017/02/01/gitlab-dot-com-database-incident) and [HN discussion](https://web.archive.org/web/20240918153505/https://news.ycombinator.com/item?id=13537052).
- **Lesson:** Backups you have never restored do not exist; test restores continuously and make destructive commands visibly environment-labelled.
- <https://about.gitlab.com/2017/02/10/postmortem-of-database-outage-of-january-31/>

### Google (`google-16`)
- tags: software-bug,process-gap | blast: partial-degradation
- A mail system emailed people more than 20 times. This happened because mail was sent with a batch cron job that sent mail to everyone who was marked as waiting for mail. This was a non-atomic operation and the batch job didn't mark people as not waiting until all messages were sent.
- **Lesson:** Batch jobs must mark work done as they go (or be idempotent), because any retry of a non-atomic sweep multiplies its side effects.
- <https://gist.github.com/jomo/2bae3821acb433d0446d>

### Google (`google-17`)
- tags: capacity-overload,dependency-failure,config-change | blast: partial-degradation
- Filestore enforces a global limit on API requests to limit impact in overload scenarios. The outage was triggered when an internal Google service managing a large number of GCP projects malfunctioned and overloaded the Filestore API with requests, causing global throttling of the Filestore API. This continued until the internal service was manually paused. As a result of this throttling, read-only API access was unavailable for all customers. This affected customers in all locations, due to a global quota that applies to Filestore. Console, gcloud and API access (List, GetOperation, etc.) calls all failed for a duration of 3 hours, 12 minutes. Mutate operations (CreateInstance, UpdateInstance, CreateBackup, etc.) still succeeded, but customers were unable to check on operation progress.
- **Lesson:** Global rate limits convert one bad internal client into an all-customer outage; scope throttling per-caller and per-region.
- <https://status.cloud.google.com/incidents/X8SNkK2BPyCrc1sveeiu>

### Google (`google-18`)
- tags: software-bug,capacity-overload | blast: partial-degradation
- The Google Meet Livestream feature experienced disruptions that caused intermittent degraded quality of experience for a small subset of viewers, starting 25 October 2021 0400 PT and ending 26 October 2021 1000 PT. Quality was degraded for a total duration of 4 hours (3 hours on 25 October and 1 hour on 26 October). During this time, no more than 15% of livestream viewers experienced higher rebuffer rates and latency in livestream video playback. We sincerely apologize for the disruption that may have affected your business-critical events. We have identified the cause of the issue and have taken steps to improve our service.
- **Lesson:** Quality-of-experience metrics like rebuffer rate need alerting of their own, since a service can be 'up' while unusable for live events.
- <https://www.google.com/appsstatus/dashboard/incidents/k71P8nHp32hgcMSsC3mR>

### Google (`google-19`)
- tags: software-bug,capacity-overload | blast: regional-outage
- On 13 October 2022 23:30 US/Pacific, there was an unexpected increase of incoming and logging traffic combined with a bug in Google’s internal streaming RPC library that triggered a deadlock and caused the Write API Streaming frontend to be overloaded. And BigQuery Storage WriteAPI observed elevated error rates in the US Multi-Region for a period of 5 hours.
- **Lesson:** Concurrency bugs in shared client libraries surface only under load spikes, so stress-test core RPC layers at beyond-peak traffic.
- <https://status.cloud.google.com/incidents/mREMLwZFe3FuLLn3zfTw>

### Google (`google-20`)
- tags: software-bug,config-change,cascading-failure | blast: global-outage
- A policy change containing blank fields triggered a null pointer exception in Service Control, Google's API management and control plane system. The code path that failed was not feature flag protected and lacked proper error handling. When the policy data replicated globally, it caused Service Control binaries to crash loop across all regions. While a red-button fix was deployed within 40 minutes, larger regions like us-central-1 experienced extended recovery times (up to 2h 40m) due to a thundering herd problem when Service Control tasks restarted, overloading the underlying Spanner infrastructure. The incident affected Google and Google Cloud APIs globally, with recovery times varying by product architecture.
- **Lesson:** Config data is code input: feature-flag new code paths, validate before global replication, fail open in the control plane, and add backoff so recovery doesn't stampede the datastore.
- <https://status.cloud.google.com/incidents/ow5i3PPK96RduMcb1SsW>

### GPS/GLONASS (`gps-glonass`)
- tags: software-bug,deploy-process | blast: safety-incident,global-outage
- A bad update that caused incorrect orbital mechanics calculations caused GPS satellites that use GLONASS to broadcast incorrect positions for 10 hours. The bug was noticed and rolled back almost immediately due to (?) this didn't fix the issue.
- **Lesson:** In safety-critical broadcast systems, a rollback does not undo state already propagated to consumers; validate updates against physical-reality checks before upload.
- <https://web.archive.org/web/20250903124227/https://www.gps.gov/governance/advisory/meetings/2014-06/beutler1.pdf>

### Healthcare.gov (`healthcare-gov`)
- tags: process-gap,human-operational-error | blast: global-outage,prolonged-recovery
- A large organizational failure to build a website for United States healthcare.
- **Lesson:** Large programs fail organizationally before they fail technically; a single accountable owner and end-to-end testing before launch are non-negotiable.
- <https://web.archive.org/web/20201108122248/https://www.bloomberg.com/opinion/articles/2015-09-16/how-healthcare-gov-went-so-so-wrong>

### Heroku (`heroku-4`)
- tags: human-operational-error,process-gap | blast: regional-outage
- Having a system that requires scheduled manual updates resulted in an error which caused US customers to be unable to scale, stop or restart dynos, or route HTTP traffic, and also prevented all customers from being able to deploy.
- **Lesson:** Any system that requires scheduled manual updates will eventually be broken by one; automate the update path or fence its blast radius.
- <https://status.heroku.com/incidents/642?postmortem>

### Heroku (`heroku-5`)
- tags: software-bug,deploy-process,data-corruption-loss | blast: data-loss,partial-degradation
- An upgrade silently disabled a check that was meant to prevent filesystem corruption in running containers. A subsequent deploy caused filesystem corruption in running containers.
- **Lesson:** Safety checks need their own monitoring: assert that guards are still active after every upgrade, or their silent removal becomes tomorrow's corruption.
- <https://engineering.heroku.com/blogs/2017-02-15-filesystem-corruption-on-heroku-dynos/>

### Heroku (`heroku-6`)
- tags: dependency-failure | blast: partial-degradation
- An upstream `apt` update broke pinned packages which lead to customers experiencing write permission failures to `/dev`.
- **Lesson:** Pinning packages does not isolate you from upstream repository changes; stage and verify OS-level dependency updates before they reach customer workloads.
- <https://status.heroku.com/incidents/1042>

### Heroku (`heroku-7`)
- tags: security | blast: data-leak
- Private tokens were leaked, and allowed attackers to retrieve data, both in internal databases, in private repositories and from customers accounts.
- **Lesson:** Long-lived integration tokens are lateral-movement gold; scope them minimally, rotate aggressively, and monitor for anomalous use.
- <https://blog.heroku.com/april-2022-incident-review>

### Heroku (`heroku-8`)
- tags: software-bug,capacity-overload,process-gap | blast: partial-degradation,prolonged-recovery
- A change to the core application that manages the underlying infrastructure for the Common Runtime included a dependency upgrade that caused a timing lock issue that greatly reduced the throughput of our task workers. This dependency change, coupled with a failure to appropriately scale up due to increased workload scheduling, caused the application's work queue to build up. Contributing to the issue, the team was not alerted immediately that new router instances were not being initialized correctly on startup largely because of incorrectly configured alerts. These router instances were serving live traffic already but were shown to be in the wrong boot state, and they were deleted via our normal processes due to failing readiness checks. The deletion caused a degradation of the associated runtime cluster while the autoscaling group was creating new instances. This reduced pool of router instances caused requests to fail as more requests were coming in faster than the limited number of routers could handle. This is when customers started noticing issues with the service.
- **Lesson:** Dependency bumps in infrastructure control planes deserve performance regression tests, and alerts must be verified to fire before you need them.
- <https://status.heroku.com/incidents/2451>

### Homebrew (`homebrew`)
- tags: security,process-gap | blast: data-leak
- A GitHub personal access token with recently elevated scopes was leaked from Homebrew’s Jenkins that allowed access to `git push` on several Homebrew repositories.
- **Lesson:** CI systems accumulate over-scoped credentials; audit token scopes after every change and assume anything readable from CI will leak.
- <https://web.archive.org/web/20210813020247/https://brew.sh/2018/08/05/security-incident-disclosure/>

### Honeycomb (`honeycomb`)
- tags: capacity-overload,process-gap | blast: partial-degradation
- A tale of multiple incidents, happening mostly due to fast growth.
- **Lesson:** Fast growth converts yesterday's adequate architecture into today's incident cluster; schedule scaling work before the graphs force you to.
- <https://www.honeycomb.io/blog/incident-resolution-september-retrospective/>

### Honeycomb (`honeycomb-2`)
- tags: software-bug,capacity-overload,cascading-failure | blast: partial-degradation
- Another story of multiple incidents that ended up impacting [query performance](https://status.honeycomb.io/incidents/fzw6hqjx5t4f) and [alerting via triggers and SLOs](https://status.honeycomb.io/incidents/jwhrxcs5zr06). These incidents were notable because of how challenging their investigation turned out to be.
- **Lesson:** Systems designed to degrade gracefully produce the hardest investigations; invest in observability of the degradation mechanisms themselves.
- <https://www.honeycomb.io/blog/incident-review-designed-failing/>

### Honeycomb (`honeycomb-3`)
- tags: capacity-overload,cascading-failure,database | blast: partial-degradation,prolonged-recovery
- On September 8th, 2022, our ingest system went down repeatedly and caused interruptions for over eight hours. We will first cover the background behind the incident with a high-level view of the relevant architecture, how we tried to investigate and fix the system, and finally, we’ll go over some meaningful elements that surfaced from our incident review process.
- **Lesson:** A cache that the hot path cannot live without is a hard dependency; model and test ingest behavior when it slows rather than fails.
- <https://www.honeycomb.io/blog/incident-review-shepherd-cache-delays/>

### Honeycomb (`honeycomb-4`)
- tags: cascading-failure,capacity-overload | blast: global-outage
- On July 25th, 2023, we experienced a total Honeycomb outage. It impacted all user-facing components from 1:40 p.m. UTC to 2:48 p.m. UTC, during which no data could be processed or accessed. The full details of incident triage process is covered in [here](https://www.honeycomb.io/wp-content/uploads/2023/08/Incident-Review-What-Comes-Up-Must-First-Go-Down.pdf).
- **Lesson:** Total outages test your cold-start story: know the dependency order for bringing the platform back up before you have to discover it live.
- <https://www.honeycomb.io/blog/incident-review-what-comes-up-must-first-go-down/>

### incident.io (`incident-io-4`)
- tags: software-bug,cascading-failure | blast: partial-degradation
- A bad event (poison pill) in the async workers queue triggered unhandled panics that repeatedly crashed the app. This combined poorly with Heroku infrastructure, making it difficult to find the source of the problem. Applied mitigations that are generally interesting to people running web services, such as catching corner cases of Go panic recovery and splitting work by type/class to improve reliability.
- **Lesson:** One malformed message must never crash the shared worker fleet: recover panics at job boundaries and isolate queues by work class.
- <https://incident.io/blog/intermittent-downtime>

### incident.io (`incident-io-5`)
- tags: network,capacity-overload,software-bug | blast: partial-degradation
- After moving to Google Cloud they saw spikes of Postgres connection timeouts (~200 new connections/s) and memcached "i/o timeout" errors. Pool tuning (15m→30m max lifetime, static pool size, `MaxIdleConns` 2→20) helped each in turn but didn't eliminate the cache errors. The smoking gun was GKE Dataplane V2: bursts of parallel outbound calls (made worse by an accidental N+1 join) saturated the per-node `anetd` agent's CPU, dropping packets between the node and other services running on it.
- **Lesson:** Cloud networking layers have per-node CPU budgets; connection timeouts that look like database or cache problems can be the dataplane itself dropping packets.
- <https://incident.io/blog/clouds-caches-and-connection-conundrums>

### incident.io (`incident-io-6`)
- tags: dependency-failure,cascading-failure,database | blast: partial-degradation,prolonged-recovery
- During the AWS us-east-1 outage, incident.io's Google-Cloud-hosted platform mostly held but third-party AWS dependencies cascaded into a complex multi-team response: their telecom provider's outage backed up the on-call notification queue (~30× normal load), their deploy pipeline was wedged because their builder transitively pulled `golang:1.24.9-alpine` from Docker Hub (which runs on AWS), and Postgres dead tuples in the escalation-acquisition index turned scaling up workers into a net throughput regression. A traffic-management feature flag also failed to apply globally because of a recent "top 10 orgs by volume" usability tweak.
- **Lesson:** You inherit your vendors' vendors: enumerate transitive third-party dependencies (including your deploy pipeline's) before a shared cloud outage does it for you.
- <https://incident.io/blog/service-disruption-october-20th-2025>

### Indian Electricity Grid (`indian-electricity-grid`)
- tags: capacity-overload,cascading-failure,process-gap | blast: regional-outage,prolonged-recovery
- One night in July 2012, a skewed electricity supply-demand profile developed when the northern grid drew a tremendous amount of power from the western and eastern grids. Following a series of circuit breakers tripping by virtue of under-frequency protection, the entire NEW (northern-eastern-western) grid collapsed due to the absence of islanding mechanisms. While the grid was reactivated after over 8 hours, similar conditions in the following day caused the grid to fail again. However, the restoration effort concluded almost 24 hours after the occurrence of the latter incident.
- **Lesson:** Interconnected systems need designed isolation points; without islanding, protection mechanisms propagate collapse instead of containing it.
- <https://web.archive.org/web/20220124104632/https://cercind.gov.in/2012/orders/Final_Report_Grid_Disturbance.pdf>

### Instapaper (`instapaper`)
- tags: database,dependency-failure,capacity-overload | blast: global-outage,prolonged-recovery
- Also [this](https://web.archive.org/web/20240911020547/https://blog.instapaper.com/post/157027537441). Limits were hit for a hosted database. It took many hours to migrate over to a new database.
- **Lesson:** Managed services have undocumented ceilings; know your provider's hard limits and your growth trajectory toward them before they meet.
- <https://web.archive.org/web/20211124170124/https://medium.com/making-instapaper/instapaper-outage-cause-recovery-3c32a7e9cc5f>

### Intel (`intel`)
- tags: software-bug,process-gap | blast: financial-loss
- A scripting bug caused the generation of the divider logic in the Pentium to very occasionally produce incorrect results. The bug wasn't caught in testing because of an incorrect assumption in a proof of correctness. (See [the Wikipedia article on 1994 FDIV bug](https://en.wikipedia.org/wiki/Pentium_FDIV_bug) for more information.)
- **Lesson:** A proof of correctness is only as good as its assumptions; verify the artifact that ships, not the model of it.
- <https://web.archive.org/web/20241105190743/http://42gems.com/blog/?p=735>

### Joyent (`joyent`)
- tags: database,software-bug | blast: partial-degradation
- Operations on Manta were blocked because a lock couldn't be obtained on their PostgreSQL metadata servers. This was due to a combination of PostgreSQL's transaction wraparound maintenance taking a lock on something, and a Joyent query that unnecessarily tried to take a global lock.
- **Lesson:** Routine database maintenance will eventually coincide with your worst query; never take broader locks than the operation requires.
- <https://web.archive.org/web/20220528044329/https://www.joyent.com/blog/manta-postmortem-7-27-2015>

### Joyent (`joyent-2`)
- tags: human-operational-error,process-gap | blast: regional-outage
- An operator used a tool with lax input validation to reboot a small number of servers undergoing maintenance but forgot to type `-n` and instead rebooted all servers in the datacenter. This caused an outage that lasted 2.5 hours, rebooted all customer instances, put tremendous load on DHCP/TFTP PXE boot systems, and left API systems requiring manual intervention. See also [Bryan Cantrill's talk](https://www.youtube.com/watch?v=30jNsCVLpAE).
- **Lesson:** Operational tools must make the dangerous scope the hard one: require explicit confirmation for fleet-wide actions instead of defaulting to them.
- <https://web.archive.org/web/20220406095752/https://www.joyent.com/blog/postmortem-for-outage-of-us-east-1-may-27-2014>

### Kickstarter (`kickstarter`)
- tags: database,software-bug,data-corruption-loss | blast: data-loss
- Primary DB became inconsistent with all replicas, which wasn't detected until a query failed. This was caused by a MySQL bug which sometimes caused `order by` to be ignored.
- **Lesson:** Replication can be silently wrong, not just behind; run continuous consistency checks between primary and replicas rather than waiting for a failing query.
- <https://web.archive.org/web/20170728131458/https://kickstarter.engineering/the-day-the-replication-died-e543ba45f262>

### Kings College London (`kings-college-london`)
- tags: hardware-failure,process-gap | blast: data-loss,prolonged-recovery
- 3PAR suffered catastrophic outage which highlighted a failure in internal process.
- **Lesson:** Vendor-redundant storage is not a backup strategy; institutional data needs restore-tested backups independent of the primary array.
- <https://regmedia.co.uk/2017/02/23/kcl_external_review.pdf>

### Launchdarkly (`launchdarkly`)
- tags: software-bug | blast: partial-degradation
- Rule attribute selector causing flag targeting web interface to crash.
- **Lesson:** The console that operators use to mitigate incidents is itself production; test its edge cases as seriously as the data plane.
- <https://status.launchdarkly.com/incidents/yltrp45vtxm2>

### Launchdarkly (`launchdarkly-2`)
- tags: dependency-failure,cascading-failure,config-change | blast: global-outage,prolonged-recovery
- The AWS us-east-1 outage degraded EC2/Lambda/DynamoDB/Route 53, leaving Launchdarkly's US web app, API, and client-side streaming SDKs unable to autoscale and dropping events. After AWS recovered, an internal change meant to shed load reverted flag-delivery to a legacy routing path with cold caches; SDKs hammered the streaming service with retries, the load balancer became unresponsive, and EC2 provisioning issues prevented scale-out, taking server-side streaming globally to ~99% errors and keeping US streaming down for another ~12 hours.
- **Lesson:** The second outage often starts during recovery from the first: warming caches and taming client retry storms must be part of the failback plan.
- <https://launchdarkly.com/blog/what-happened-what-we-learned-and-how-were-improving/>

### Mailgun (`mailgun`)
- tags: human-operational-error,database,capacity-overload | blast: partial-degradation
- Secondary MongoDB servers became overloaded and while troubleshooting accidentally pushed a change that sent all secondary traffic to the primary MongoDB server, overloading it as well and exacerbating the problem.
- **Lesson:** Changes made under incident pressure need the same review as normal changes, because a mis-scoped mitigation can convert degradation into outage.
- <https://status.mailgun.com/incidents/p9nxxql8g9rh>

### Mandrill (`mandrill`)
- tags: database,process-gap | blast: partial-degradation,prolonged-recovery
- Transaction ID wraparound in Postgres caused a partial outage lasting a day and a half.
- **Lesson:** XID wraparound is a scheduled disaster: monitor transaction-age headroom and ensure autovacuum can actually keep up on your busiest tables.
- <https://mailchimp.com/what-we-learned-from-the-recent-mandrill-outage/>

### Medium (`medium`)
- tags: software-bug | blast: partial-degradation
- Polish users were unable to use their "Ś" key on Medium.
- **Lesson:** Keyboard shortcuts collide with international input methods; test text entry across locales before binding modifier combos.
- <https://web.archive.org/web/20160426163728/https://medium.com/medium-eng/the-curious-case-of-disappearing-polish-s-fa398313d4df>

### Metrist (`metrist`)
- tags: dependency-failure,process-gap | blast: partial-degradation
- Azure published a breaking change that affected downstream systems like Metrist's service without warning them, the post covers how to identify the issue and how to recover from it.
- **Lesson:** Treat upstream provider behavior as an unversioned contract and continuously probe it, because providers will break it without notice.
- <https://web.archive.org/web/20230927050430/https://metrist.io/blog/how-we-found-azures-unannounced-breaking-change/>

### NASA (`nasa`)
- tags: software-bug,capacity-overload | blast: safety-incident
- A design flaw in the Apollo 11 rendezvous radar produced excess CPU load, causing the spacecraft computer to restart during lunar landing.
- **Lesson:** Real-time systems should shed low-priority work under overload rather than crash; Apollo's priority-scheduled restart design saved the landing.
- <https://www.doneyles.com/LM/Tales.html>

### NASA (`nasa-2`)
- tags: software-bug,process-gap,human-operational-error | blast: financial-loss
- Use of different units of measurement (metric vs. English) caused Mars Climate Orbiter to fail. There were also organizational and procedural failures[[ref](https://space.stackexchange.com/a/20241)] and defects in the navigation software[[ref](https://spectrum.ieee.org/aerospace/robotic-exploration/why-the-mars-probe-went-off-course)].
- **Lesson:** Cross-team interfaces need explicit unit/contract validation; anomalies noticed in navigation were also not escalated, so process failures compounded the bug.
- <https://en.wikipedia.org/wiki/Mars_Climate_Orbiter>

### NASA (`nasa-3`)
- tags: software-bug | blast: partial-degradation
- NASA's Mars Pathfinder spacecraft experienced system resets a few days after landing on Mars (1997). Debugging features were remotely enabled until the cause was found: a [priority inversion](https://en.wikipedia.org/wiki/Priority_inversion) problem in the VxWorks operating system. The OS software was remotely patched (all the way to Mars) to fix the problem by adding priority inheritance to the task scheduler.
- **Lesson:** Ship with remotely enableable diagnostics; Pathfinder was only debuggable and patchable on Mars because tracing hooks were left in.
- <https://web.archive.org/web/20161230103247/https://research.microsoft.com/en-us/um/people/mbj/Mars_Pathfinder/Authoritative_Account.html>

### Netflix (`netflix`)
- tags: dependency-failure,hardware-failure | blast: partial-degradation
- An EBS outage in one availability zone was mitigated by migrating to other availability zones.
- **Lesson:** Practiced AZ-evacuation turns a provider zone failure into a mitigation exercise instead of an outage.
- <https://netflixtechblog.com/post-mortem-of-october-22-2012-aws-degradation-efcee3ab40d5>

### North American Electric Power System (`north-american-electric-power-system`)
- tags: cascading-failure,software-bug,process-gap | blast: regional-outage,prolonged-recovery
- A power outage in Ohio around 1600h EDT cascaded up through a web of systemic vulnerabilities and process failures and resulted in an outage in the power grid affecting ~50,000,000 people for ~4 days in some areas, and caused rolling blackouts in Ontario for about a week thereafter.
- **Lesson:** When the monitoring that operators rely on fails silently, a contained local fault can cascade continent-wide before anyone reacts.
- <https://www3.epa.gov/region1/npdes/merrimackstation/pdfs/ar/AR-1165.pdf>

### Okta (`okta`)
- tags: security,dependency-failure | blast: data-leak
- A hackers group got access to a third-party support engineer's laptop.
- **Lesson:** Your vendors' endpoints are part of your attack surface; scope and monitor third-party support access as tightly as your own.
- <https://www.okta.com/blog/2022/03/oktas-investigation-of-the-january-2022-compromise/>

### OpenAI (`openai`)
- tags: software-bug,dependency-failure | blast: data-leak
- Queues for requests and responses in a Redis cache became corrupted and out of sequence, leading to some requests revealing other people's user data to some users, including app activity data and some billing info.
- **Lesson:** Session/cache multiplexing bugs convert an availability defect into a privacy incident, so cross-user isolation must not depend on queue ordering.
- <https://web.archive.org/web/20240426015133/https://openai.com/blog/march-20-chatgpt-outage>

### PagerDuty (`pagerduty-2`)
- tags: network,process-gap | blast: partial-degradation
- In April 2013, PagerDuty, a cloud service proving application uptime monitoring and real-time notifications, suffered an outage when two of its three independent cloud deployments in different data centers began experiencing connectivity issues and high network latency. It was found later that the two independent deployments shared a common peering point which was experiencing network instability. While the third deployment was still operational, PagerDuty's applications failed to establish quorum due to to high network latency and hence failed in their ability to send notifications.
- **Lesson:** Redundancy is only as real as the verified independence of its failure domains; audit shared network paths behind supposedly independent sites.
- <https://web.archive.org/web/20211019062735/https://www.pagerduty.com/blog/outage-post-mortem-april-13-2013/>

### PagerDuty (`pagerduty-3`)
- tags: dependency-failure | blast: partial-degradation
- A third party service for sending SMS and making voice calls experienced an outage due to AWS having issues in a region.
- **Lesson:** Transitive cloud dependencies mean your vendor's region outage is your outage; diversify notification delivery paths.
- <https://status.pagerduty.com/incidents/70m30bh7qfmx>

### Parity (`parity`)
- tags: security,software-bug,process-gap | blast: financial-loss
- $30 million of cryptocurrency value was diverted (stolen) with another $150 million diverted to a safe place (rescued), after a 4000-line software change containing a security bug was mistakenly labeled as a UI change, inadequately reviewed, deployed, and used by various unsuspecting third parties. See also [this analysis](https://web.archive.org/web/20221226010429/https://hackingdistributed.com/2017/07/22/deep-dive-parity-bug/).
- **Lesson:** Review depth must be driven by the actual diff and its risk, never by the change's self-declared label.
- <https://web.archive.org/web/20180830181639/https://paritytech.io/the-multi-sig-hack-a-postmortem/>

### Platform.sh (`platform-sh`)
- tags: capacity-overload,process-gap | blast: global-outage
- Outage during a scheduled maintenance window because there were too much data for Zookeeper to boot.
- **Lesson:** Restart and restore paths must be regularly exercised at real production data scale, because state grows past what boot procedures were tested with.
- <https://web.archive.org/web/20201202234639/https://medium.com/@florian_7764/technical-post-mortem-of-the-august-incident-82ab4c3d6547>

### Reddit (`reddit`)
- tags: deploy-process,human-operational-error | blast: global-outage
- Experienced an outage for 1.5 hours, followed by another 1.5 hours of degraded performance on Thursday August 11 2016. This was due to an error during a migration of a critical backend system.
- **Lesson:** Migrations of critical backends need rehearsal, staged rollout, and a tested rollback before touching production.
- <https://web.archive.org/web/20221029203405/https://www.reddit.com/r/announcements/comments/4y0m56/why_reddit_was_down_on_aug_11/>

### Reddit (`reddit-2`)
- tags: deploy-process,config-change | blast: global-outage,prolonged-recovery
- Outage for over 5 hours when a critical Kubernetes cluster upgrade failed. The failure was caused by node metadata that changed between versions which brought down workload networking.
- **Lesson:** Version upgrades silently change implicit metadata your infra depends on; rehearse upgrades on production-identical clusters.
- <https://web.archive.org/web/20230727225235/https://www.reddit.com/r/RedditEng/comments/11xx5o0/you_broke_reddit_the_piday_outage/>

### Roblox (`roblox`)
- tags: software-bug,capacity-overload,cascading-failure | blast: global-outage,prolonged-recovery
- Roblox end Oct 2021 73 hours outage. Issues with Consul streaming and BoltDB.
- **Lesson:** A single central control-plane cluster that your monitoring also depends on maximizes both blast radius and time-to-diagnose; break circular observability dependencies.
- <https://blog.roblox.com/2022/01/roblox-return-to-service-10-28-10-31-2021/>

### Salesforce (`salesforce`)
- tags: hardware-failure,cascading-failure,database | blast: regional-outage,data-loss
- Initial disruption due to power failure in one datacenter led to cascading failures with a database cluster and file discrepancies resulting in cross data center failover issues.
- **Lesson:** Failover must be validated for data integrity, not just availability, or the recovery path itself creates the data loss.
- <https://help.salesforce.com/apex/HTViewSolution?urlname=Root-Cause-Message-for-Disruption-of-Service-on-NA14-May-2016&language=en_US>

### Salesforce (`salesforce-2`)
- tags: config-change,human-operational-error | blast: partial-degradation
- On September 20, 2023, a service disruption affected a subset of customers across multiple services beginning at 14:48 Coordinated Universal Time (UTC). As a result, some customers were unable to login and access their services. A policy change executed as a part of our standard security controls review and update cycle to be the trigger of this incident. This change inadvertently blocked access to resources beyond its intended scope.
- **Lesson:** Access-policy changes need scope simulation and canary rollout because their blast radius is invisible until enforced.
- <https://help.salesforce.com/s/articleView?id=000396429&type=1>

### Sentry (`sentry-2`)
- tags: database,process-gap | blast: global-outage,prolonged-recovery
- Transaction ID Wraparound in Postgres caused Sentry to go down for most of a working day.
- **Lesson:** Databases have slow-burning operational limits (XID age, vacuum debt) that must be monitored long before they become emergencies.
- <https://blog.sentry.io/2015/07/23/transaction-id-wraparound-in-postgres>

### Shapeshift (`shapeshift`) ⚠dead-link
- tags: security,process-gap | blast: financial-loss
- Poor security practices enabled an employee to steal $200,000 in cryptocurrency in 3 separate hacks over a 1 month period. The company's CEO expanded upon the story in a [blog post](https://web.archive.org/web/20190811214903/http://moneyandstate.com:80/looting-of-the-fox/).
- **Lesson:** Least-privilege and key-separation must assume insider threat; one trusted employee should never be able to move funds alone.
- <http://web.archive.org/web/20160610080136/https://www.scribd.com/doc/309574927/ShapeShift-Post-Mortem-Public>

### Skyliner (`skyliner`)
- tags: software-bug,dependency-failure | blast: global-outage
- A memory leak in a third party library lead to Skyliner being unavailable on two occasions.
- **Lesson:** Third-party code needs the same resource-usage monitoring and restart hygiene as your own, because its leaks become your outages.
- <https://web.archive.org/web/20251230063242/https://blog.skyliner.io/post-mortem-outages-on-1-19-17-and-1-23-17-3f65cc6f693e>

### Slack (`slack`)
- tags: cascading-failure,capacity-overload | blast: partial-degradation
- A combination of factor results in a large number of Slack's users being disconnected to the server. The subsequent massive disconnection-reconnection process exceeded the database capacity and caused cascading connection failures, leading to 5% of Slack's users not being able to connect to the server for up to 2 hours.
- **Lesson:** Design for the reconnect storm after an outage, not just the outage: admission control and jittered backoff are load-bearing.
- <https://web.archive.org/web/20181208123409/https://slackhq.com/this-was-not-normal-really>

### Slack (`slack-2`)
- tags: network,capacity-overload,cascading-failure | blast: global-outage
- Network saturation in AWS's traffic gateways caused packet loss. An attempt to scale up caused more issues.
- **Lesson:** Provider network components have their own scaling lag, and losing your dashboards in the same event multiplies recovery time — keep observability off the shared failure path.
- <https://slack.engineering/slacks-outage-on-january-4th-2021/>

### Slack (`slack-3`)
- tags: capacity-overload,cascading-failure | blast: global-outage
- Cache nodes removal caused the high workload on the vitness cluster, which in turn cased the service outage.
- **Lesson:** A cache tier is capacity protection, not an optimization; removing it transfers its entire absorbed load to the database instantly.
- <https://slack.engineering/slacks-incident-on-2-22-22/>

### Spotify (`spotify`)
- tags: software-bug,cascading-failure | blast: partial-degradation
- Lack of exponential backoff in a microservice caused a cascading failure, leading to notable service degradation.
- **Lesson:** Every service client needs exponential backoff with jitter, or retries convert a blip into a cascading failure.
- <https://labs.spotify.com/2013/06/04/incident-management-at-spotify/>

### Square (`square`)
- tags: cascading-failure,capacity-overload | blast: partial-degradation
- A cascading error from an adjacent service lead to merchant authentication service being overloaded. This impacted merchants for ~2 hours.
- **Lesson:** Bulkhead critical services from their neighbors so one service's failure traffic cannot consume another's capacity.
- <https://web.archive.org/web/20210818034431/https://medium.com/square-corner-blog/incident-summary-2017-03-16-2f65be39297>

### Stackdriver (`stackdriver`)
- tags: database,cascading-failure,capacity-overload | blast: global-outage
- In October 2013, [Stackdriver](https://www.stackdriver.com/), experienced an outage, when its Cassandra cluster crashed. Data published by various services into a message bus was being injested into the Cassandra cluster. When the cluster failed, the failure percolated to various producers, that ended up blocking on queue insert operations, eventually leading to the failure of the entire application.
- **Lesson:** Producers must fail or shed rather than block when a downstream store dies; missing backpressure design propagates a storage failure everywhere.
- <https://www.stackdriver.com/post-mortem-october-23-stackdriver-outage/>

### Stack Exchange (`stack-exchange`) ⚠dead-link
- tags: deploy-process,capacity-overload | blast: global-outage
- Enabling StackEgg for all users resulted in heavy load on load balancers and consequently, a DDoS.
- **Lesson:** Ramp new client-side features gradually; a 100% launch turns your own users into a DDoS botnet.
- <http://web.archive.org/web/20150404235419/https://stackstatus.net/post/115305251014/outage-postmortem-march-31-2015>

### Stack Exchange (`stack-exchange-2`) ⚠dead-link
- tags: software-bug,capacity-overload | blast: global-outage
- Backtracking implementation in the underlying regex engine turned out to be very expensive for a particular post leading to health-check failures and eventual outage.
- **Lesson:** Never run backtracking regexes on user input; one pathological string can take down every instance simultaneously via shared code.
- <http://web.archive.org/web/20160720200842/https://stackstatus.net/post/147710624694/outage-postmortem-july-20-2016>

### Stack Exchange (`stack-exchange-3`)
- tags: software-bug,process-gap | blast: data-leak
- Porting old Careers 2.0 code to the new Developer Story caused a leak of users' information.
- **Lesson:** Code ports and rewrites need a fresh privacy/authorization review because old assumptions about visibility rarely survive the move.
- <https://meta.stackoverflow.com/q/340960/2422776>

### Stack Exchange (`stack-exchange-4`) ⚠dead-link
- tags: software-bug,database | blast: global-outage
- The primary SQL-Server triggered a bugcheck on the SQL Server process, causing the Stack Exchange sites to go into read only mode, and eventually a complete outage.
- **Lesson:** Even mature commercial databases crash; a rehearsed degraded read-only mode buys time but you still need tested primary-failure recovery.
- <http://web.archive.org/web/20170130231315/https://stackstatus.net/post/156407746074/outage-postmortem-january-24-2017>

### Strava (`strava`) ⚠dead-link
- tags: software-bug,database | blast: partial-degradation
- Hit the signed integer limit on a primary key, causing uploads to fail.
- **Lesson:** Monitor key-space and counter exhaustion as a capacity metric; integer limits are a scheduled outage with a computable date.
- <https://engineering.strava.com/the-upload-outage-of-july-29-2014/>

### Stripe (`stripe`)
- tags: human-operational-error,database,process-gap | blast: global-outage
- Manual operations are regularly executed on production databases. A manual operation was done incorrectly (missing dependency), causing the Stripe API to go down for 90 minutes.
- **Lesson:** Routinely performed manual production operations are latent outages; encode them as checked, automated runbooks.
- <https://support.stripe.com/questions/outage-postmortem-2015-10-08-utc>

### Sweden (`sweden`)
- tags: process-gap,human-operational-error | blast: safety-incident
- Use of different rulers by builders caused the _Vasa_ to be more heavily built on its port side and the ship's designer, not having built a ship with two gun decks before, overbuilt the upper decks, leading to a design that was top heavy. Twenty minutes into its maiden voyage in 1628, the ship heeled to port and sank.
- **Lesson:** Unify measurement standards and demand independent design review when scaling beyond anything previously built — a 400-year-old units lesson that Mars Climate Orbiter repeated.
- <https://www.pri.org/stories/2012-02-23/new-clues-emerge-centuries-old-swedish-shipwreck>

### Tarsnap (`tarsnap`)
- tags: automation-gone-wrong,software-bug | blast: global-outage
- A batch job which scans for unused blocks in Amazon S3 and marks them to be freed encountered a condition where all retries for freeing certain blocks would fail. The batch job logs its actions to local disk and this log grew without bound. When the filesystem filled, this caused other filesystem writes to fail, and the Tarsnap service stopped. Manually removing the log file restored service.
- **Lesson:** Bound every log and retry loop: an operation that can fail forever plus unbounded logging equals a disk-full outage.
- <https://mail.tarsnap.com/tarsnap-announce/msg00035.html>

### Telstra (`telstra`)
- tags: hardware-failure,data-corruption-loss | blast: regional-outage,data-leak
- A fire in a datacenter caused SMS text messages to be sent to random destinations. Corrupt messages were also experienced by customers.
- **Lesson:** Physical failures can corrupt and misroute data rather than just stopping service, so failure modes include privacy exposure, not only downtime.
- <https://web.archive.org/web/20170202055452/https://www.businessinsider.com.au/a-fire-in-a-telstra-exchange-is-causing-flight-delays-and-network-outages-2017-2>

### Therac-25 (`therac-25`)
- tags: software-bug,process-gap | blast: safety-incident
- The Therac-25 was a radiation therapy machine involved in at least six accidents between 1985 and 1987 in which patients were given massive overdoses of radiation. Because of concurrent programming errors, it sometimes gave its patients radiation doses that were thousands of times greater than normal, resulting in death or serious injury.
- **Lesson:** Never replace hardware safety interlocks with unverified software, and treat user-reported anomalies in safety systems as emergencies.
- <http://sunnyday.mit.edu/papers/therac.pdf>

### trivago (`trivago`)
- tags: human-operational-error,config-change | blast: partial-degradation
- Due to a human error, all engineers lost access to the central source code management platform (GitHub organization). An Azure Active Directory Security group controls the access to the GitHub organization. This group was removed during the execution of a manual and repetitive task.
- **Lesson:** Automate repetitive identity-management tasks and ensure critical access groups have soft-delete and restore paths.
- <https://tech.trivago.com/2021/10/05/postmortem-removing-all-users-from-github.com/trivago/>

### Twilio (`twilio`)
- tags: network,software-bug,cascading-failure | blast: financial-loss
- In 2013, a temporary network partition in the redis cluster used for billing operations, caused a massive resynchronization from slaves. The overloaded master crashed and when it was restarted, it started up in read-only mode. The auto-recharge component in This resulted in failed transactions from Twilio's auto-recharge service, which unfortunately billed the customers before updating their balance internally. So the auto-recharge system continued to retry the transaction again and again, resulting in multiple charges to customer's credit cards.
- **Lesson:** Billing operations must be idempotent and record state before charging, or infrastructure failures translate directly into repeated customer charges.
- <https://www.twilio.com/blog/2013/07/billing-incident-post-mortem-breakdown-analysis-and-root-cause.html>

### Twilio (`twilio-2`)
- tags: dependency-failure | blast: partial-degradation
- Twilio's incident of having high filtering on SMS towards AT&T Network In United States.
- **Lesson:** Delivery through carriers is a dependency governed by their opaque policies; monitor per-carrier delivery rates as a first-class SLO.
- <https://status.twilio.com/incidents/wdrlk4qps0z1>

### Valve (`valve-2`)
- tags: software-bug,process-gap | blast: data-loss
- Steam's desktop client deleted all local files and directories. The thing I find most interesting about this is that, after this blew up on social media, there were widespread reports that this was reported to Valve months earlier. But Valve doesn't triage most bugs, resulting in an extremely long time-to-mitigate, despite having multiple bug reports on this issue.
- **Lesson:** Guard destructive shell operations against unset variables, and triage inbound bug reports — time-to-mitigate is a process property, not a technical one.
- <https://github.com/valvesoftware/steam-for-linux/issues/3671>

### Xubuntu (`xubuntu`)
- tags: security | blast: partial-degradation
- The website for Xubuntu, a derivative of Ubuntu Linux that uses Xfce as its desktop environment, was compromised by an attacker who changed download links to a malicious zip file.
- **Lesson:** Distribution websites are supply-chain attack targets; signed artifacts and out-of-band checksums are the only defense users can verify.
- <https://lists.ubuntu.com/archives/xubuntu-users/2025-November/012210.html>

### Yeller (`yeller`)
- tags: network,process-gap | blast: partial-degradation
- A network partition in a cluster caused some messages to get delayed, up to 6-7 hours. For reasons that aren't clear, a rolling restart of the cluster healed the partition. There's some suspicious that it was due to cached routes, but there wasn't enough logging information to tell for sure.
- **Lesson:** If a recovery works for reasons you cannot explain, the incident is not over; invest in logging sufficient to diagnose partitions.
- <https://web.archive.org/web/20201018145502/http://yellerapp.com/posts/2014-08-04-postmortem1.html>

### Zerodha (`zerodha`)
- tags: capacity-overload,dependency-failure,software-bug | blast: partial-degradation,financial-loss
- The Order Management System (OMS) provided to Zerodha, a stock broker, collapsed when an order for 1M units of a penny stock was divided into more than 0.1M individual trades against the typical few hundreds, triggering a collapse of the OMS, which was not encountered prior by its provider - Refinitiv (formerly Thomson Reuters), a subsidiary of the London Stock Exchange.
- **Lesson:** Load-test for legal-but-pathological input shapes and cap inputs at the boundary, because market/user behavior will eventually produce the worst case.
- <https://zerodha.com/marketintel/bulletin/229363/post-mortem-of-technical-issue-august-29-2019>

### Zerodha (`zerodha-2`)
- tags: network,dependency-failure,process-gap | blast: partial-degradation
- A failure of the primary leased line to a CTCL between a stock broker and a stock exchange led to the activation of a backup leased line that was operating sporadically over the following hour, affecting bracket and cover orders. Subsequently, the process of placing and validating orders had been modified to incorporate the unreliability of the CTCL's leased lines, but the reliability of the primary and the backup leased lines was not fundamentally improved by the providers.
- **Lesson:** A flapping backup link can do more damage than a dead primary; design order-validation to tolerate degraded links rather than trusting provider redundancy.
- <https://zerodha.com/marketintel/bulletin/105569/postmortem-trading-and-hanging-orders-on-12th-april-2018>

