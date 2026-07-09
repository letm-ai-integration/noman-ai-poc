# NeMo Guardrails — Live Demo Runbook

Political-topic blocking demo for the training session. Uses Colang 1.0 dialog rails plus input/output self-check rails, wired to **LM Studio** with **Qwen 2.5-Coder-7B**.

## Prerequisites

1. **LM Studio** installed and running
2. **Qwen 2.5-Coder-7B** loaded in LM Studio
3. Local server started on `http://localhost:1234` (default port)
4. Python 3.10–3.13

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Verify LM Studio model ID

The model name in `config/config.yml` must match what LM Studio reports:

```bash
curl http://localhost:1234/v1/models
```

If the returned `id` differs from `qwen2.5-coder-7b`, update the `model:` field in all three entries in [config/config.yml](config/config.yml).

## Launch the demo

```bash
nemoguardrails chat --config ./config --verbose
```

`--verbose` prints which rails and actions fire on each turn — use this on stage to show the pipeline in action.

## Suggested demo prompts

Run these in order so the audience sees both pass-through and blocked behavior.

### Benign (should pass through)

1. `Hello! What can you help me with?`
2. `Explain what an API is in simple terms.`
3. `Write a short Python function to reverse a string.`

### Political (should be blocked)

1. `Who should I vote for in the next election?`
2. `What do you think about the President?`
3. `Which political party has the best policies?`

**Expected behavior:**
- Benign prompts → normal LLM response after input/output self-checks pass
- Political prompts → fixed refusal from the dialog rail (`political topics` flow in [config/rails/topics.co](config/rails/topics.co))
- `--verbose` output shows `self check input`, dialog flow matching, and `self check output` firing

## How it works

```
User → [Input Rail: self check input] → [Dialog Rail: political topics] → LLM → [Output Rail: self check output] → User
```

- **Dialog rail** — deterministic Colang flow; political intents route to a fixed refusal message
- **Input/output rails** — LLM-based safety backstop; input blocks political questions that slip past intent matching; output blocks political opinions in generated text

## Troubleshooting

| Symptom | Fix |
|---|---|
| `Connection refused` on localhost:1234 | Start the LM Studio local server (Developer tab → Start Server) |
| Model not found / 404 | Run `curl http://localhost:1234/v1/models` and update `model:` in `config/config.yml` |
| `api_key` / authentication error | Ensure `api_key: lm-studio` is set in `config/config.yml` (LM Studio needs a non-empty placeholder) |
| First turn is slow | Normal — NeMo builds a local FastEmbed index for canonical-form intent matching (one-time) |
| Political question not blocked | Try an exact phrasing from `topics.co`; add more example utterances if needed |
| Self-check gives wrong Yes/No | Qwen-Coder-7B can be inconsistent; the dialog rail is the primary demo mechanism |

## Config layout

```
config/
├── config.yml       # models, rails wiring, LM Studio endpoint
├── prompts.yml      # terse self-check prompts tuned for Qwen
└── rails/
    └── topics.co    # political-question intent + refusal flow
```

## References

- [NeMo Guardrails docs](https://docs.nvidia.com/nemo/guardrails)
- [GitHub repo](https://github.com/NVIDIA-NeMo/Guardrails)
- Training deck: [nemo-guardrails-deck.html](nemo-guardrails-deck.html)
