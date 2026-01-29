How to Use, Create, and Maintain Documentation

This page is the single source of truth for how the Data Team uses Confluence.
It serves as:

A New Hire onboarding guide

A Team-wide SOP

A reference for contributors and admins

 How to Use This Page

New to the team?
Start with Sections 1–3 to learn how Confluence works here.

Creating content?
Go to Section 4 (Creating Pages).

Maintaining documentation?
See Section 5 (Maintenance).

Admin?
Jump to Section 7 (Governance & Audits).

Context & Best Practices

(Mental model for using Confluence)

1.1 Why Confluence Matters on the Data Team

Confluence is the Data Team’s single source of truth. It allows us to:

Scale knowledge beyond individuals

Reduce repeated questions and rework

Preserve decisions, assumptions, and learnings

Onboard new teammates efficiently

If information is:

Referenced more than once

Needed by more than one person

Important for continuity

It belongs in Confluence.

1.2 What Confluence Is (and Isn’t)

Confluence Is

Authoritative documentation

Shared team knowledge

A reference for how things work

A long-term memory for the team

Confluence Is Not

A personal notebook

A scratchpad for incomplete thoughts

A place for content without ownership

If no one owns it, it will eventually be wrong.

1.3 How We Organize Information

We organize Confluence to answer three questions quickly:

What is this about?

Who is this for?

How does it relate to other content?

To support this:

We avoid deep hierarchies

We require landing pages that explain what lives underneath

Structure & Navigation Standards

2.1 Preferred Hierarchy

Data Team Space

└── Parent Page (context + navigation)

    ├── Supporting Page

    ├── Supporting Page

    └── Subsection Page (only if necessary)

Best Practices

Maximum depth: 3 levels

Every page has a clear parent

Parent pages explain content — they don’t just group it

2.2 Landing Pages (Requirement)

Every Parent Page must include:

Purpose of the section

Intended audience

Description of what’s included

Links or a table of contents

If you cannot explain a section clearly, the structure likely needs revision.

Finding Information (New Hire Guide)

When you’re looking for something:

Start at the nearest Parent Page

Read the description — it should guide you

Use labels and search if needed

Check page metadata:

Owner

Status

Last reviewed date

If you can’t find something you expect to exist:

Ask in Data Team channel or

Create it (following the rules below)

Creating Content

(Rules + Step-by-Step Instructions)

4.1 Should I Create a New Page? (Quick Check)

Create a page if:

Someone else will reference this later

This explains how or why something works

This documents a decision or process

Do not create a page if:

It’s personal notes

It’s speculative or unfinished

You can’t define an audience

4.2 Page Creation Checklist (Required)

Use this checklist every time you create a page

 Required Metadata

☐ Owner

☐ Backup Owner (required for SOPs / core docs)

☐ Target Audience

☐ Document Status (Draft / In Progress / In Review / Verified)

☐ Last Reviewed Date

☐ Next Review Date

☐ At least one label

Pages missing any of the above are considered incomplete.

The Template Meeting Notes Page can be used as an example

4.3 Ownership Rules

Owners

Accountable for accuracy

Responsible for reviews and updates

Decide when content is archived or merged

Backup Owners

Provide continuity

Must understand the content

Step in if Owner is unavailable

Backup Owners are required for:

SOPs

Core workflows

Business-critical documentation

4.4 Editing Rules

Edit Type

Allowed Action

Typos / formatting

Anyone

Logic or process changes

Notify Owner/Backup

Structural changes

Owner approval required

4.5 Writing & Formatting Standards

Required Formatting

H1: Page title

H2: Main sections

H3: Subsections

Writing Best Practices

Define acronyms on first use

Write for someone new to the topic

Explain why, not just what

Link to prerequisite knowledge

Avoid:

“As usual”

“Standard process”

“Everyone knows”

4.6 Labels & Discoverability

Label Rules

All pages must be labeled on creation

Use existing labels whenever possible

Labels describe what the page is

Common labels:

SOP

Project

Documentation

Internal-Guide

External-Guide

Template

Meeting-Notes

CDS

Admins periodically clean up unused or duplicate labels.

4.7 Project Documentation

Creating a Project

Use the Project Template

Create a dedicated Parent Page

Assign Owner and Backup

Link related documentation (don’t duplicate)

4.7.1 Data Science / ML Projects: Confluence vs README.md (Technical Guidance)

Principle: avoid duplication. Confluence is the index + narrative; the repo is the executable source of truth.

README.md should contain (repo-local technical truth)

- Problem statement and success metrics (what “good” looks like)
- How to run: local setup, environments, required secrets (.env.example), and common commands
- Data contracts: sources, schemas, access requirements, PII notes, and refresh cadence
- Training/evaluation/scoring steps (including reproducibility notes)
- Model notes: assumptions, limitations, monitoring signals, rollback/retrain procedure
- Operational details: backfills, deployments, and troubleshooting

Confluence should contain (cross-team context + governance)

- High-level overview for non-engineers, scope, and stakeholders
- Decision log and trade-offs (why we built it this way)
- Ownership (Owner + Backup), status, review cadence, and links to repo + dashboards
- Runbook links (incident/maintenance playbooks) when the system is productionized

Linking rules (required)

- Every DS/ML project Confluence Parent Page must link to the repo README.md
- Every DS/ML repo README.md must link back to the Confluence Parent Page
- If content needs code examples or commands, keep it in README.md and link from Confluence (don’t paste-and-forget)

Project Lifecycle Expectations

Phase

Documentation Expectation

Active

Regular updates

Paused

Status clearly marked

Completed

Final summary added

Archived

Working docs archived

4.8 Drafts, Live Pages & Publishing

Live Pages

Use when:

Actively collaborating

Expecting frequent edits

Convert to standard pages when:

Content stabilizes

It becomes reference material

Publishing Rule

If a page isn’t ready to help someone else, don’t publish it yet.

Maintenance & Content Lifecycle

5.1 Review Cadence

Content Type

Review Frequency

SOPs

Every 6 months

Technical Docs

Every 6–12 months

Project Pages

At phase changes

Owners are responsible for initiating reviews.

5.2 Archiving Process

Content may be archived when:

Outdated

Superseded

No longer relevant

Process:

Owner is notified

Owner chooses:

Update

Merge

Archive

Archived pages remain searchable but clearly marked

Reference: Confluence Elements

Element

When to Use

Parent Pages

Context & navigation

Live Pages

Active collaboration

Pages

Stable documentation

Templates

Repeatable content

Governance & Admin Reference

7.1 Admin Responsibilities

Data Team Space Admins:

Maintain structure and permissions

Review unowned, unlabeled, or expired content

Enforce SOP standards

Facilitate improvements

Admins are facilitators, not gatekeepers.

Role

Permissions

Who

Admin

All Space Permissions, including user management and content archival

People leaders

Data and Analytics Team User

Can add/delete content

Can add comments

Can manage attachments

Can export from space

ICs

Enterprise User

Can view content

Can add but not delete comments

Can add attachments

Non-Data & Analytics Team Members

7.2 Quarterly Admin Audit Checklist

Admins should review the following quarterly

Structure & Hygiene

☐ No orphaned pages

☐ No content >3 levels deep

☐ Landing pages present and descriptive

Metadata & Ownership

☐ All pages have Owners

☐ Backup Owners on critical docs

☐ Review dates are current

Labels

☐ No unlabeled pages

☐ No duplicate/unused labels

Content Quality

☐ No blank or abandoned drafts

☐ Outdated content archived or merged

Decision Tree: “Should This Be a Confluence Page?”

Is this useful to someone else?

        |

       No → Don’t create a page

        |

       Yes

        |

Will it be referenced again?

        |

       No → Consider Teams or notes

        |

       Yes

        |

Can you define an audience & owner?

        |

       No → Clarify first

        |

       Yes → Create a Confluence page

Templates (Required)

Use approved templates for:

Projects

SOPs

Technical Documentation

Meeting Notes

Templates are maintained by Space Admins.

Final Thought

Confluence works when:

Content is intentional

Ownership is clear

Maintenance is shared

This page is our shared agreement for how documentation works on the Data Team. If something feels unclear, outdated, or hard to find, raise it to the Confluence Admins.