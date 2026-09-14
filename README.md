# PC Monitor ESP32

Monitoramento local para **LilyGO T-Display-S3 (ESP32-S3)** com agente Windows/Linux, painel web responsivo e firmware PlatformIO.

> **Privacidade por padrão:** o agente serve dados somente na rede local e não envia telemetria para servidores externos. Sensores sem suporte do sistema/driver aparecem como `Indisponível neste computador.`

## O que já está incluído

- Agente Python com API HTTP local (`/api/metrics`), streaming SSE (`/events`) e WebSocket opcional.
- Métricas reais de CPU, RAM, discos, rede, uptime, processos/jogos e sistema via `psutil`.
- Descoberta de porta serial do ESP32 e envio JSON por USB; Wi-Fi usa HTTP/SSE local.
- Painel web responsivo em português, dark mode, histórico de 60 segundos, DEMO explícito, estados offline e WebFlasher com Web Serial.
- Firmware PlatformIO para T-Display-S3 com 9 telas, persistência de configurações, Wi-Fi, BLE de configuração e atualização sem bloqueio.
- Scripts `.bat`, modo portátil e configuração PyInstaller para o agente Windows.
- GitHub Actions que compila o `.exe` e publica artefatos Windows automaticamente.

## Início rápido

```bash
cd agent
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python pc_monitor_agent.py --demo
```

Abra `http://127.0.0.1:8765`. Para dados reais, remova `--demo`.

### Windows

Execute `installer\\install.bat` como usuário comum. Para gerar um portátil localmente:

```bat
installer\\build_portable.bat
```

O `.exe` oficial é produzido pelo workflow `build-windows.yml` em runner Windows; o ambiente Linux desta entrega não consegue executar/validar binários Windows nativamente.

### Firmware

1. Instale PlatformIO.
2. Abra `firmware/` no VS Code.
3. Ajuste SSID/senha no primeiro boot pelo portal de configuração ou no código.
4. Rode `pio run -t upload`.

O firmware aceita linhas JSON delimitadas por newline na serial. O agente envia snapshots a cada segundo.

## Sensores e Discord

CPU/RAM/discos/rede/processos são coletados sem inventar valores. Temperaturas de GPU, placa-mãe, VRM, RAM e armazenamento dependem de LibreHardwareMonitor/HWiNFO e drivers. O adaptador de sensores é opcional e documentado em `docs/sensors.md`. Discord fica limitado a presença permitida; o agente não captura áudio, mensagens ou chamadas.

## Licença

MIT. Consulte `LICENSE`.

## Dashboard de presença

A dashboard hospedada em `/presence` mostra PCs registrados pelo agente, tempo desde o início e último heartbeat. O agente envia apenas presença mínima a cada 15 segundos; use `--no-presence` para desativar. O estado online expira após 30 segundos sem heartbeat.

## Acesso protegido na Vercel

O site hospedado usa autenticação HTTP Basic no middleware da Vercel. A senha não fica no HTML, no JavaScript do navegador ou no Git; ela deve ser cadastrada como variável secreta no projeto da Vercel. Configure `SITE_USERNAME` como `pc-monitor` e `SITE_PASSWORD` como a senha escolhida (neste pedido, `210580`) nos ambientes **Production** e **Preview**. Sem `SITE_PASSWORD`, o middleware bloqueia todas as requisições.

Para publicar, importe este repositório na Vercel, mantenha o diretório raiz como `/` e faça o deploy. Em **Settings → Environment Variables**, cadastre as duas variáveis sem aspas e faça um novo deploy após salvá-las. Não inclua a senha em `.env`, commits, issues ou mensagens públicas. O arquivo `.env.example` contém apenas os nomes esperados.

A proteção cobre também os arquivos estáticos e aplica cabeçalhos de segurança. A integração local do agente continua funcionando em `http://127.0.0.1:8765`; a senha protege a cópia hospedada, não substitui a segurança da rede local.
