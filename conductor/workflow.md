# Project Workflow (Toy Project Edition)

## Guiding Principles

1. **The Plan is the Source of Truth:** All work must be tracked in `plan.md`.
2. **The Tech Stack is Deliberate:** Changes to the tech stack must be documented in `tech-stack.md` *before* implementation.
3. **Flexible Workflow:** Priorities are speed and experimentation over strict process adherence.
4. **User Experience First:** Every decision should prioritize user experience.
5. **Non-Interactive & CI-Aware:** Prefer non-interactive commands. Use `CI=true` for watch-mode tools to ensure single execution.

## Task Workflow

All tasks follow a lightweight lifecycle:

### Standard Task Workflow

1. **Select Task:** Choose the next available task from `plan.md`.

2. **Mark In Progress:** Edit `plan.md` and change the task from `[ ]` to `[~]`.

3. **Implement:** Write the code to fulfill the task requirements.

4. **Run Tests:** Execute relevant automated tests (e.g., `pytest`) to verify the implementation and ensure no regressions.

5. **Verify (Lightweight):** Ensure the changes work as expected (manual verification is acceptable).

6. **Document Deviations:** If implementation differs from tech stack:
   - Update `tech-stack.md` with new design.
   - Resume implementation.

7. **Get and Record Task:**
    - **Update Plan:** Read `plan.md`, find the line for the completed task, update its status from `[~]` to `[x]`.
    - **Write Plan:** Write the updated content back to `plan.md`.

### Phase Completion Verification Protocol

**Trigger:** This protocol is executed immediately after a task is completed that also concludes a phase in `plan.md`.

1.  **Announce Protocol Start:** Inform the user that the phase is complete and the verification protocol has begun.

2.  **Verify Functionality:**
    -   Run any available automated tests: `npm test` or equivalent (if applicable).
    -   Perform manual verification of the features implemented in this phase.

3.  **Announce Completion:** Inform the user that the phase is complete.

### Quality Gates

Before marking any task complete, verify:

- [ ] Functionality meets the task description.
- [ ] Code is reasonably clean and readable.
- [ ] Basic happy-path scenarios work.

## Development Commands

**AI AGENT INSTRUCTION: This section should be adapted to the project's specific language, framework, and build tools.**

### Setup
```bash
# Example: Commands to set up the development environment
# e.g., pip install -r requirements.txt
```

### Daily Development
```bash
# Example: Commands for common daily tasks
# e.g., python main.py
```

## Testing Requirements (Optional)

### Unit Testing
- Write tests for complex logic where helpful.
- Focus on critical paths.

### Integration Testing
- Verify that key components work together.

## Code Review Process

### Self-Review Checklist
Before finishing a task:

1. **Functionality:** Does it work?
2. **Code Quality:** Is it readable?
3. **Security:** No obvious security holes (e.g., committed secrets).

## Definition of Done

A task is complete when:

1. Code implemented to specification.
2. Feature verified (manually or automatically).
3. Implementation notes added to `plan.md` (if useful).

## Emergency Procedures

### Critical Bug
1. Fix it.

## Deployment Workflow (Simplified)

1. Ensure code works locally.
2. Deploy/Publish.
