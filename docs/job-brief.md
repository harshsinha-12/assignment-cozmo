# Job brief (extracted)

Source PDF: `docs/briefs/ai-backend-engineer.pdf`  
Original drop filename contained a newline: `AI Backend Engineer\n.docx.pdf`  
Recruiter: Brynz (saik@brynz.io, https://www.brynz.tech)

Do not re-extract the PDF unless this file is suspected incomplete. The PDF is two pages of JD, **not** the take-home problem.

## Header (as printed)

- **Title:** AI Backend Engineer
- **Company:** Cozmo AI · In-Office · New York · YC W25
- **Location (sidebar):** India Remote / Abu Dhabi
- **Employment:** Full-time
- **Experience:** 1–4 years (body also says 0–4, new grads welcome)
- **Salary (sidebar):** 50 LPA
- **Work type:** In-office, 996
- **Stage (sidebar):** YC W22
- **Team size:** ~5
- **Equity:** 0.14% – 2.00%

The sidebar and the body disagree on intern-friendly details (W22 vs W25, India remote vs NY 996). Treat the **body** as the company’s self-description and the sidebar as a recruiter form that may be stale. Do not spend interview time on this contradiction.

## About Cozmo AI (JD text, cleaned)

Cozmo AI is the AI operating system for property claims. When a pipe bursts in someone’s home at 2am, Cozmo’s agents answer the call, capture the loss, enter the claim into Xactimate and Cotality, dispatch the right contractor against SLA, chase acceptances before breach, and draft the carrier-ready estimate from field photos.

Cozmo runs both halves of a claims operation: everything the customer touches, and everything that happens behind the desk.

Customers are restoration franchisors, TPAs, and adjusting firms whose boards have told them to become AI-native and who have no way to do it themselves. The anchor customer is one of the largest restoration franchisors in the US. Backed by Y Combinator (W25), Dubai Future District Fund, and global VCs. HQ in San Francisco.

## About the role (JD text, cleaned)

A claim is a hostile engineering environment. The data lives in Xactimate files, carrier portals, Zendesk queues, voicemails, and photos of wet drywall. The workflows were designed twenty years ago and enforced by franchise agreements. SLAs are measured in minutes and breaches cost real money.

The job is to walk into that environment, reason from first principles about what the system should be, then build agents that run it in production. Time is split between customer operations and platform code. The distance between “I saw a dispatcher waste an hour on this” and “an agent now does it” should be days — and you own the whole distance. Report to the CTO; work with both founders.

Cozmo works almost six days a week, in person in New York — 9am to 9pm (996) — and go-live weeks take the seventh day. Intensity is framed as the structural advantage against incumbents with 100× headcount.

## What you’d do

- Deploy into enterprise claims operations and own technical outcomes end to end
- Build production agent systems: prompt architectures, tool use, routing, evals, fallbacks, and glue between LLMs and systems that were never meant to have APIs
- Reverse engineer legacy claims software (Xactimate, Cotality, carrier portals) and make it programmable
- Design the data layer as you go — every claim generates hundreds of structured data points; those pipelines are the moat
- Ship during live go-lives with hard dates and executives watching, including hurricane-season surges
- Convert field solutions into platform primitives so each deployment is faster than the last

## Must-haves

- Exceptional CS fundamentals (or self-taught equivalent with proof); they test thinking directly
- 0–4 years; new grads welcome if the work is stronger than the resume
- Python or TypeScript, full stack enough to go empty-repo → production alone
- Hands-on LLM engineering: agents, evals, knowing where models break — not “I called an API in a notebook”
- First-principles reasoning; willing to redesign a 20-year workflow and defend it to the person who runs it
- Inspectable ambition: research, startup, OSS, competitions, something shipped
- Wants to be around customers (FDE energy)
- Committed to 996 in-office New York — stated as non-negotiable

## Nice-to-haves

- Voice AI, telephony, or real-time systems
- Insurance, claims, or field services
- Competitive programming, olympiads, or research record

## Interview process (as printed)

1. Profile shortlist
2. Take-home assignment
3. Technical discussion
4. Culture fit
5. Offer

## Why this JD matters for the take-home

They will not grade a pretty notebook. They will grade whether you:

- Turn messy field input into **structured data**
- Build something that could sit behind an agent (tool, schema, evals, fallbacks)
- Know where the method breaks
- Could explain it to a restoration operator without lying about accuracy

The floor-plan problem is a slice of “draft the carrier-ready estimate from field photos.”
