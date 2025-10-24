# Estudo de Algoritmos de Hashing na Proteção de Senhas em Sistemas de Informação

Repositório técnico do Trabalho de Conclusão de Curso desenvolvido por **Gabriella Dantas** e **Pedro Siqueira Pereira Bitarães**, com o objetivo de analisar e comparar diferentes algoritmos de hashing aplicados à proteção de senhas em sistemas de informação.

## 🎯 Objetivos da Pesquisa

O projeto investiga o comportamento dos algoritmos **Argon2**, **bcrypt** e **SHA-256**, avaliando dois aspectos complementares:

1. **Medições do Servidor (Uso Legítimo)**  
   Mede o tempo e o consumo de memória para gerar/verificar senhas, simulando o funcionamento de um servidor real.

2. **Medições de Resistência (Ataque)**  
   Avalia a dificuldade de quebrar os hashes por meio de ataques de força bruta com o **John the Ripper**, analisando tempo de quebra, uso de CPU e memória.

Essas análises permitem balancear **segurança x desempenho**, mostrando o custo computacional de proteger uma senha e o esforço necessário para quebrá-la.

## ⚙️ Metodologia e Arquitetura Experimental

O ambiente foi construído em Python e PowerShell, automatizando todas as etapas do experimento.  
O script principal `run_full_benchmark.ps1` executa o ciclo completo:

1. **Geração de senhas e hashes**  
   - Arquivo `generate_hashes_full.py` cria amostras de senhas e gera hashes para Argon2, bcrypt e SHA-256.

2. **Medições de desempenho do servidor**  
   - Script `benchmark_server.py` mede o tempo médio e o uso de memória de cada algoritmo no contexto de uso legítimo.

3. **Execução de ataques práticos**  
   - O **John the Ripper** é utilizado para tentar recuperar as senhas (apenas bcrypt e SHA-256).
   - O script `monitor_john.ps1` registra CPU e memória durante o ataque.

4. **Análise e consolidação de resultados**  
   - O script `prepare_results.py` processa os dados gerados, calcula médias e percentuais e gera gráficos e arquivos `.csv`.

## 🧪 Como Executar o Projeto

### 1. Requisitos

- **Python 3.12+**
- **PowerShell 5.0+**
- **John the Ripper** instalado (ex: `C:\john\john-1.9.0-jumbo-1-win64\run\john.exe`)
- Sistema operacional Windows

### 2. Preparação do Ambiente

```bash
# Clonar o repositório
git clone https://github.com/seuusuario/hashing-comparison-tcc.git
cd hashing-comparison-tcc

# Criar e ativar o ambiente virtual
python -m venv .venv
.venv\Scripts\activate

# Instalar dependências
python -m pip install -r requirements.txt

# Executar o experimento completo
.\scripts\run_full_benchmark.ps1 -bcrypt_rounds 12
```

O processo leva alguns minutos e gera automaticamente todos os resultados em /results.

## 📊 Resultados Gerados

Após a execução, os principais arquivos produzidos são:

| Tipo de Arquivo            | Descrição                                              |
| -------------------------- | ------------------------------------------------------ |
| `server_benchmarks.csv`    | Dados de tempo e memória de cada algoritmo no servidor |
| `monitor_summary.csv`      | Consumo médio de CPU e memória durante o ataque        |
| `john_results.csv`         | Percentual de senhas quebradas por algoritmo           |
| `plot_time_per_hash.png`   | Tempo médio (s) por algoritmo                          |
| `plot_mem_mb.png`          | Uso médio de memória (MB)                              |
| `plot_percent_cracked.png` | Percentual de senhas quebradas                         |

## 👥 Autores

Gabriella Dantas  
Pedro Siqueira Pereira Bitaraes

Orientador: Prof. **Luciana Mara Freitas Diniz**  
Curso de *Sistemas de Informação* — Pontifícia Universidade Católica de Minas Gerais

## 📚 Licença e Uso Acadêmico

Este projeto é de caráter acadêmico e experimental, com fins de pesquisa e reprodutibilidade científica.
Os scripts e resultados podem ser utilizados como referência em outros estudos sobre segurança da informação e criptografia de senhas.
