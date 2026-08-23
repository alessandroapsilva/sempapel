# Linha de releases CEM

Esta distribuição mantém compatibilidade com o SIGA-DOC 11.5 e usa uma identificação institucional separada para permitir rastreabilidade sem alterar as coordenadas Maven legadas dos módulos.

## Versão atual

**v11.5.cem**

O `pom.xml` upstream continua em `11.5-SNAPSHOT` por compatibilidade entre os módulos. A distribuição CEM sobrescreve apenas `patch.version` por `.mvn/maven.config`, fazendo o `human.version` e o `Build-Label` resultarem em `v11.5.cem`.

## Branch canônica

- `release/11.5.cem`: única branch de release/produção da distribuição CEM.

Branches antigas ficam apenas como histórico e não devem receber novos commits:

- `release/11.5-enfas` — superseded por `release/11.5.cem`;
- `release/enfas-production-2026-08` — legado de preparação;
- `feat/classificacoes-sp-uape-2026` — feature encerrada;
- `release/11.5` — linha base upstream/fork e branch padrão histórica.

## Regra de evolução

A versão base permanece `11.5`. Correções institucionais usam sufixos incrementais quando necessário:

- `v11.5.cem` — baseline de produção;
- `v11.5.cem.1` — primeiro hotfix;
- `v11.5.cem.2` — segundo hotfix.

Mudanças incompatíveis ou atualização da base SIGA devem abrir nova linha, por exemplo `release/11.6.cem`.

## Fluxo

1. Desenvolvimento e correções são preparados fora da branch canônica.
2. Somente alterações revisadas entram em `release/11.5.cem`.
3. O deploy de produção sempre aponta para `release/11.5.cem` e registra o SHA exato do commit implantado.
4. Nunca renumerar documentos já finalizados nem alterar migrations já aplicadas; novas mudanças de banco recebem uma nova migration.
5. Antes de cada produção: backup completo do banco, build limpo, teste do WAR, health-check e possibilidade de rollback.

## Identificação de build

O manifesto do WAR continua registrando `Project-Version`, `Patch-Version`, branch, commit e horário de build. Na linha CEM, o identificador humano esperado é:

```text
v11.5.cem-<commit-curto>
```

Assim a versão apresentada ao usuário permanece simples e cada WAR continua tecnicamente rastreável pelo commit que o gerou.
