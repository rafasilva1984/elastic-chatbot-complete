# Padrão de CI/CD da Empresa
- **CI**: cada PR roda testes unitários, lint e build.
- **CD**: deploy automatizado via pipelines GitHub Actions + ArgoCD.
- **Branching**: usamos GitFlow simplificado (`main`, `develop`, `feature/*`).
- **Observabilidade**: cada deploy gera evento em Elastic APM para rastreabilidade.
