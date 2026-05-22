# Installation instructions for Cert-Manager and security enhancements

## Prerequisites

```bash
# 1. Install cert-manager using Helm
helm repo add jetstack https://charts.jetstack.io
helm repo update

helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --version v1.13.0 \
  --set installCRDs=true

# 2. Verify installation
kubectl get pods --namespace cert-manager
kubectl get crd | grep cert-manager
```

## Apply Security Manifests

```bash
# Apply RBAC
kubectl apply -f deployment/k8s/base/security/rbac.yaml

# Apply cert-manager configuration
kubectl apply -f deployment/k8s/base/security/cert-manager.yaml

# Verify Certificate was created
kubectl get certificate -n portfolio
kubectl describe certificate portfolio-cert -n portfolio
```

## Testing Certificate Generation

```bash
# Check if certificate secret was created
kubectl get secret portfolio-tls-secret -n portfolio

# Decode and view certificate
kubectl get secret portfolio-tls-secret -n portfolio \
  -o jsonpath='{.data.tls\.crt}' | base64 -d | openssl x509 -text -noout

# Test HTTPS access (after DNS configured)
curl -v https://portfolio.local/it-compass
```

## Troubleshooting

### Certificate not generated

```bash
# Check cert-manager logs
kubectl logs -n cert-manager -l app.kubernetes.io/name=cert-manager

# Check Certificate status
kubectl describe certificate portfolio-cert -n portfolio

# Check ClusterIssuer status
kubectl describe clusterissuer letsencrypt-prod
```

### ACME Challenge failing

```bash
# Check for challenges
kubectl get challenges -n portfolio

# Describe specific challenge
kubectl describe challenge <challenge-name> -n portfolio

# Check ingress ACME solver logs
kubectl logs -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx
```

## Production Configuration

For production, update:

1. **Email**: Replace `your-email@example.com` with real email
2. **Domain**: Update `dnsNames` to your actual domain
3. **Ingress**: Update `host` in ingress rules
4. **ClusterIssuer**: Use `letsencrypt-prod` (not staging)

```yaml
# Update ClusterIssuer reference
spec:
  issuerRef:
    name: letsencrypt-prod  # NOT letsencrypt-staging
    kind: ClusterIssuer
```

## Automatic Certificate Renewal

Cert-manager automatically:
- Renews certificates 30 days before expiration
- Handles renewal challenges
- Updates TLS secrets

Monitor renewal:
```bash
kubectl get certificate -n portfolio -w
```

## Security Headers

The ingress includes security headers:
- `X-Frame-Options: DENY` - Prevent clickjacking
- `X-Content-Type-Options: nosniff` - Prevent MIME sniffing
- `X-XSS-Protection` - XSS protection
- `Referrer-Policy` - Control referrer information
- `Strict-Transport-Security` - Force HTTPS (add manually if needed)

## Next Steps

1. Install cert-manager in your cluster
2. Configure your DNS records to point to ingress IP
3. Apply security manifests
4. Monitor certificate generation
5. Test HTTPS access
