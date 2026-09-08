# GitOps layout

```
gitops/
├── bootstrap/root-app.yaml        # app-of-apps — the only manual apply
├── projects/observability.yaml    # AppProject: repo/namespace/kind allowlist
├── apps/                          # one Application per component
│   ├── kube-prometheus-stack.yaml # sync-wave 0
│   ├── loki.yaml                  # sync-wave 1
│   └── alloy.yaml                 # sync-wave 2
└── values/<app>/values.yaml       # Helm values, kept out of the manifests
```

`apps/` says *what and where*; `values/` says *how*. Reviewing a tuning change
then doesn't mean re-reviewing sync policy. Argo CD orders by sync-wave, not by
filename.

## The multi-source pattern

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

**The trap:** for a chart from a Helm repo, a bare `values.yaml` in `valueFiles`
resolves relative to the *chart root* — the chart's own defaults, which Helm
already loads. It does not pull `values.yaml` from your git repo. The app syncs,
reports Healthy, and deploys pure upstream defaults. Use the `$values` form.

Other rules worth knowing: `$values` only at the start of a path; it resolves to
the ref'd repo's root regardless of that source's `path`; a `ref` source must not
also set `chart`; and when `sources` is set, the singular `source` is ignored.

Value precedence: `parameters` > `valuesObject` > `values` > `valueFiles`
(later files win) > the chart's own `values.yaml`.

## Bootstrap

```bash
kubectl apply -f projects/observability.yaml
kubectl apply -f bootstrap/root-app.yaml
```

## Adding an environment

Add `values/<app>/values-prod.yaml`, list it after `values.yaml` in a second
Application's `valueFiles`, and set `ignoreMissingValueFiles: true`. Keep in the
overlay anything that depends on a fact this repo can't know — hostnames, TLS
assumptions, IdP endpoints, replica counts.

## Credentials

No AWS credentials anywhere in this tree: EKS Pod Identity binds the IAM role
from the AWS side, so not even a role ARN appears here. Grafana's admin password
comes from a Secret created out of band.
