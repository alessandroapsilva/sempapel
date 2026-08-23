# Política de versões e branches

## Versão atual

A versão oficial desta linha é **v11.5.100** e a branch de produção correspondente é **`release/11.5.100`**.

O projeto-base continua com `11.5-SNAPSHOT` nos módulos Maven para preservar compatibilidade interna. O número de revisão da distribuição é definido por `.mvn/maven.config` com `-Dpatch.version=100`, produzindo o identificador humano `v11.5.100` e o `Build-Label` com o SHA curto do commit.

## Numeração de releases

A linha 11.5 passa a usar revisão numérica crescente:

- `v11.5.100` — primeira release de produção consolidada;
- `v11.5.101` — próxima release/hotfix;
- `v11.5.102` — release seguinte;
- e assim sucessivamente.

Cada versão publicada deve ter sua própria branch imutável de release, por exemplo `release/11.5.101`. Depois que uma versão entra em produção, não se reescreve seu histórico; correções entram na próxima revisão.

## Branches oficiais

- `develop/11.5` — linha de desenvolvimento e integração da série 11.5;
- `release/11.5.100` — release atual de produção.

As branches abaixo são legado e não devem receber novos commits:

- `release/11.5.cem`;
- `release/11.5-enfas`;
- `release/enfas-production-2026-08`;
- `feat/classificacoes-sp-uape-2026`;
- `release/11.5` — base histórica/upstream do fork.

## Fluxo de trabalho

1. Novas correções entram em `develop/11.5`.
2. Quando o conjunto estiver aprovado, cria-se a próxima branch, por exemplo `release/11.5.101`.
3. Na nova release, atualizar `VERSION` e `.mvn/maven.config` para o mesmo número.
4. Executar build limpo, testes, backup, implantação controlada e aceite funcional.
5. Registrar o SHA exato do commit implantado.
6. Não alterar migrations já aplicadas em produção; novas mudanças de banco recebem nova migration.
7. Não renumerar documentos já finalizados.

## Identificação do WAR

Para a release atual, o manifesto deve conter:

```text
Patch-Version: 100
Build-Label: v11.5.100-<commit-curto>
```

Isso permite identificar rapidamente a versão funcional e o commit exato de qualquer WAR implantado.
