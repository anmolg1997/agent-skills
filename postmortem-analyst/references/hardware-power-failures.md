# Hardware/Power Failures, 14 postmortems

## Canonical patterns

- **Backup power fails at the moment of truth**: Generators, breakers, and PLCs pass routine tests but fail during a real utility-power failover, when load and switching conditions differ from the test. (`amazon-2`, `amazon-3`, `amazon-4`, `amazon-5`)
- **Facility control-plane failure disables cooling or power**: A bug or hang in datacenter control software (cooling controllers, automated power management) converts a recoverable event into thermal shutdown or extended power loss. (`amazon-6`, `google-13`, `amazon-5`)
- **Correlated failure defeats redundancy**: Nominally redundant components share a stressor (heat, storm, one facility, one provider) or a capacity ceiling, so they fail together or overload each other sequentially. (`google-13`, `amazon-5`, `cloudflare-9`)
- **Byzantine partial failure propagates plausible garbage**: A half-alive device (switch, IMP, alarm system) keeps emitting corrupt-but-valid-looking signals that healthy systems trust and propagate, cascading far beyond the device. (`cloudflare-8`, `arpanet`, `firstenergy-general-electric`)
- **Power loss surfaces persistence and durability gaps**: Extended power failure or missing error correction reveals that data believed durable (write caches, single volumes, non-ECC memory) was not. (`google-12`, `sun`, `pythonanywhere`)
- **HA design drift: new services never joined the redundant cluster**: The high-availability architecture was real, but services added after its design carried non-obvious dependencies on a single facility, discovered only during the outage. (`cloudflare-9`, `github-4`)

## Entries

Fetch any entry's full text: `python3 scripts/pm.py fetch <id>`

### Amazon (`amazon-2`)
- tags: hardware-failure,cascading-failure | blast: regional-outage
- An unknown event caused a transformer to fail. One of the PLCs that checks that generator power is in phase failed for an unknown reason, which prevented a set of backup generators from coming online. This affected EC2, EBS, and RDS in EU West.
- **Lesson:** Backup power has its own control-logic failure modes, test the switchover chain (PLCs, breakers), not just the generators.
- <https://aws.amazon.com/message/2329B7/>

### Amazon (`amazon-3`)
- tags: hardware-failure | blast: regional-outage
- Bad weather caused power failures throughout AWS US East. A single backup generator failed to deliver stable power when power switched over to backup and the generator was loaded. This is despite having passed a load tests two months earlier, and passing weekly power-on tests.
- **Lesson:** Passing periodic load tests does not guarantee performance during a real failover, validate backups under production-like load and duration.
- <https://aws.amazon.com/message/67457/>

### Amazon (`amazon-4`)
- tags: hardware-failure | blast: regional-outage
- At 10:25pm PDT on June 4, loss of power at an AWS Sydney facility resulting from severe weather in that area lead to disruption to a significant number of instances in an Availability Zone. Due to the signature of the power loss, power isolation breakers did not engage, resulting in backup energy reserves draining into the degraded power grid.
- **Lesson:** Protection systems tuned to expected failure signatures miss real ones, design isolation to fail safe on ambiguous signals rather than drain reserves into a dead grid.
- <https://aws.amazon.com/message/4372T8/>

### Amazon (`amazon-5`)
- tags: hardware-failure,cascading-failure,human-operational-error | blast: regional-outage
- Utility power was lost at a São Paulo AZ; during failover a breaker opened in front of one generator and a second generator independently failed mechanically, leaving the remaining healthy generators overloaded so they also shut down. The site's automated power-control system then malfunctioned, forcing operators to bring generators online manually. After power was restored, a network technician brought a device back up with a bad config that advertised an invalid route, degrading internet connectivity for both AZs in SA-EAST-1 for ~20 minutes.
- **Lesson:** Redundancy is capacity-bounded, losing two backups can overload and cascade the rest, and rushed recovery actions (a bad device config) can extend the blast radius.
- <https://aws.amazon.com/message/656481/>

### Amazon (`amazon-6`)
- tags: software-bug,dependency-failure,hardware-failure | blast: regional-outage
- A bug in third-party datacenter control system code caused excessive interactions during a control-host failover, making the cooling control system unresponsive. Most of the datacenter correctly failed cooling into "max cooling" mode, but in a small portion the cooling units shut down instead, and the operator-initiated "purge" mode also failed because the PLCs controlling the air handlers had become unresponsive too. EC2 servers in one Tokyo AZ overheated and powered off; customers using ALB + AWS WAF or sticky sessions saw cross-AZ impact despite running multi-AZ.
- **Lesson:** Facility control software is a hidden single point of failure, cooling must fail into a safe mode that does not depend on the control plane being responsive.
- <https://aws.amazon.com/message/56489/>

### ARPANET (`arpanet`)
- tags: hardware-failure,software-bug,cascading-failure | blast: global-outage
- A malfunctioning IMP ([Interface Message Processor](https://en.wikipedia.org/wiki/Interface_Message_Processor)) corrupted routing data, software recomputed checksums propagating bad data with good checksums, incorrect sequence numbers caused buffers to fill, full buffers caused loss of keepalive packets and nodes took themselves off the network. From 1980.
- **Lesson:** Recomputing integrity checks after corruption launders bad data, validate semantic plausibility before propagating state, not just checksums.
- <https://datatracker.ietf.org/doc/html/rfc789.html>

### Cloudflare (`cloudflare-8`)
- tags: hardware-failure,cascading-failure | blast: partial-degradation,prolonged-recovery
- A partial switch misbehavior caused a cascading Byzantine failure which impacted the availability of the API and dashboard for six hours and 33 minutes.
- **Lesson:** A half-dead component is worse than a dead one, design failure detection for Byzantine partial failures, not just clean crashes.
- <https://web.archive.org/web/20211015231917/https://blog.cloudflare.com/a-byzantine-failure-in-the-real-world/>

### Cloudflare (`cloudflare-9`)
- tags: hardware-failure,dependency-failure,process-gap | blast: prolonged-recovery,partial-degradation
- Flexential Data Center Power Failure. This post outlines the events that caused this incident.
- **Lesson:** HA architectures rot as new products launch, continuously audit that every critical service actually runs on the high-availability cluster, and rehearse full-facility loss.
- <https://blog.cloudflare.com/post-mortem-on-cloudflare-control-plane-and-analytics-outage/>

### FirstEnergy / General Electric (`firstenergy-general-electric`)
- tags: software-bug,cascading-failure,hardware-failure | blast: regional-outage,safety-incident
- FirstEnergy had a local failure when some transmission lines hit untrimmed foliage. The normal process is to have an alarm go off, which causes human operators to re-distribute power. But the GE system that was monitoring this had a bug which prevented the alarm from getting triggered, which eventually caused a cascading failure that eventually affected 55 million people.
- **Lesson:** When monitoring fails silently, operators act on a stale model of the world, alarm and monitoring systems need their own independent health checks.
- <https://en.wikipedia.org/wiki/Northeast_blackout_of_2003>

### GitHub (`github-4`)
- tags: hardware-failure | blast: global-outage
- On January 28th, 2016 GitHub experienced a disruption in the power at their primary datacenter.
- **Lesson:** Know exactly which services survive a primary-datacenter power loss before it happens, and eliminate hidden hard dependencies on one site.
- <https://github.com/blog/2106-january-28th-incident-report>

### Google (`google-12`)
- tags: hardware-failure,data-corruption-loss | blast: data-loss
- Successive lightning strikes on their European datacenter (europe-west1-b) caused loss of power to Google Compute Engine storage systems within that region. I/O errors were observed on a subset of Standard Persistent Disks (HDDs) and permanent data loss was observed on a small fraction of those.
- **Lesson:** Write caches and single-facility persistence lose data in extended power failure, durable data must be replicated beyond one power domain.
- <https://status.cloud.google.com/incident/compute/15056#5719570367119360>

### Google (`google-13`)
- tags: hardware-failure | blast: regional-outage
- On Tuesday, 19 July 2022 at 06:33 US/Pacific, a simultaneous failure of multiple, redundant cooling systems in one of the data centers that hosts the zone europe-west2-a impacted multiple Google Cloud services. This resulted in some customers experiencing service unavailability for impacted products.
- **Lesson:** Redundant systems that share an environmental stressor fail together, redundancy must be evaluated against correlated causes, not component counts.
- <https://status.cloud.google.com/incidents/fmEL9i2fArADKawkZAa2>

### PythonAnywhere (`pythonanywhere`)
- tags: hardware-failure,cascading-failure | blast: partial-degradation
- A storage volume failure on one of storage servers caused a number of outages, starting with PythonAnywhere site and also with our users’ programs (including websites) that were dependent on that volume, and later spreading to other hosted sites.
- **Lesson:** Shared storage concentrates blast radius, map which customers and services ride on each volume so a single device failure is not a surprise multi-service outage.
- <https://blog.pythonanywhere.com/189/>

### Sun (`sun`)
- tags: hardware-failure,data-corruption-loss,process-gap | blast: data-loss
- Sun famously didn't include ECC in a couple generations of server parts. This resulted in data corruption and crashing. Following Sun's typical MO, they made customers that reported a bug sign an NDA before explaining the issue.
- **Lesson:** Omitting error correction trades silent data corruption for cost, and hiding a known defect behind NDAs multiplies the reputational damage.
- <https://www.forbes.com/forbes/2000/1113/6613068a.html#6d1bdc036162>

