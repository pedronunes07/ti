# Monitor de Alarme Arduino

Este é um aplicativo desktop desenvolvido em Python para monitorar um sistema de alarme conectado via Arduino. O aplicativo permite visualizar o status do alarme em tempo real, registrar eventos e exportar o histórico de eventos.

## Funcionalidades

- Monitoramento em tempo real do status do alarme
- Conexão serial com Arduino
- Interface gráfica com Tkinter
- Banco de dados SQLite para armazenamento de eventos
- Visualização e exportação do histórico de eventos
- Alertas visuais e sonoros quando o alarme é ativado

## Requisitos

- Python 3.x
- Bibliotecas Python:
  - tkinter
  - pyserial
  - sqlite3

## Instalação

1. Clone este repositório
2. Instale as dependências:
```bash
pip install pyserial
```
pip install -r requirements.txt 

## Uso

1. Execute o arquivo principal:
```bash
python alarm_monitor.py
```

2. Na interface do aplicativo:
   - Selecione a porta serial do Arduino
   - Clique em "Conectar"
   - O status do alarme será exibido em tempo real
   - Use o botão "Ver Banco de Dados" para visualizar o histórico de eventos
   - Os eventos podem ser filtrados por data e exportados para CSV

## Estrutura do Projeto

- `alarm_monitor.py`: Arquivo principal do aplicativo
- `alarm_history.db`: Banco de dados SQLite para armazenamento de eventos

## Contribuição

Sinta-se à vontade para contribuir com o projeto através de pull requests ou reportando issues.

## Licença

Este projeto está sob a licença MIT. 