# Implement your own adapter

Start with `aptflow_core/adapters.py`. No built-in live provider is implemented; endpoint or billing behavior is not assumed.

An adapter implements `execute(payload: dict) -> dict`. Earlier results are passed under their role names:

| Role | Input | Expected result |
|---|---|---|
| memory | Empty context | Compact relevant summary and optional sources |
| research | Optional memory | evidence: unique id, HTTPS url, finding |
| script | Prior context | scenes: title, body, integer seconds, evidence_ids |
| video | script and research | Current storyboard contract: scenes and evidence |

The current runner validates a storyboard. A real avatar provider requires extending the delivery contract to handle media; do not label a storyboard as a generated video.

1. Implement a class matching the Adapter protocol in your own module.
2. Register its role/name in SPECS and declare required environment variable names.
3. Register its constructor in create_adapter; do not use the mock factory for a real provider.
4. Select it in your private configuration. Demo mode rejects non-mock adapters.
5. Update workflow.run for live results: do not reuse the synthetic flag or mock cost/status fields. Record actual usage or unknown charges.
6. Add offline contract/failure fixtures before opting into live tests with your own credentials.

Read credentials at execution time from the environment. Never return them in results or errors. Do not execute instructions copied from retrieved web pages.

For asynchronous providers persist the returned job ID before polling. Reconcile that job after timeout before any retry. Use bounded waits and an explicit unknown-completion state. Keep network work opt-in; never trigger it from init, doctor, plan or tests.

NotebookLM is optional and requires your own authentication plus notebook selection. Never ship a session, private notebook UUID, personal memory or another user's browser profile.

Document implemented operations, auth, output contracts and remaining limitations. Adding a credential variable alone is not an integration.
