# protocolo-2V2PL
Implementação do protocolo de controle de concorrência 2V2PL para disciplina de SGBD 2024.1

# Integrantes

| Nome | Matrícula |
| - | - |
| Pedro Joás Freitas Lima | 548292 |
| José Alberto Rodrigues Neto | 547872 |
| Gabriel Victor Magalhães da Silva | 539922 |


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

# Enunciado

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


## Detecção e prevenção de deadlocks

A detecção de deadlocks deverá utilizar a estratégia do grafo de espera. Enquanto a prevenção utilizando bloqueio do tipo update.

# Funcionamento

O arquivo main.py recebe como entrada um schedule no formato de string, onde as operações das transações são separadas por vírgulas. Cada operação segue o formato r1(x) ou w2(y), onde:

- r indica uma operação de leitura (read).
- w indica uma operação de escrita (write).
- O número após a operação (1, 2, etc.) identifica a transação associada.
- O valor entre parênteses (x, y, etc.) é o objeto sobre o qual a operação está sendo realizada.

## Exemplo de Entrada:

```dash
r1(x),w2(y),r1(y),w2(x)
```

Neste exemplo:

- A transação T1 lê o objeto x e depois lê o objeto y.
- A transação T2 escreve no objeto y e depois escreve no objeto x

## Funcionalidades do Script:
1. Parse do Schedule: A entrada é analisada e convertida em um formato dicionário, onde cada transação tem suas operações listadas.

- Exemplo de dicionário gerado:

```python  
{
    'T1': [('r', 'x'), ('r', 'y')],
    'T2': [('w', 'y'), ('w', 'x')]
}
```

2. Geração dos Dicionários de Bloqueios e Espera:

- O script processa o schedule e gera dois dicionários:

   - Locks: Mapeia quais transações têm bloqueios sobre quais objetos e o tipo de bloqueio (compartilhado ou exclusivo).
   - Waits: Mapeia quais transações estão esperando por outras transações devido a bloqueios.

Exemplo:

```python
locks = {
    'x': {'compartilhado': ['T1'], 'exclusivo': []},
    'y': {'compartilhado': [], 'exclusivo': ['T2']}
}
waits = {
    'T2': [('T1', 'x')],
    'T1': [('T2', 'y')]
}
```

3. Criação do Grafo de Espera:
- Com base no dicionário waits, um grafo de espera é construído, onde:

   - Cada nó representa uma transação.
   - Cada aresta representa uma dependência, ou seja, uma transação que está esperando por outra.

- Este grafo é usado para detectar **deadlocks**. Caso um 
ciclo seja identificado no grafo, isso indica a presença de um deadlock entre as transações.

4. Detecção de Deadlocks:
- O script utiliza o grafo de espera para verificar a presença de ciclos. Se um ciclo for encontrado, ele é impresso, indicando quais transações estão em deadlock.

Fluxo do Script:
- O usuário fornece o schedule.
- O script realiza o parsing da entrada.
- Os dicionários de bloqueios e espera são gerados.
- O grafo de espera é construído.
- Deadlocks são detectados e exibidos.
