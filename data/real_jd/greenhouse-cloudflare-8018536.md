---
job_code: "greenhouse-cloudflare-8018536"
title: "Customer Reliability Engineer"
department: "Customer Support"
job_family: "Customer Support"
employment_type: ""
location: "Hybrid"
source_name: "greenhouse"
source_external_id: "8018536"
source_company: "Cloudflare"
source_url: "https://boards.greenhouse.io/cloudflare/jobs/8018536?gh_jid=8018536"
source_published_at: "2026-06-24T08:44:22"
source_fetched_at: "2026-06-24T14:07:22.630601"
source_hash: "7a02fafe1ce7bf0c1396d45408f48b1b3d04edc1a68869d12571428a3a5fa3f6"
tags: [real-data, public-job-posting]
---

# Customer Reliability Engineer

- **Company:** Cloudflare
- **Location:** Hybrid
- **Employment type:** Not specified
- **Original posting:** https://boards.greenhouse.io/cloudflare/jobs/8018536?gh_jid=8018536

## Job description

About Us
At Cloudflare, we are on a mission to help build a better Internet. Today the company runs one of the world’s largest networks that powers millions of websites and other Internet properties for customers ranging from individual bloggers to SMBs to Fortune 500 companies. Cloudflare protects and accelerates any Internet application online without adding hardware, installing software, or changing a line of code. Internet properties powered by Cloudflare all have web traffic routed through its intelligent global network, which gets smarter with every request. As a result, they see significant improvement in performance and a decrease in spam and other attacks. Cloudflare was named to Entrepreneur Magazine’s Top Company Cultures list and ranked among the World’s Most Innovative Companies by Fast Company.
At Cloudflare, we’re not looking for people who wait for a polished roadmap; we’re looking for the builders who see the cracks in the Internet that everyone else has simply learned to live with. We value candidates who have the instinct to spot a "normalized" problem and the AI-native curiosity to create a solution using the latest tools. Our culture is built on iteration, leveraging AI to ship faster today to make it better tomorrow, while ensuring that every improvement, no matter how small, is shared across the team to lift everyone up. If you’re the type of person who values curiosity over bureaucracy, and that AI is a partner in solving tough problems to keep the Internet moving forward, you’ll fit right in.
Available Locations: Austin, Texas
About the Role
Cloudflare built its reputation helping build a better Internet, defending millions of sites, giving away SSL and DDoS mitigation when the industry charged premium prices. In an acceleratingly dangerous world, the scope of that mission has changed. We are becoming something more: critical infrastructure. Banks run their payment rails on us. Governments run public services on us. Media companies depend on us during live events. Health systems depend on us to provide care. Reliability for these customers is no longer a feature of our product. It is a mission.
Serving that customer base demands a different operating model. Traditional support organizations route tickets. Traditional engineering organizations ship features. Neither alone is enough when the stakes are this high. We are pivoting to something different: a customer-facing engineering organization, directly engaged with our customers at scale. This is work a central dev team cannot do from the inside of the network.
The Customer Reliability Engineering function is the spine of that pivot. CRE is SRE applied outward, the same engineering discipline, applied to the reliability of the systems our customers run on Cloudflare. You are the engineer who owns the problems that matter most to the customers who matter most, and you contribute directly to our products and tooling, in partnership with Product Engineering, to hold that standard across the entire customer base.
The Role
CRE is a rapid response team and a proactive engineering team. You fix things at the edge as they come up, and you help build the product capabilities that identify customer issues before they become a crisis. Both modes are equally core.
Rapid response.
When a customer issue surfaces that is high-severity, cross-layer and complex, you are the engineer who answers. You reproduce the defect, isolate the root cause across Cloudflare's infrastructure and the customer's stack, drive the fix with Product Engineering, and confirm resolution. You hold on-call for high-severity incidents as part of a global shift rotation.
Proactive engineering.
When no fire is burning, you work with Product Engineering and our platform teams to build the capabilities that make the next fire cheaper or unnecessary: telemetry pipelines that correlate signals across the customer base, detectors that fire before a human notices, diagnostic tooling that scales across hundreds of customers, automation that reduces toil for Customer Support. Every incident you carry generates engineering output that reduces the cost of recurrence. The work compounds.
Cloudflare is building CRE as an AI-native function. You will work with and help build agents and tooling that pre-diagnose incidents, surface relevant logs and configuration, and propose fixes with cited evidence. Engineers who ship AI-assisted diagnostics are the ones defining this discipline.
What You Might Work On
Rapid response:
Own a Sev-1 incident where a large financial services customer sees asymmetric latency from a single POP. Trace it through BGP routing and origin configuration. Produce the fix upstream.
Diagnose a recurring WebSocket disconnect that a media customer has been fighting for weeks. Isolate it to a specific interaction between WAF and their origin load balancer. Drive the fix with Product Engineering.
Partner with a government customer's SRE team during an active DDoS event. Help them shape their Magic Transit and WAF configuration in real time.
Proactive engineering:
Build, with Product Engineering, a distributed tracing capability that correlates Cloudflare edge signals with customer origin metrics so a single query tells the story of a failing request end-to-end.
Ship a detector for a class of WAF false positives silently degrading several customers. Get it into production before the next renewal cycle.
Prototype an AI agent that takes a new customer case, pulls relevant logs and config, and proposes a root cause with linked evidence. Deploy it internally. Measure whether it makes engineers faster. Iterate.
Responsibilities
Rapid incident response and root cause analysis.
Own the most complex, high-severity customer issues end-to-end, from first signal through confirmed resolution. Lead deep-dive debugging across the full stack: edge, network, DNS, transport, APIs, application, customer-side configuration. Reproduce defects, validate fixes with Engineering, and confirm customer-side resolution. Produce postmortems other engineers rely on. Hold on-call for high-severity incidents as part of a global rotation that includes weekends.
Proactive reliability engineering.
Analyze support and telemetry signals across the customer base to find systemic risks before they become incidents. Contribute monitoring, detection, and diagnostic capability to the core product and the engineering systems that give Customer Support early visibility into customer-affecting issues. Define customer-facing reliability metrics (error rates, resolution times, repeat-contact rates) and drive measurable improvement. Write automation that reduces mean-time-to-detect and mean-time-to-resolve.
Cross-functional partnership.
Manage the technical escalation lifecycle with clear ownership and timely communication. Partner with Product Engineering to drive fixes, workarounds, and configuration changes that address underlying gaps. Represent the customer reliability perspective in engineering syncs, incident reviews, and post-mortem processes.
Technical leadership and enablement.
Raise the technical floor of Customer Support through pair-debugging, structured knowledge transfer, and shared tooling. Document diagnostic procedures and resolution patterns in runbooks, internal knowledge bases, and AI skills. Share insights from customer-facing incidents to improve product documentation and operational readiness.
Product and platform depth.
Maintain deep, current expertise across Cloudflare's product portfolio: edge networking, DNS, CDN, WAF, DDoS mitigation, Zero Trust, Workers, and our developer platform. Anticipate customer impact from new releases and architecture changes. Serve as a go-to subject-matter expert in one or more domains.
Requirements
Minimum 5 years of hands-on experience in site reliability engineering, escalation engineering, systems engineering, or a comparable deeply technical support / operations role, with at least 2 years in customer-facing environments.
Strong foundation in networking and security:
TCP/IP fundamentals: OSI model, IPv4/IPv6 addressing, subnetting, routing, switching.
Core protocols: DNS, HTTP/S, TLS/SSL, SMTP, SNMP, NTP.
Routing protocols: BGP, OSPF, including path selection and route propagation.
Firewall concepts: stateful/stateless inspection, rule sets, NAT, ACLs.
VPN and encryption: IPSec, SSL/TLS tunnels, GRE.
Zero Trust architecture, network segmentation, modern security models.
Proficiency with observability and diagnostic tooling: packet capture and analysis (Wireshark, tcpdump), log aggregation (Kibana, Elasticsearch), metrics dashboards (Grafana), distributed tracing.
Strong scripting and automation skills (Bash, Python) with a track record of shipping tooling that improves reliability and reduces toil.
Experience with incident management, postmortem culture, and SLO/SLI-based reliability practices.
Excellent written and verbal communication. Able to convey complex technical information clearly to engineers, leadership, and customers.
Comfort owning ambiguous, cross-layer problems. Composure under pressure during high-severity incidents.
Desired Skills & Experience
SRE, DevOps, or platform engineering experience with direct customer-facing accountability.
Deep expertise at both L3/L4 (network infrastructure) and L7 (application protocols, DNS, HTTP, WebSocket).
Expert-level proficiency with Linux command-line tools: curl, dig, git, traceroute, mtr, strace, ss.
Data-at-scale analysis using SQL, PromQL, or equivalent.
Familiarity with CI/CD pipelines, infrastructure-as-code (Terraform, Pulumi), and container orchestration (Kubernetes, Docker).
Track record of building internal tooling or diagnostic utilities that measurably improved team efficiency.
Demonstrated technical leadership: mentoring engineers, driving cross-team initiatives, influencing outcomes without direct authority.
Experience applying AI/ML to production engineering or operational workflows.
Comfort engaging directly with enterprise customer engineering teams, including on calls during incidents.
Bonus Points
Active Cloudflare user who understands the platform as a practitioner.
Hands-on experience with Workers, Pages, R2, D1, or other developer platform services.
Cloud networking and security experience across AWS, Azure, or GCP.
Web programming (HTML, JavaScript) and regular expressions.
Chaos engineering or formal reliability frameworks (e.g., Google SRE principles).
Managing or configuring non-HTTP services: email, DNS authoritative/recursive, FTP, SSH.
Equity
This role is eligible to participate in Cloudflare's equity plan.
Benefits (may vary by region)
Cloudflare offers a complete package of benefits and programs to support you and your family. Our benefits programs can help you pay health care expenses, support caregiving, build capital for the future, and make life a little easier and fun. The below is a description of our benefits for employees in the United States; benefits may vary for employees based outside the U.S.
Health & Welfare Benefits
Medical/Rx Insurance
Dental Insurance
Vision Insurance
Flexible Spending Accounts
Commuter Spending Accounts
Fertility & Family Forming Benefits
On-demand mental health support and Employee Assistance Program
Global Travel Medical Insurance
Financial Benefits
Short and Long Term Disability Insurance
Life & Accident Insurance
401(k) Retirement Savings Plan
Employee Stock Participation Plan
Time Off
Flexible paid time off covering vacation and sick leave
Leave programs, including parental, pregnancy health, medical, and bereavement leave
What Makes Cloudflare Special?
We’re not just a highly ambitious, large-scale technology company. We’re a highly ambitious, large-scale technology company with a soul. Fundamental to our mission to help build a better Internet is protecting the free and open Internet.
Project Galileo
: Since 2014, we've equipped more than 2,400 journalism and civil society organizations in 111 countries with powerful tools to defend themselves against attacks that would otherwise censor their work, technology already used by Cloudflare’s enterprise customers--at no cost.
Athenian Project
: In 2017, we created the Athenian Project to ensure that state and local governments have the highest level of protection and reliability for free, so that their constituents have access to election information and voter registration. Since the project, we've provided services to more than 425 local government election websites in 33 states.
1.1.1.1
: We released
1.1.1.1
to help fix the foundation of the Internet by building a faster, more secure and privacy-centric public DNS resolver. This is available publicly for everyone to use - it is the first consumer-focused service Cloudflare has ever released. Here’s the deal - we don’t store client IP addresses never, ever. We will continue to abide by our
privacy commitment
and ensure that no user data is sold to advertisers or used to target consumers.
Sound like something you’d like to be a part of? We’d love to hear from you!
Please note that applicants who progress to the offer stage of the interview process may be asked to attend an in-person interview within one of the Cloudflare Offices or Cloudflare Hubs.  More details about this will be available at that stage of the interview process.
This position may require access to information protected under U.S. export control laws, including the U.S. Export Administration Regulations. Please note that any offer of employment may be conditioned on your authorization to receive software or technology controlled under these U.S. export laws without sponsorship for an export license.
Cloudflare is proud to be an equal opportunity employer.  We are committed to providing equal employment opportunity for all people and place great value in both diversity and inclusiveness.  All qualified applicants will be considered for employment without regard to their, or any other person's, perceived or actual
race, color, religion, sex, gender, gender identity, gender expression, sexual orientation, national origin, ancestry, citizenship, age, physical or mental disability, medical condition, family care status, or any other basis protected by law.
We are an AA/Veterans/Disabled Employer.
Cloudflare provides reasonable accommodations to qualified individuals with disabilities.  Please tell us if you require a reasonable accommodation to apply for a job. Examples of reasonable accommodations include, but are not limited to, changing the application process, providing documents in an alternate format, using a sign language interpreter, or using specialized equipment.  If you require a reasonable accommodation to apply for a job, please contact us via e-mail at
hr@cloudflare.com
or via mail at 101 Townsend St. San Francisco, CA 94107.

## Source and provenance

Retrieved from the public greenhouse job feed on 2026-06-24T14:07:22.630601 UTC.
