# Deployment Commands

## Render.com

Git hub action listens to all `prod-ui-*`, `prod-api-*` tags.
But prefer to create version tags in form `v*`.

Create `prod-ui-v*` and/or `prod-api-v*` tags when you want to
deploy ui and/or api to prod on render.com.

```bash
> git tag v1.0.3
> git tag prod-ui-v1.0.3
> git tag prod-api-v1.0.3
```
```bash
> git push origin v1.0.3 prod-ui-v1.0.3 prod-api-v1.0.3
```