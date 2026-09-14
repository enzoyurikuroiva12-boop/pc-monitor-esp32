# Sensores e limites técnicos

O agente trata qualquer leitura ausente como indisponível. `psutil` fornece CPU, RAM, discos, rede, processos e uptime em múltiplos sistemas, mas temperaturas/GPU variam muito entre fabricante, driver e permissões.

Para temperaturas completas no Windows, recomenda-se executar o LibreHardwareMonitor com a API local habilitada e adicionar um adaptador autenticado ao agente. A integração não está embutida por padrão para evitar instalar software privilegiado sem autorização. O contrato esperado é uma lista de sensores com `name`, `value`, `min`, `max`, `average`, `source`, `status` e `updated_at`.

Discord é deliberadamente limitado. O agente apenas verifica se o processo está aberto e mostra a mensagem de indisponibilidade para chamada; não captura áudio, mensagens, conversas, tokens ou conteúdo privado.

GPU NVIDIA/AMD/Intel e sensores de VRAM/hotspot/VRM dependem do provedor disponível. Nunca substitua `null` por um valor estimado no agente ou no firmware.
