# Caminho mínimo: Dijkstra (heap) × Bellman-Ford, em Python e JavaScript

Projeto de Complexidade da disciplina de Teoria da Computação. São 2 algoritmos × 2 linguagens = 4 implementações, todas executadas sobre as mesmas entradas.

## Requisitos
- Python 3.10 ou superior (testado com 3.14) e `pip install -r requirements.txt` (só para os gráficos)
- Node.js 18 ou superior (testado com v24). Não há dependências npm.

## Como reproduzir
Todos os comandos rodam dentro da pasta `src/`. No Windows use `python`; no Linux ou macOS, `python3`.

```bash
cd src
pip install -r requirements.txt
python gen_inputs.py
python test_crosscheck.py
python bench.py --reps 30
node bench.js --reps 30 --warmup 20
python bench_mem.py
node --expose-gc --min-semi-space-size=256 --max-semi-space-size=256 bench_mem.js
python env_info.py
python plot.py
```

Teste rápido: `python bench.py --max-n 1000 --reps 3` e `node bench.js --max-n 1000 --reps 3`.

Dica para medições estáveis: usar o computador na tomada, com plano de energia de alto desempenho e sem outros programas abertos. Em CPUs com núcleos de performance e de eficiência (Windows), fixar o processo em um núcleo de performance reduz o ruído:

```powershell
$p = Get-Process -Id $PID
$p.ProcessorAffinity = 0x4
$p.PriorityClass = 'High'
```

## Estrutura
| Arquivo | Função |
|---|---|
| `caminho_minimo.py` / `.js` | Dijkstra (heap) e Bellman-Ford, com parada antecipada e detecção de ciclo negativo |
| `gen_inputs.py` | Gera os grafos com semente fixa (42) e salva em `inputs/`. Python e JS leem os mesmos arquivos |
| `test_crosscheck.py` | Verifica que as 4 implementações dão o mesmo resultado nas mesmas entradas |
| `bench.py` / `bench.js` | Medição de tempo. Só o algoritmo é cronometrado; leitura e montagem do grafo ficam fora |
| `bench_mem.py` / `bench_mem.js` | Bônus: memória extra usada pelo algoritmo |
| `env_info.py` | Registra o ambiente de execução em `results/ambiente.txt` |
| `plot.py` | Gera os gráficos em `results/figs/` e a tabela `results/tabela.md` |

## Casos de entrada
Pesos inteiros em [1, 100], origem no vértice 0. A pasta `inputs/` não é versionada, porque é regenerada pela semente.

| Caso | Descrição |
|---|---|
| `random_sparse` | E = 4V, arestas em ordem aleatória (caso médio, grafo esparso) |
| `random_dense` | E = V²/20, arestas em ordem aleatória (caso médio, grafo denso) |
| `bf_best` | DAG com arestas em ordem topológica: o Bellman-Ford termina em 2 passadas |
| `bf_worst` | Cadeia com arestas em ordem reversa: o Bellman-Ford faz V−1 passadas |
| `dij_worst` | Um vértice tem a distância melhorada V−2 vezes (muitas inserções no heap) |

Tamanhos: V = 250, 500, 1000, 2000, 4000, 8000 (denso: 125 a 4000).

## Metodologia
- 30 repetições por tamanho, com média e desvio-padrão; o `min_s` também fica registrado nos CSVs.
- Warm-up: 1 rodada em Python e 20 em JavaScript (por causa do JIT).
- O coletor de lixo do Python fica desligado durante a medição.
- Corretude: `test_crosscheck.py` compara a quantidade de vértices alcançáveis e a soma das distâncias nas 4 implementações, e testa a detecção de ciclo negativo.

## Resultados
Em `src/results/`: `results_*.csv` (tempos), `results_mem_*.csv` (memória), `tabela.md`, `ambiente.txt` e `figs/` com `tempo_loglog.png`, `razao_T_sobre_f.png`, `python_vs_js.png` e `memoria.png`.

Nota sobre memória: o Node não expõe o pico de heap. Em JS, o script registra o total alocado (inclui lixo) e o valor retido após o GC, então só o Python (pico via `tracemalloc`) é usado na comparação com a complexidade de espaço.

## Convenções
- Python usa `snake_case` (`bellman_ford`); JavaScript usa `camelCase` (`bellmanFord`).
- Dijkstra usa lista de adjacência; Bellman-Ford usa lista de arestas.
- O Bellman-Ford retorna `(dist, ciclo_negativo)`. Os experimentos usam apenas pesos não negativos.