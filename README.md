# 🧠 Auto-Research: Equity Financial Agent (LLM-as-a-Judge)

Este repositório contém um ecossistema de pesquisa autônoma focado na extração e estruturação de dados financeiros de empresas de capital aberto (Blue Chips e BDRs). 

O diferencial deste projeto é a sua arquitetura de desenvolvimento. O agente final não foi escrito de forma tradicional; ele foi forjado através de um loop autônomo utilizando **LLM-as-a-Judge**, garantindo resiliência, generalização (zero overfitting) e a eliminação de alucinações de dados.

---

## 🏗️ Arquitetura do Sistema

O sistema opera sob três pilares, dividindo responsabilidades entre Nuvem e Edge (Local) para otimizar custos e inteligência:

* **The Orchestrator:** Atuou como o desenvolvedor autônomo. Escreveu o código do agente iterativamente e executou testes no terminal sorteando ativos aleatórios (PETR4, VALE3, ITUB4, ROXO34) para evitar hardcoding.
* **The Evaluator (eval.py - Edge/Local):** O juiz do sistema. Utiliza o modelo Llama 3.2:3b (via Ollama local) para auditar o relatório financeiro gerado pelo agente. Ele avalia métricas estritas de Zero Alucinação, precisão factual e formatação JSON, forçando o Orquestrador a corrigir falhas de raspagem.
* **The Agent (agent.py - Cloud):** O artefato final. Um pesquisador autônomo que realiza Deep Web Scraping e utiliza a API do OpenRouter (Llama 3.1 8B) para estruturar os dados, forçando a citação exata de fontes para cada métrica extraída.

---

## 🛡️ Decisões de Engenharia & Funcionalidades

* **Zero Alucinação & Transparência:** Se um dado não está na web, o agente reporta "Data not found in sources" em vez de inventar números.
* **Extração Dinâmica (Regex):** O script não depende de inputs perfeitos. Ele extrai autonomamente o ticker (ex: VALE3) de strings complexas passadas via terminal.
* **Normalização de Câmbio (BDRs):** Inteligência embutida para identificar relatórios em USD (como os da Nubank - ROXO34) e realizar a conversão para BRL na formatação final do JSON.
* **Audit Trail (eval_history.jsonl):** O repositório inclui o log real de aprendizado do Orquestrador, demonstrando a evolução das notas de 0 (falhas críticas) até o platô de 80-85 pontos de consistência estocástica.

---

## 🚀 Como Executar

### Pré-requisitos
* Python 3.10+
* Chave de API do OpenRouter

### Instalação

1. Clone o repositório e instale as dependências:
    pip install requests duckduckgo-search python-dotenv openai

2. Crie um arquivo .env na raiz do projeto e insira sua chave:
    OPENROUTER_API_KEY="sk-or-v1-sua-chave"

### Uso

Para gerar o relatório de equity, passe o nome ou o ticker da empresa como argumento no terminal:

    python agent.py "Resultados Financeiros Petrobras (PETR4) 2024"

A saída será um objeto JSON rigorosamente estruturado contendo Receita, Lucro Líquido, Valor de Mercado e Destaques do ano, pronto para consumo por pipelines de dados ou comitês de investimento.

---

## 💡 Visão de Evolução do Produto (Roadmap)

Pensando em escalabilidade para o setor financeiro (Asset Management e Venture Capital), a arquitetura deste agente foi desenhada para suportar duas evoluções claras:

1. **RAG (Retrieval-Augmented Generation) para PDFs Oficiais:** A transição de web scraping de portais de notícias para a leitura direta de demonstrações financeiras (ITRs/DFPs) nos sites de Relações com Investidores (RI) ou CVM. Isso envolveria um banco vetorial leve (como FAISS ou ChromaDB) para fatiar PDFs e garantir precisão contábil na fonte primária.
2. **Validação Cruzada e Comitê Multi-Agente:** Em vez de um único pesquisador, o sistema seria orquestrado por personas distintas: um agente focado na coleta (The Researcher), um agente focado em estressar os balanços e cruzar fontes diferentes para o mesmo dado (The Bear), e um orquestrador final para sintetizar um Investment Memo automatizado.