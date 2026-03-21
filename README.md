# O REINO DE RAPHAEL

Jogo 2D de sobrevivência com IA local (Ollama), em que Raphael atua como observador divino, conselheiro e interventor ocasional.

## Como executar
```powershell
cd c:\Users\Hiro\Documents\VSCode\BitaCarnes
ollama serve
python main.py
```

## Controles atuais
1. Movimento: `W`, `A`, `S`, `D`
2. Coletar recurso: `G`
3. Escavar tesouro: `E`
4. Construir casa: `B`
5. Atacar inimigo: `SPACE`
6. Caçar animal: `C`
7. Acariciar/domesticar animal próximo: `T`
8. Descansar: `Z`
9. Conversar com Raphael: `R`
10. Pausar/retomar: `ESC`
11. Salvar rápido: `F5`
12. Salvar com novo nome: `F6`

## Mecânicas principais
1. Ciclo de tempo de 24h em 24 minutos reais.
2. Dia e noite com iluminação dinâmica.
3. Mundo expansível em todas as bordas: esquerda, direita, cima e baixo.
4. Renderização por região (viewport/câmera), estilo jogos 2D de exploração.
5. Memória completa de sessão do Raphael.

## Raphael
1. Observa continuamente as ações do jogador.
2. Pode conversar por curiosidade sem necessariamente interferir.
3. Pode interferir no mundo e no tempo (pausar tempo, avançar dias/anos, escassez, bênção etc.).
4. Concessão de poderes ocorre por conversa: para pedir poder, fale com Raphael no chat (`R`) e descreva seu pedido.

## Poderes
1. Raphael pode conceder ou recusar.
2. Poderes automáticos, como defesa divina, ativam sem tecla.
3. Poderes manuais recebem tecla livre sem conflito com comandos principais.

## Animais e fauna
1. Múltiplas espécies com personalidade básica (tímido, curioso, agressivo, calmo).
2. Comportamento de fuga/aproximação simples.
3. Domesticação por carinho (`T`) para criar pet.

## Vilas e estruturas
1. Vilas aparecem no mundo e são renderizadas como ponto de assentamento.
2. Casas construídas pelo jogador funcionam como infraestrutura local.

## Saves
1. Menu inicial com Novo Jogo, Carregar Save e Sair.
2. Nome de save digitado na interface (sem terminal).
3. Saves ilimitados em `saves/` (limite apenas do disco).

## Configuração de viewport
No `objectives.json`, em `gameplay.render`:
1. `visible_squares_x`: quantidade de colunas visíveis
2. `visible_squares_y`: quantidade de linhas visíveis

## Organização do projeto
1. `main.py`: ponto de entrada.
2. `jogo/config.py`: constantes visuais, teclas e caminhos.
3. `jogo/modelos.py`: estado do mundo, animais, tempo e memória.
4. `jogo/servicos.py`: Raphael, integração Ollama, saves e criação do mundo.
5. `jogo/ui.py`: renderização do mapa, HUD, chat e menu inicial.
6. `jogo/app.py`: loop principal e orquestração dos sistemas.

## Requisitos
1. Python 3.14+
2. `pygame-ce`
3. Ollama em execução local (`http://localhost:11434`)

## Observações
1. Toda a experiência está em PT-BR.
2. O jogo não depende de sprites externos.
3. Se o Ollama cair, o jogo continua com comportamento de fallback para manter a jogabilidade.
