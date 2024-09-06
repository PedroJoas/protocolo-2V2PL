# protocolo-2V2PL
Implementação do protocolo de controle de concorrência 2V2PL para disciplina de SGBD 2024.1

# Como configurar o ambiente do projeto

Este projeto utiliza dependências gerenciadas pelo Python e armazenadas no arquivo `requirements.txt`. Para garantir que todas as dependências corretas estejam instaladas no seu ambiente, siga as instruções abaixo:

## Pré-requisitos

- Python 3.x instalado na máquina.
- **pip** (Python package manager) instalado.

## Passos para instalar as dependências

1. **Clonar o repositório**

   Se você ainda não clonou o repositório, faça isso usando o seguinte comando:

   ```bash
   git clone https://github.com/PedroJoas/protocolo-2V2PL.git
   ```
   
   Entre no repositório:
   ```
   cd protocolo-2V2PL
   ```
  
2. **Instalar as dependências**

execute o seguinte comando para instalar todas as bibliotecas listadas no arquivo requirements.txt:

```
pip install -r requirements.txt
```

Pronto, após esses passos é só começar a codar ;)

## Enunciado

O trabalho prático representará a implementação do protocolo conservador 2V2PL, para controle de concorrência, com suporte à múltipla granulosidade de bloqueio, detecção e prevenção (bloqueio do tipo update) de deadlocks. Na implementação do protocolo, a entrada deverá ser um escalonamento (conjunto de transações e suas operações) qualquer. A saída deve mostrar a sincronização correta das operações do escalonamento fornecido. A detecção de deadlocks deverá utilizar a estratégia do grafo de espera.

## Funcionamento do protocolo 2v2PL

1. **Duas versões de cada item de dados**: No 2V2PL, cada item de dados no banco de dados pode ter duas versões: uma versão velha (ou antiga) e uma versão nova.
- A versão velha é a versão atual do dado antes de qualquer transação em execução.
- A versão nova é a versão que será criada por uma transação que está modificando o dado.

2. **Bloqueio em duas fases**:
- Expansão: Durante a fase de expansão (ou crescimento), uma transação pode adquirir bloqueios em itens de dados à medida que os acessa.
- Contratação: Após a fase de expansão, a transação entra na fase de contratação, onde libera todos os bloqueios adquiridos.

3. **Controle de leitura/escrita**:
- Leituras: Transações podem ler a versão velha ou nova do dado, dependendo da etapa em que a transação que modifica o dado se encontra. Se uma transação quer ler um dado que outra transação está escrevendo, pode optar por ler a versão velha (se a nova ainda não estiver disponível).

- Escritas: Quando uma transação escreve um dado, ela cria a versão nova e, após a transação ser confirmada (commit), a versão velha é substituída pela nova.

A principal difereça entre a 2V2PL e a 2PL é as duas versões dos dados. Entender bem a 2PL é essencial para implementação da 2V2PL.


## Múltipla granulosidade

A múltipla granularidade de bloqueio é uma técnica que permite que bloqueios sejam aplicados em diferentes níveis de granularidade, como:

- Tupla: Um registro específico em uma tabela.
- Página: Um bloco de registros em uma tabela.
- Tabela: Toda a tabela em si.
- Banco de dados: Todo o banco de dados.


Essa abordagem permite um controle mais flexível e eficiente dos bloqueios, onde transações podem bloquear apenas o nível necessário de granularidade, em vez de bloquear dados em um nível mais amplo.

Utilizar grafo de granularidade(?)


## Detecção e prevenção de deadlocks

A detecção de deadlocks deverá utilizar a estratégia do grafo de espera.Enquanto a prevenção utilizando bloqueio do tipo update.

## Ideias iniciais

Fazer um parser que gera uma lista de tuplas, onde cada tupla contém a operação, qual transação e objeto.

classes operacoes, transacoes, ...

Implementação da tabela syslockinfo.

Mostra o grafo usando plotly

utilziar um dicionario para armazenar cada acao da transacao, bloqueios, (?)