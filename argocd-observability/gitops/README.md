# GitOps layout

```
gitops/
├── bootstrap/root-app.yaml            # app-of-apps — the only manual apply
├── projects/
│   ├── bootstrap.yaml                 # root app: may create Applications, nothing else
│   └── observability.yaml             # the stack: repo/namespace/kind allowlist
├── apps/                              # one Application per component
│   ├── 00-prometheus-operator-crds.yaml   # wave -2
│   ├── 10-kube-prometheus-stack.yaml      # wave  0
│   ├── 20-loki.yaml                       # wave  1
│   └── 30-alloy.yaml                      # wave  2
├── values/<app>/
│   ├── values.yaml                    # base — true everywhere
│   ├── values-dev.yaml                # loaded by the Applications above
│   └── values-prod.yaml               # NOT loaded; template for a prod Application
└── examples/                          # reference manifests, deployed by nothing
```

Filename numbers are for humans reading `ls`; Argo CD orders by sync-wave.

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

## Why CRDs are their own Application

The Prometheus CRDs are over 1 MB, and Helm will not upgrade CRDs shipped in a
chart's `crds/` directory. As a separate chart in wave -2 a CRD bump is an
ordinary sync, and `prune: false` on it means a mis-sync can never
cascade-delete every ServiceMonitor in the cluster. `crds.enabled: false` in
the stack's values prevents double ownership.

## Bootstrap

```bash
kubectl apply -f projects/bootstrap.yaml
kubectl apply -f projects/observability.yaml
kubectl apply -f bootstrap/root-app.yaml
```

## Base vs. overlay

The split is not dev-vs-prod convenience — it is **whether the setting depends
on a fact this repo cannot know**. `cookie_secure: true` is objectively more
secure and still belongs in the overlay, because it silently breaks the session
cookie unless Grafana really is reached over HTTPS. A hardening setting applied
to the wrong deployment shape is an outage, not a hardening.

Base carries what is true everywhere. The overlay carries hostnames, TLS
assumptions, IdP endpoints, bucket names and replica counts. A placeholder that
looks plausible is worse than an absent value, because the plausible one ships.

For a production instance, add a second Application per component pointing at
`values.yaml` + `values-prod.yaml`.

## Credentials

No AWS credentials anywhere in this tree: EKS Pod Identity binds the IAM role
from the AWS side, so not even a role ARN appears here. Grafana's admin password
comes from a Secret created out of band.
