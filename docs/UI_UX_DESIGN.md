# PC Monitor ESP32 — UI/UX Design System

## Direção visual

A identidade usa o conceito **Instrument Panel**: uma estação de telemetria local, precisa e silenciosa. O fundo grafite profundo reduz distração; uma faixa ciano identifica dados vivos; cada domínio tem uma cor própria, mas estados críticos sempre combinam cor com texto e símbolo.

| Token | Valor | Uso |
|---|---:|---|
| Ink | `#0B0D12` | Fundo principal |
| Panel | `#141821` | Cards e superfícies |
| Line | `#252D3D` | Divisores e bordas |
| Text | `#EDF2F7` | Texto principal |
| Muted | `#8A96A8` | Apoio e metadados |
| CPU blue | `#4D9CFF` | CPU |
| GPU violet | `#AD8CFF` | GPU |
| RAM green | `#61E294` | RAM |
| Network cyan | `#4DE3F2` | Rede e conexão |
| Storage orange | `#FFB454` | Armazenamento |
| Critical red | `#FF647C` | Alertas críticos |

A tipografia usa a pilha `Inter, system-ui, sans-serif`; números usam peso 800 e leve tracking negativo para leitura à distância. O display usa tamanho grande, poucas palavras e unidades consistentes.

## Mapa de navegação

```text
Painel
├── Visão geral
├── CPU
├── GPU
├── RAM
├── Armazenamento
├── Internet
├── Jogo
├── Discord
├── Sistema
├── Configurações
├── WebFlasher
└── Diagnóstico
```

A navegação é SPA no web panel. No desktop, a barra lateral permanece disponível; no celular, a navegação torna-se uma barra inferior com os destinos mais usados.

## Primeira configuração

```text
Boas-vindas → verificar Chrome/Edge → solicitar porta USB → identificar ESP32-S3
→ confirmar apagamento → gravar firmware → verificar → configurar Wi-Fi
→ baixar/iniciar agente → teste de comunicação → painel ao vivo
```

Quando o agente não está disponível, o estado é explícito e oferece **Modo demonstração**, instruções e diagnóstico. DEMO nunca é apresentado como telemetria real.

## Wireframes

### Desktop

```text
┌──────────────┬─────────────────────────────────────────────────────┐
│ PC MONITOR   │ PC-NAME                 ● PC conectado  12:40:31   │
│ Visão geral  ├─────────────────────────────────────────────────────┤
│ CPU          │ CPU       GPU       RAM       INTERNET              │
│ GPU          │ 42%       37%       44%       120 Mb/s              │
│ RAM          ├───────────────────────┬─────────────────────────────┤
│ Internet     │ Histórico 60 segundos │ Jogo / mais quente         │
│ WebFlasher   │                         │                             │
└──────────────┴───────────────────────┴─────────────────────────────┘
```

### Mobile

```text
┌────────────────────────────┐
│ PC-NAME       ● conectado  │
│ CPU 42%   GPU 37%          │
│ RAM 44%   NET 120 Mb/s     │
│ Histórico                  │
├────────────────────────────┤
│ Visão CPU GPU RAM Web      │  ← navegação inferior
└────────────────────────────┘
```

### T-Display-S3

```text
┌────────────────────────┐
│ PC MONITOR       LIVE   │
│ RESUMO                 │
│ CPU 42%   GPU 37%      │
│ RAM 44%   NET 120M     │
│ Nenhum jogo detectado  │
│ BOOT: próxima tela     │
└────────────────────────┘
```

## Componentes reutilizáveis

`Shell`, `Sidebar`, `MobileNav`, `MetricCard`, `ProgressBar`, `StatusBadge`, `MiniChart`, `DetailPanel`, `Toast`, `Skeleton`, `OfflineState`, `FlasherStepper`, `FlasherLog`, `SettingsPanel` e `ThermalState`.

## Movimento

As entradas usam `opacity + translateY` abaixo de 300 ms; atualizações de valor e largura são transições curtas. O status conectado pulsa apenas no indicador. A troca automática usa uma barra de progresso e pausa ao interagir. `prefers-reduced-motion` desativa movimentos não essenciais. Nenhum loop usa partículas, 3D ou vídeo.

## Responsividade e acessibilidade

O desktop usa sidebar de 238 px; até 850 px ela vira navegação compacta e os cards passam para duas colunas; em telas estreitas, uma coluna. Todos os botões têm foco visível, área de toque mínima, rótulo textual/`aria-label`, estados desabilitado e erro. Estados não dependem apenas da cor: exibem `LIVE`, `DEMO`, `offline`, `indisponível` ou `crítico`. Contraste é mantido sobre o fundo Ink.

## Desempenho

O histórico do painel é limitado a 60 pontos, o agente atualiza por intervalo configurável e o firmware evita bloqueios longos. O painel usa Canvas para o gráfico, atualização sem recarregamento e CSS transforms/opacity. O firmware redesenha em baixa frequência e mantém o loop principal livre. Sensores ausentes permanecem `null`, sem polling agressivo ou valores inventados.
