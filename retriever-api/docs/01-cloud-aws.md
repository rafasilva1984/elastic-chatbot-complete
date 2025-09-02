# Cloud AWS — Boas Práticas Corporativas
- **Multi-account**: separe produção, homologação e dev em contas diferentes.
- **Tagging**: todo recurso deve ter `Owner`, `Projeto`, `CustoCenter`.
- **FinOps**: use AWS Cost Explorer e relacione com Elastic para acompanhar custo por time.
- **Segurança**: nunca use usuário root; políticas devem ser aplicadas via IAM Roles.
