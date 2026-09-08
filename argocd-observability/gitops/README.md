# GitOps repository layout

```
argocd-observability/gitops/
├── bootstrap/
│   └── root-app.yaml                  # app-of-apps — the only manifest applied by hand
├── projects/
│   └── observability.yaml             # AppProject — repo/namespace/kind allowlist
├── apps/                              # Argo CD Applications, one file per component
│   ├── 00-prometheus-operator-crds.yaml   # sync-wave -2
│   ├── 10-kube-prometheus-stack.yaml      # sync-wave  0
│   ├── 20-loki.yaml                       # sync-wave  1
│   └── 30-alloy.yaml                      # sync-wave  2
└── values/                            # Helm values, kept OUT of the app manifests
    ├── kube-prometheus-stack/
    │   ├── values.yaml                # base
    │   └── values-dev.yaml            # environment overlay
    ├── loki/
    │   └── values.yaml
    └── alloy/
        └── values.yaml
```

## Why this shape

**`apps/` is separate from `values/`.** The `Application` manifest answers
*what and where*; the values file answers *how*. Reviewing a values change then
does not mean re-reviewing sync policy, and vice versa. The numeric filename
prefixes are for humans reading `ls` — Argo CD orders by sync-wave, not by name.

**Values live in git, not inline in the Application.** You *can* inline them
with `helm.valuesObject`, but then every tuning change edits an Argo CD CRD, you
lose YAML schema support in your editor, and `helm template -f` becomes
impossible to run locally. Keep them as real files.

**Charts are consumed, never forked.** Multi-source (`ref: values`) combines an
upstream chart with local values. Vendoring a copy of kube-prometheus-stack into
this repo means manually tracking upstream releases forever.

**One AppProject per blast radius.** `default` allows any repo, any cluster, any
namespace, any kind. The `observability` project names four repos and two
namespaces; anything else is rejected at admission.

## The multi-source pattern, precisely

```yaml
sources:
  - repoURL: https://prometheus-community.github.io/helm-charts
    chart: kube-prometheus-stack
    targetRevision: 90.0.0
    helm:
      valueFiles:
        - $values/argocd-observability/gitops/values/kube-prometheus-stack/values.yaml
  - repoURL: https://github.com/BoldFellow/aws-mini-lessons.git
    targetRevision: main
    ref: values           # defines $values
```

Rules that are easy to get wrong:

| Rule | Consequence if broken |
|---|---|
| `$values` may only appear at the **start** of the path | Path is not substituted; Helm errors on a missing file |
| `$values` resolves to the **root of the ref'd repo**, ignoring its `path` | Silently reads the wrong file |
| A source with `ref` must **not** also set `chart` | Argo CD rejects the Application |
| When `sources` is set, the singular `source` field is **ignored** | Your edits to `source:` do nothing |
| Keep it to 2–3 sources | Multi-source is not a grouping mechanism — use app-of-apps |

### The `valueFiles: [values.yaml]` trap

For a chart pulled from a Helm repo, a bare `values.yaml` in `valueFiles`
resolves **relative to the chart root** — that is, the chart's own default
values file, which Helm already loads. It does *not* pull `values.yaml` from
your git repo. The Application syncs, reports Healthy, and applies pure
upstream defaults. Use the `$values` form above instead.

## Value precedence

`parameters` > `valuesObject` > `values` > `valueFiles` (later files win) >
the chart's own `values.yaml`.

## Bootstrap

```bash
kubectl apply -f projects/observability.yaml
kubectl apply -f bootstrap/root-app.yaml
```

Everything else is pulled in by the root app.
