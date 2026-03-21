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
2. Mirar/direção do personagem: mouse
3. Coletar recurso na célula à frente: `G`
4. Escavar tesouro na célula à frente: `E`
5. Construir casa na célula à frente: `B`
6. Atacar inimigo na célula à frente: `SPACE`
6. Caçar animal: `C`
7. Acariciar/domesticar animal próximo: `T`
8. Descansar: `Z`
9. Ação contextual (entrar/sair de casa, igreja, biblioteca): `F`
10. Conversar com NPC próximo: `Y`
11. Conversar com Raphael: `R`
12. Pausar/retomar: `ESC`
13. Salvar rápido: `F5`
14. Salvar com novo nome: `F6`

## Mecânicas principais
1. Ciclo de tempo de 24h em 24 minutos reais.
2. Dia e noite com iluminação dinâmica.
3. Mundo expansível em todas as bordas: esquerda, direita, cima e baixo.
4. Renderização por região (viewport/câmera), com apresentação visual em estilo RPG pixel-art.
5. Memória completa de sessão do Raphael.
6. Interações físicas usam a célula imediatamente à frente do personagem, definida pela posição do mouse.
7. Jogador e NPCs recebem perfis aleatórios, com retratos/sprites montados a partir dos assets em `sprites/mana-seed-farmer/`.
8. O herói começa com idade aleatória entre 9 e 30 anos.

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
2. Casas de vila são entráveis (interior).
3. NPCs possuem papel social e memória individual de conversa.
4. Vilas evoluem com os anos (aldeia, vila, castelo, cidade, metrópole).

## Saves
1. Menu inicial em estilo RPG com Novo Jogo, Carregar Save e Sair.
2. Nome de save digitado na interface (sem terminal).
3. Na criação de novo jogo, o herói é gerado aleatoriamente e pode ser rerrolado com `R` no menu.
4. Saves ilimitados em `saves/` (limite apenas do disco).
5. Formato novo por pasta de save com múltiplos JSON (`meta.json`, `mundo.json`, `tiles.json`, `sociedade.json`, `lore_quests.json`, `memoria_raphael.json`).
6. Compatível com saves legados em arquivo único `.json`.

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
2. O jogo agora usa os pacotes visuais disponíveis em `sprites/` para retratos, UI e ambientação RPG.
3. Se o Ollama cair, o jogo continua com comportamento de fallback para manter a jogabilidade.
