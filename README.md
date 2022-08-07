<h1 align="center">Robô da Innovar</h1>
<p align="center">
    Um assistente virtual básico com escalabilidade e múltiplas funções.
</p>
<p align="center">
    <a href="https://twitter.com/jaobernard">
        <img alt="Feito por João Bernardi" src="https://img.shields.io/badge/feito%20por-%40jaobernard-1DA1F2">
    </a>
</p>

# 📑 Documentação
- ## Estruturas externas
    - ## 🧪 Menus
        ```js
        {
            "options": 
                // Aqui estarão as opções.
                "*": {
                    // Aqui estarão as opções para qualquer "carry"
                    "index": {
                        "prompt": "texto",
                        "action": "menu#nomeDoMenu@Index" 
                        /* 
                        * Pimeiro item indica a ação
                        * Segundo dá contexto
                        * Terceiro dá argumentos.
                        * 
                        * no caso de menu#nomeDoMenu@Index
                        * a ação é menu, o contexto nomeDoMenu e o argumento é Index
                        * Ou seja, chamará o menu nomeDoMenu e definirá o "carry" para Index.
                        */
                    }
                }
            "prompt": "Mensagem principal do menu\n",
            "fallbacks": {
                "action": "menu#nomeDoMenu@Index"
                // Aqui é definido o fallback para as opções que não tiverem a chave de "action"
            },
            "messages": {
                "welcome": "Olá {user.name} 👋",
                "wrong": "📛 — Esta não é uma opção válida.."
                // Aqui são definidas mensagens padrão sobre a interação do usuário
            }
        }
        ```
    - ## 📟 Cards
        ```js
        {
            "name": "Transmissão — Teste", // Define o nome do card
            "type": 1, /*
                        * Define o tipo do card
                        * 1 - Transmissão básica
                        * 1.1 - Transmissão de convite de evento
                        */
            "disabled": true,
            // Se o "disabled" estiver ativo, o card, por convenção, deverá ser ignorado.
            "data": {
                "recipients": [
                    {"name": "João Lucas Bernardi", "number": "555492022338"}
                    // Aqui são colocados os recipientes, os argumentos serão passados para lib.structures.User.no_id
                ],
                "messages": [
                    {"msg": "Texto"}
                    // Aqui os argumentos serão passados direto para o método send_message de lib.structures.User
                ]
            },
            "invoke": {
                "call": "ℹ️ — O card _’{card.name}’_ foi invocado e executará as suas tarefas."
                // Aqui é definida mensagem para quando um card é invocado.
            }
        }
        ```