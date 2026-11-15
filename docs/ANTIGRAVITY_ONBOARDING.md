# Antigravity project onboarding — MANSI

## Required local preparation

1. Open `C:\Users\HP\Downloads\aivision` in Antigravity as a Project.
2. Confirm Git recognizes the `main` branch and `origin` points to `https://github.com/NIHAL-PM/MANSI.git`.
3. Attach only this repository folder. Do not attach a home directory, another repository, credential directory, or cloud-synced personal folder.
4. Read `AGENTS.md` at the start of every conversation.

## Project permissions

Use the project's **Default** preset. If the installed Antigravity version exposes **Auto**, it is acceptable only when its policy still asks before risky or irreversible commands.

Configure the following boundary:

| Setting | Required value |
|---|---|
| Project folders | `C:\Users\HP\Downloads\aivision` only |
| Agent file access inside project | Read/write |
| Outside-project file access | Always Ask |
| Terminal execution | Default/Auto, not unrestricted |
| Git work mode for implementation | New Worktree |
| Browser permissions | Ask before uploads, posts, permission changes, and secret entry |
| Production deployment, database migration, or credential creation | Human approval required |

These restrictions still let agents fully implement their assigned scopes while preventing cross-project data access and accidental destructive operations. Antigravity project permissions are scoped to its folders, and New Worktree mode provides an isolated checkout per concurrent conversation. See the official [Antigravity Projects documentation](https://antigravity.google/docs/projects) and [Settings documentation](https://antigravity.google/docs/settings?tab=ide).

## Parallel-agent protocol

1. The integration lead creates the GitHub Project item before creating an agent conversation.
2. The agent starts a New Worktree conversation named after the ticket, for example `PROJ-201 backend ingestion gateway`.
3. Paste the ticket link and the following instruction at the top of the conversation:

   ```text
   You own only the paths specified in GitHub Project item PROJ-XXX. Read AGENTS.md and the linked manual sections. Work in this new worktree; do not modify other paths, use secrets, change GitHub settings, deploy, or merge. Open one pull request with tests and exact command output.
   ```

4. Give each ticket a distinct worktree and branch. No two agents may share a branch, worktree, or scope lock.
5. Queue integration tickets only after their dependency tickets are merged.

## Capacity and escalation

The number of concurrent agents is determined by the Antigravity account, product plan, and runtime capacity; it is not safely or truthfully set to “unlimited.” Start only as many agents as have non-overlapping tickets and isolated worktrees. The project board is the concurrency limiter: a ticket cannot enter **In Progress** until dependencies are complete and the scope lock is unique.

## Before the first agent

- GitHub authentication is active.
- `main` branch protection is enabled: pull request required, review required, status checks required, force pushes disabled, deletion disabled.
- The Project board uses fields: Status, Epic, Agent Role, Dependencies, Scope Lock, Priority, and Release.
- The repository contains the initial architecture/manual commit.
- Each agent receives an issue URL, not an unscoped instruction.
