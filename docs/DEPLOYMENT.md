# Deployment Commands

## Render.com

### finnikacc-ui

Git hub action listens to all tags `prod-*`.
But prefer to create both `v*` and `prod-v*` for versioning consistency.

```bash
> git tag v1.0.3
> git tag prod-v1.0.3
```
```bash
> git push origin v1.0.3 prod-v1.0.3
```