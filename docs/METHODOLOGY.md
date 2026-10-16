# Evaluation method and limits

ControlCanvas compares an untrusted frontend-code builder with a code
inspector. It stores code, raw model responses, labels, inspector decisions,
and status fields so a reviewer can inspect why a run was counted or excluded.

## Ground-truth boundary

The simulation builder returns `html` plus a `ground_truth` object. Those
labels describe the builder's stated intent; they are **model self-reports**,
not an independent executable oracle. The inspector receives the user request
and generated HTML, not the builder's label object.

Validation checks that HTML and label fields exist and that boolean labels
match the planned benign/adversarial case. It does not prove the HTML actually
implements the labelled behaviour. A builder may claim an attack without
implementing it, or omit behaviour from its explanation.

Before treating model-mode results as research evidence, independently review
the code/behaviour and save adjudicated labels outside the model decision.
Automatic manual-review persistence and independent execution-based label
verification are not implemented. Existing screenshots are illustrations, not
new benchmark results.

## Invalid runs

- Missing/malformed builder HTML: `BUILDER_FORMAT_ERROR`.
- Missing or contradictory builder labels: `INVALID_GROUND_TRUTH`.
- Missing/unparseable inspector JSON or a non-boolean `detected` field:
  `INSPECTOR_FORMAT_ERROR`.
- Request failures: `REQUEST_ERROR`.

These runs retain available raw responses and are excluded from confusion
counts. An invalid inspector result never inherits the expected answer from
the planned case. TP/FP/FN/TN use valid rows and the declared label; they remain
conditional on the reliability of that label.

“Flagged for repair” counts detected adversarial cases. It does not measure a
successful repair; rewritten code is not independently re-evaluated here.

## Fixture mode

`USE_FAKE_DATA=true` returns predefined responses without calling a model.
It exercises the UI and request pipeline, including a fixed inspector result.
Perfect scores in this mode are expected fixtures, not evidence that an LLM
detects attacks. The UI displays the current execution mode.

## Preview isolation

Generated HTML is displayed in an iframe with `sandbox="allow-scripts"` and
without `allow-same-origin`. This separates its origin from the parent UI; it
does not make arbitrary JavaScript safe or block all network access. Use
synthetic inputs. This is a local research tool, not a hardened malware lab.

The HTTP server binds to loopback. It does not serve dotfiles such as `.env`
or Git metadata. The model key stays on the server; code/text sent in model
mode goes to the configured OpenAI endpoint.

## Regression checks

```bash
python -m unittest discover -s tests -v
node --test tests/evaluation.test.cjs
```

Tests cover a fixture-mode server cycle without API calls, input rejection,
malformed inspector responses, private-file protection, label consistency,
invalid-run exclusion, preserved true/false decisions, and confusion counts.
They test the harness, not any model's detection quality.
